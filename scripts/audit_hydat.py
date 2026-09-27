#!/usr/bin/env python3
"""audit_hydat.py — HYDAT-X REFERENCE-01 : HYDAT DATA AUDIT + TARGET DESIGN.

Analyse **en lecture seule** de la base HYDAT SQLite (release 20260717).

Produit (cf. mission §5) :
  evaluation/reports/DATA-AUDIT-001/
    report.md | summary.json | tables.csv | stations.csv | coverage.csv
    missingness.csv | distributions.csv | temporal-coverage.parquet
    annual-peaks.csv | target-events.csv | seasonality.csv | events/*.csv

Interprétations HYDAT documentées (ne jamais inventer un flag — §7) :
  * DATA_SYMBOLS : 'D'=jour sec, 'E'=estimé, 'A'=partiel, 'B'=glace,
                   'S'=échantillons collectés (doc ECCC HYDAT)
  * une cellule 0.0 SANS symbole : interprétation ambiguë dans la doc HYDAT
    → jamais supposée silencieusement ; comptée séparément (n_zero_blank).
  * PEAK_CODE : 'H'=maximum, 'L'=minimum (doc ECCC HYDAT)
  * NO_DAYS   : nombre de jours avec données dans le mois (doc HYDAT)
  * FULL_MONTH: indicateur de mois complet (doc HYDAT)

Politique d'exploitation (déclarée, HUMAN DECISION REQUIRED pour la gelée) :
  * un "jour valide" = valeur > 0 OU symbole 'D' (jour sec mesuré).
    0.0 sans symbole n'est PAS compté comme observation valide.
  * seuils de target : quantiles station-spécifiques ; deux politiques
    d'information temporelle : 'whole-series' (= future-informed, marqué)
    et 'reference-first-half' (seuil sur 1re moitié du registre, événements
    évalués sur la 2de moitié uniquement) — cf. §11 mission (target leakage).

Trace : chaque chiffre est relié à une requête SQL reproduite dans report.md.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RELEASE = "20260717"
RAWDIR = ROOT / "data" / "raw" / "hydat" / RELEASE
DB = RAWDIR / "sqlite" / "Hydat.sqlite3"
OUT = ROOT / "evaluation" / "reports" / "DATA-AUDIT-001"
SCRATCH = ROOT / "logs" / "audit"
TMP = Path("/tmp/opencode/duckdb_tmp")

FLOW = [f"FLOW{i}" for i in range(1, 32)]
FLOWSYM = [f"FLOW_SYMBOL{i}" for i in range(1, 32)]
LEVEL = [f"LEVEL{i}" for i in range(1, 32)]
LEVELSYM = [f"LEVEL_SYMBOL{i}" for i in range(1, 32)]


def listexpr(cols):
    return "list_value(" + ", ".join(cols) + ")"


class Audit:
    def __init__(self, db: Path):
        self.db = db
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "events").mkdir(parents=True, exist_ok=True)
        SCRATCH.mkdir(parents=True, exist_ok=True)
        TMP.mkdir(parents=True, exist_ok=True)
        self.con = duckdb.connect(str(TMP / "audit.duckdb"))
        self.con.execute("PRAGMA memory_limit='6GB'")
        self.con.execute(f"SET temp_directory='{TMP}'")
        self.con.execute(f"ATTACH '{db}' AS h (TYPE sqlite, READ_ONLY)")
        self.md: list[str] = []
        self.sum: dict = {}
        self.total_stations = 0

    def q(self, sql):
        return self.con.execute(sql)

    def log(self, msg):
        print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

    def addmd(self, *lines):
        self.md.extend(lines)

    def put_csv(self, name, df):
        df.to_csv(OUT / name, index=False)

    # ------------------------------------------------------------------ #
    # parquet journalier (streaming — jamais tout en RAM)
    # ------------------------------------------------------------------ #
    def daily_parquet(self, table, valcols, symcols, fname) -> Path:
        p = SCRATCH / fname
        if p.exists():
            return p
        self.q(f"""
            COPY (
              SELECT * FROM (
                SELECT STATION_NUMBER AS station,
                       YEAR AS yr, MONTH AS mon,
                       UNNEST(range(1,32)) AS dom,
                       UNNEST({listexpr(valcols)}) AS "value",
                       UNNEST({listexpr(symcols)}) AS symbol,
                       TRY_CAST(printf('%04d-%02d-%02d', YEAR, MONTH,
                                       UNNEST(range(1,32))) AS DATE) AS dte,
                       NO_DAYS AS no_days, FULL_MONTH AS full_month
                FROM h."{table}"
              )
              WHERE dom <= no_days AND "value" IS NOT NULL
            ) TO '{p}' (FORMAT PARQUET)
        """)
        self.log(f"OK  {fname}")
        return p

    # ------------------------------------------------------------------ #
    # PHASE A — inventaire base
    # ------------------------------------------------------------------ #
    def inventory(self):
        self.log("PHASE A — inventaire base")
        cols = self.q(
            "SELECT table_name, column_name, data_type, ordinal_position "
            "FROM information_schema.columns WHERE table_catalog='h' "
            "ORDER BY table_name, ordinal_position"
        ).fetchall()
        tables = {}
        for t, c, ty, _ in cols:
            tables.setdefault(t, []).append((c, ty))
        rows = []
        for t in sorted(tables):
            n = self.q(f'SELECT count(*) FROM h."{t}"').fetchone()[0]
            keys = [c for c, _ in tables[t]
                    if c == "STATION_NUMBER" or c.endswith(("_ID", "_CODE", "_SYMBOL_ID"))]
            rows.append({"table": t, "rows": n, "columns": len(tables[t]),
                         "key_candidates": "; ".join(keys)})
        self.put_csv("tables.csv", pd.DataFrame(rows))
        self.sum["tables"] = {r["table"]: int(r["rows"]) for r in rows}
        self.addmd("## 1. Inventaire base",
                   f"- **{len(tables)} tables** ; lignes : "
                   f"{sum(r['rows'] for r in rows):,}.",
                   "- Détail colonnes/types/clés candidates : `tables.csv`.",
                   "- Relations : voir `docs/DATA-AUDIT-001.md` (schéma HYDAT).")
        self.log(f"OK  {len(tables)} tables")

    # ------------------------------------------------------------------ #
    # PHASE A — inventaire stations
    # ------------------------------------------------------------------ #
    def stations(self):
        self.log("PHASE A — stations")
        df = self.q("""
            SELECT STATION_NUMBER, STATION_NAME, LATITUDE, LONGITUDE,
                   DRAINAGE_AREA_GROSS, DRAINAGE_AREA_EFFECT,
                   PROV_TERR_STATE_LOC, HYD_STATUS, RHBN
            FROM h.STATIONS
        """).fetchdf()
        rng = self.q("""
            SELECT STATION_NUMBER, YEAR_FROM, YEAR_TO, RECORD_LENGTH
            FROM h.STN_DATA_RANGE WHERE DATA_TYPE='Q'
        """).fetchdf()
        m = df.merge(rng, on="STATION_NUMBER", how="left")

        def bucket(y):
            if y is None or (y != y):
                return "NA"
            if y < 1: return "<1 an"
            if y < 5: return "1-5 ans"
            if y < 10: return "5-10 ans"
            if y < 15: return "10-15 ans"
            if y < 20: return "15-20 ans"
            if y < 30: return "20-30 ans"
            return ">30 ans"
        m["record_length_bucket"] = m["RECORD_LENGTH"].map(bucket)
        m["record_length_bucket"] = pd.Categorical(
            m["record_length_bucket"],
            ["NA", "<1 an", "1-5 ans", "5-10 ans", "10-15 ans",
             "15-20 ans", "20-30 ans", ">30 ans"])
        bubb = m["record_length_bucket"].value_counts().to_dict()
        prov = m["PROV_TERR_STATE_LOC"].fillna("NA").value_counts().to_dict()
        n = len(m)
        self.total_stations = n
        n_active = int((m["HYD_STATUS"] == "A").sum())
        n_coord = int(m["LATITUDE"].notna().sum())
        n_area = int(m["DRAINAGE_AREA_GROSS"].notna().sum())
        n_rhbn = int(m["RHBN"].fillna(0).gt(0).sum())
        self.put_csv("stations.csv", m)
        self.sum["stations"] = {"total": n, "active": n_active,
                                "with_coordinates": n_coord,
                                "with_gross_area": n_area, "rhbn": n_rhbn,
                                "record_length_buckets": {k: int(v)
                                    for k, v in bubb.items()},
                                "by_province": {k: int(v)
                                    for k, v in prov.items()}}
        self.addmd("## 2. Stations",
                   f"- **{n}** stations ; actives **{n_active}** ; coordonnées "
                   f"**{n_coord}** ; superficie **{n_area}** ; RHBN **{n_rhbn}**.",
                   f"- durée d'enregistrement : "
                   f"{ {k: int(v) for k, v in bubb.items()} }.",
                   f"- par province : { {k: int(v) for k, v in prov.items()} }.")
        self.log(f"OK  stations={n}")

    # ------------------------------------------------------------------ #
    # PHASE B — couverture temporelle
    # ------------------------------------------------------------------ #
    def coverage(self):
        self.log("PHASE B — couverture temporelle")
        pf = self.daily_parquet("DLY_FLOWS", FLOW, FLOWSYM, "dly_flows.parquet")
        d = self.q(f"""
            WITH v AS (
              SELECT station, dte, value, symbol,
                     (CASE WHEN value > 0 OR symbol = 'D' THEN 1 ELSE 0 END)::INT
                       AS is_valid
              FROM read_parquet('{pf}')
              WHERE dte IS NOT NULL
            )
            SELECT station,
                   min(dte) FILTER (WHERE is_valid=1) first_observation,
                   max(dte) FILTER (WHERE is_valid=1) last_observation,
                   count(*) FILTER (WHERE is_valid=1) n_observations,
                   count(*)                       n_cells,
                   count(*) FILTER (WHERE is_valid=0 AND value=0
                                    AND symbol IS NULL)   n_zero_blank,
                   count(*) FILTER (WHERE symbol IS NOT NULL) n_symbols,
                   count(*) FILTER (WHERE is_valid=1 AND symbol='E') n_estimated
            FROM v GROUP BY station
        """).fetchdf()
        span = (d["last_observation"] - d["first_observation"]).dt.days + 1
        d["n_missing"] = span - d["n_observations"]
        d["coverage_ratio"] = d["n_observations"] / span.replace(0, np.nan)
        self.put_csv("coverage.csv", d)
        self.q(f"""
            COPY (
              SELECT station, yr,
                     count(*) FILTER (WHERE value>0 OR symbol='D') n_valid,
                     count(*) FILTER (WHERE symbol IS NOT NULL)   n_symbols,
                     count(*)                                     n_cells
              FROM read_parquet('{pf}')
              GROUP BY station, yr
            ) TO '{OUT / "temporal-coverage.parquet"}' (FORMAT PARQUET)
        """)
        n_with = int(d["n_observations"].gt(0).sum())
        self.sum["coverage"] = {
            "stations_with_flow_obs": n_with,
            "stations_with_cells_but_zero_valid_obs": int(
                ((d["n_observations"] == 0) & (d["n_cells"] > 0)).sum()),
            "median_valid_days": int(d["n_observations"].median()),
            "median_missing_days": int(d["n_missing"].median()),
            "median_coverage_ratio": round(float(d["coverage_ratio"].median()), 4),
            "total_valid_days": int(d["n_observations"].sum()),
            "total_zero_blank_days": int(d["n_zero_blank"].sum()),
            "total_estimated_days": int(d["n_estimated"].sum())}
        self.addmd("## 3. Couverture temporelle",
                   f"- stations avec ≥1 jour de débit valide : **{n_with}**.",
                   f"- stations avec cellules mais **0 observation valide** "
                   f"(tous les jours 0.0 ou symboles non-D) : "
                   f"**{self.sum['coverage']['stations_with_cells_but_zero_valid_obs']}** "
                   f"— à exclure de la population exploitable (voir DATA-AUDIT-001).",
                   f"- jours valides (total) : {int(d['n_observations'].sum()):,} ; "
                   f"médiane par station : {int(d['n_observations'].median()):,}.",
                   f"- jours 0.0 sans symbole (ambigu) : {int(d['n_zero_blank'].sum()):,} "
                   "— voir HYDAT-DATA-QUALITY.md.",
                   f"- couverture médiane (jours valides/registre) : "
                   f"{self.sum['coverage']['median_coverage_ratio']}.",
                   "- `coverage.csv` (par station) ; `temporal-coverage.parquet` "
                   "(station × année).")
        self.log(f"OK  stations avec débit={n_with}")

    # ------------------------------------------------------------------ #
    # PHASE C — qualité / missingness
    # ------------------------------------------------------------------ #
    def quality(self):
        self.log("PHASE C — qualité / missingness")
        pf = self.daily_parquet("DLY_FLOWS", FLOW, FLOWSYM, "dly_flows.parquet")
        symd = self.q(f"""
            SELECT COALESCE(symbol,'__NULL__') sym, count(*) n
            FROM read_parquet('{pf}') WHERE dte IS NOT NULL
            GROUP BY 1 ORDER BY n DESC
        """).fetchdf()
        zero_sym = self.q(f"""
            SELECT COALESCE(symbol,'__NULL__') sym, count(*) n
            FROM read_parquet('{pf}') WHERE value=0
            GROUP BY 1 ORDER BY n DESC
        """).fetchdf()
        prec = self.q("""
            SELECT CAST(PRECISION_CODE AS VARCHAR) c, count(*) n
            FROM h.ANNUAL_INSTANT_PEAKS GROUP BY 1 ORDER BY 2 DESC
        """).fetchdf()
        fm = self.q("""
            SELECT CAST(FULL_MONTH AS VARCHAR) c, count(*) n
            FROM h.DLY_FLOWS GROUP BY 1 ORDER BY 2 DESC
        """).fetchdf()
        s = symd.set_index("sym")["n"]
        z = zero_sym.set_index("sym")["n"]
        prec = prec.fillna("NULL").set_index("c")["n"]
        fm = fm.fillna("NULL").set_index("c")["n"]
        rows = []
        for k in s.index:
            rows.append({"field": "FLOW_SYMBOL", "value": k, "n": int(s[k]),
                         "of_which_zero": int(z.get(k, 0))})
        for k, v in prec.items():
            rows.append({"field": "PRECISION_CODE (pics)", "value": k, "n": int(v),
                         "of_which_zero": None})
        for k, v in fm.items():
            rows.append({"field": "FULL_MONTH (débit)", "value": k, "n": int(v),
                         "of_which_zero": None})
        self.put_csv("missingness.csv", pd.DataFrame(rows))
        self.sum["quality"] = {
            "symbols": {k: int(v) for k, v in s.items()},
            "zeros_by_symbol": {k: int(v) for k, v in z.items()},
            "precision_codes_peaks": {k: int(v) for k, v in prec.items()},
            "full_month_flow": {k: int(v) for k, v in fm.items()}}
        self.addmd("## 4. Qualité & missingness",
                   f"- symboles sur jours : "
                   f"{ {k: int(v) for k, v in s.items()} }.",
                   f"- jours à **0.0** — par symbole : "
                   f"{ {k: int(v) for k, v in z.items()} }.",
"→ 0.0 sans symbole : sémantique ambiguë dans la doc HYDAT ; "
                    "comptée séparément, jamais supposée. Symbole `' '` (espace), "
                    f"{int(s.get(' ', 0))} cellules hors vocabulaire officiel "
                    "(A/B/D/E/S), toutes valeurs non nulles (0 jour à 0.0) — "
                    "documenté HYDAT-DATA-QUALITY.md.",
                   f"- PRECISION_CODE (pics annuels) : "
                   f"{ {k: int(v) for k, v in prec.items()} } ; "
                   f"FULL_MONTH (mois débit) : "
                   f"{ {k: int(v) for k, v in fm.items()} }.")
        self.log("OK  quality")

    # ------------------------------------------------------------------ #
    # PHASE D — distributions (débit journalier valide)
    # ------------------------------------------------------------------ #
    def distributions(self):
        self.log("PHASE D — distributions")
        pf = self.daily_parquet("DLY_FLOWS", FLOW, FLOWSYM, "dly_flows.parquet")
        STATS = ("count(*) n, count(*) FILTER (WHERE symbol='E') n_est, "
                 "min(value) mn, quantile_cont(value,0.01) p01, "
                 "quantile_cont(value,0.05) p05, median(value) med, "
                 "quantile_cont(value,0.95) p95, quantile_cont(value,0.99) p99, "
                 "quantile_cont(value,0.999) p999, max(value) mx")
        d = self.q(f"""
            SELECT station, {STATS}
            FROM read_parquet('{pf}')
            WHERE dte IS NOT NULL AND (value > 0 OR symbol='D')
            GROUP BY station
        """).fetchdf()
        self.put_csv("distributions.csv", d)
        agg = d.drop(columns=["station"]).agg(["count", "min", "max", "median"])
        g = agg.iloc[1:]
        self.sum["flow_daily"] = {
            "stations": int(d["n"].count()),
            "total_valid_days": int(d["n"].sum()),
            "p01": round(float(d["p01"].median()), 2),
            "p05": round(float(d["p05"].median()), 2),
            "median_of_station_med": round(float(d["med"].median()), 2),
            "p95": round(float(d["p95"].median()), 2),
            "p99": round(float(d["p99"].median()), 2),
            "p999": round(float(d["p999"].median()), 2),
            "max": round(float(d["mx"].max()), 2),
            "estimated_days": int(d["n_est"].sum())}
        self.addmd("## 5. Distributions (débit journalier, m³/s)",
                   "- par station : `distributions.csv` (count/min/p01/p05/median/"
                   "p95/p99/p999/max + n_est).",
                   "- distributions fortement asymétriques → quantiles robustes "
                   "utilisés (voir summary.json).",
                   "- jours estimés (symbole E) retenus : comptés dans n_est, "
                   "inclus dans les quantiles (documenté HYDAT-DATA-QUALITY.md).")
        self.log("OK  distributions")

    # ------------------------------------------------------------------ #
    # PHASE D — extrêmes annuels (pics)
    # ------------------------------------------------------------------ #
    def extremes(self):
        self.log("PHASE D — pics annuels")
        aip = self.q("""
            SELECT STATION_NUMBER, YEAR, PEAK, MONTH, DAY, HOUR, MINUTE,
                   TIME_ZONE, PEAK_CODE, PRECISION_CODE, SYMBOL
            FROM h.ANNUAL_INSTANT_PEAKS WHERE DATA_TYPE='Q'
            ORDER BY STATION_NUMBER, YEAR
        """).fetchdf()
        n_h = int((aip["PEAK_CODE"] == "H").sum())
        n_l = int((aip["PEAK_CODE"] == "L").sum())
        perY = aip[aip["PEAK_CODE"] == "H"].groupby("YEAR").size()
        self.put_csv("annual-peaks.csv", aip)
        self.sum["annual_peaks"] = {
            "n_peaks_H": n_h, "n_peaks_L": n_l,
            "stations_with_peaks": int(aip["STATION_NUMBER"].nunique()),
            "period": [int(aip["YEAR"].min()), int(aip["YEAR"].max())],
            "peaks_per_year_min": int(perY.min()), "peaks_per_year_max": int(perY.max()),
            "peaks_per_year_median": int(perY.median())}
        self.addmd("## 6. Extrêmes annuels (pics)",
                   f"- pics de type H (max) : **{n_h:,}** ; type L (min) : {n_l:,} ; "
                   f"stations concernées : {aip['STATION_NUMBER'].nunique()}.",
                   f"- pics H/année : min {perY.min()}, médiane {perY.median()}, "
                   f"max {perY.max()} (période {aip['YEAR'].min()}–{aip['YEAR'].max()}).",
                   "- relation pics vs série journalière : voir DATA-AUDIT-001.md "
                   "(comparaison partielle station vs flux annuel max).")
        self.log("OK  pics")

    # ------------------------------------------------------------------ #
    # THRESHOLDS par station selon politique d'information temporelle
    # ------------------------------------------------------------------ #
    def station_thresholds(self, qfrac, policy):
        pf = self.daily_parquet("DLY_FLOWS", FLOW, FLOWSYM, "dly_flows.parquet")
        if policy == "whole-series":
            agg = "quantile_cont(value, %g)" % qfrac
            cut = "NULL::DATE"
        else:
            agg = ("quantile_cont(value, %g) FILTER (WHERE dte<=c.mid)" % qfrac)
            cut = "c.mid"
        self.q(f"""
            DROP TABLE IF EXISTS _thr;
            CREATE TABLE _thr AS
            WITH d AS (
              SELECT station, dte, value
              FROM read_parquet('{pf}')
              WHERE (value>0 OR symbol='D') AND dte IS NOT NULL
            ),
            c AS (
              SELECT station, min(dte) mn, max(dte) mx,
                     (min(dte) + CAST(date_diff('day', min(dte), max(dte))/2 AS INT)
                      * INTERVAL 1 DAY) AS mid
              FROM d GROUP BY station
            )
            SELECT t.station, t.q, {cut} cut_date
            FROM (
              SELECT station, {agg} q
              FROM d JOIN c USING (station) GROUP BY station
            ) t JOIN c USING (station)
        """)

    # ------------------------------------------------------------------ #
    # événements : séries de jours consécutifs > seuil
    # ------------------------------------------------------------------ #
    def events_runs(self, qfrac, policy, min_dur=1):
        pf = self.daily_parquet("DLY_FLOWS", FLOW, FLOWSYM, "dly_flows.parquet")
        self.station_thresholds(qfrac, policy)
        self.log(f"    events q={qfrac} policy={policy} min_dur={min_dur}")
        self.q(f"""
            DROP TABLE IF EXISTS _ev;
            CREATE TABLE _ev AS
            WITH d AS (
              SELECT station, dte, value
              FROM read_parquet('{pf}')
              WHERE (value>0 OR symbol='D') AND dte IS NOT NULL
            ),
            e AS (
              SELECT d.station, d.dte, (d.value > t.q)::INT ex
              FROM d JOIN _thr t USING (station)
              WHERE t.cut_date IS NULL OR d.dte >= t.cut_date
            ),
            r AS (
              SELECT station, dte, ex,
                     sum(ex=0) OVER (PARTITION BY station ORDER BY dte) grp
              FROM e
            ),
            ev AS (
              SELECT station, grp, count(*) dur, min(dte) start_dte, max(dte) end_dte
              FROM r WHERE ex=1 GROUP BY station, grp
            )
            SELECT station, dur, start_dte, end_dte FROM ev
            WHERE dur >= {min_dur}
        """)
        ev = self.q("SELECT * FROM _ev").fetchdf()
        return ev

    def peaks_events(self, qfrac):
        aip = self.q("""
            SELECT STATION_NUMBER station, YEAR, MONTH, DAY, PEAK, PEAK_CODE
            FROM h.ANNUAL_INSTANT_PEAKS WHERE DATA_TYPE='Q'
        """).fetchdf()
        aip = aip[aip["PEAK_CODE"] == "H"]
        thr = aip.groupby("station")["PEAK"].quantile(qfrac)
        out = aip.merge(thr.rename("q"), left_on="station", right_index=True)
        out = out[out["PEAK"] > out["q"]].copy()
        out["start_dte"] = pd.to_datetime(
            out["YEAR"].astype(str) + "-"
            + out["MONTH"].fillna(1).astype(int).astype(str).str.zfill(2) + "-"
            + out["DAY"].fillna(1).astype(int).astype(str).str.zfill(2))
        out["dur"] = 1
        out["end_dte"] = out["start_dte"]
        return out

    # ------------------------------------------------------------------ #
    # résumé §10 (comparaison des targets)
    # ------------------------------------------------------------------ #
    def summarize_events(self, ev, target, info_time):
        if len(ev) == 0:
            return {"target": target, "N_events": 0, "event_rate_per_station": 0,
                    "events_per_station": 0, "stations_with_events": 0,
                    "stations_zero_events": self.total_stations,
                    "median_duration_d": 0, "max_duration_d": 0,
                    "events_by_province": {}, "events_by_year": {},
                    "events_by_month": {}, "events_by_season": {},
                    "threshold_information_time": info_time}
        prov = self.q("SELECT STATION_NUMBER, PROV_TERR_STATE_LOC FROM h.STATIONS"
                      ).fetchdf().rename(columns={"STATION_NUMBER": "station",
                                                  "PROV_TERR_STATE_LOC": "province"})
        ev = ev.merge(prov, on="station", how="left")
        ev["year"] = ev["start_dte"].dt.year
        ev["month"] = ev["start_dte"].dt.month
        ev["season"] = ev["month"].map(lambda m:
            "DJF" if m in (12, 1, 2) else "MAM" if m in (3, 4, 5)
            else "JJA" if m in (6, 7, 8) else "SON")
        return {
            "target": target,
            "N_events": int(len(ev)),
            "event_rate_per_station": round(len(ev) / self.total_stations, 4),
            "events_per_station": round(len(ev) / ev["station"].nunique(), 3),
            "stations_with_events": int(ev["station"].nunique()),
            "stations_zero_events": int(self.total_stations - ev["station"].nunique()),
            "median_duration_d": int(ev["dur"].median()),
            "max_duration_d": int(ev["dur"].max()),
            "events_by_province": ev.groupby("province").size().to_dict(),
            "events_by_year": ev.groupby("year").size().to_dict(),
            "events_by_month": ev.groupby("month").size().to_dict(),
            "events_by_season": ev.groupby("season").size().to_dict(),
            "threshold_information_time": info_time}

    # ------------------------------------------------------------------ #
    # PHASE E — exploration des targets (T1, T3, T4) — §9-11
    # ------------------------------------------------------------------ #
    def targets(self):
        self.log("PHASE E — targets")
        R = []

        # T1 — quantile station-spécifique, variantes whole (future-informed)
        for qf in (0.95, 0.99, 0.995, 0.999):
            lab = "T1-q%s-whole" % str(qf).replace(".", "")
            ev = self.events_runs(qf, "whole-series")
            ev.to_csv(OUT / "events" / f"{lab}.csv", index=False)
            R.append(self.summarize_events(ev, lab, "future-informed"))
        # T1-ref — seuil sur 1re moitié, éval sur 2de (historical/reference)
        for qf in (0.95, 0.99):
            lab = "T1-q%s-refhalf" % str(qf).replace(".", "")
            ev = self.events_runs(qf, "reference-first-half")
            ev.to_csv(OUT / "events" / f"{lab}.csv", index=False)
            R.append(self.summarize_events(ev, lab, "historical/reference"))

        # T3 — pics annuels au-dessus du quantile station des pics (future-informed)
        for qf in (0.8, 0.9, 0.95):
            lab = "T3-peak-q%s-whole" % str(qf).replace(".", "")
            ev = self.peaks_events(qf)
            keep = ["station", "dur", "start_dte", "end_dte"]
            ev[keep].to_csv(OUT / "events" / f"{lab}.csv", index=False)
            R.append(self.summarize_events(ev[keep], lab, "future-informed"))

        # T4 — persistance : dépassement sur ≥ N jours consécutifs
        for qf, N in ((0.95, 3), (0.95, 5), (0.99, 3), (0.99, 5), (0.99, 10)):
            lab = "T4-q%s-N%d-whole" % (str(qf).replace(".", ""), N)
            ev = self.events_runs(qf, "whole-series", min_dur=N)
            ev.to_csv(OUT / "events" / f"{lab}.csv", index=False)
            R.append(self.summarize_events(ev, lab, "future-informed"))

        cols = ["target", "N_events", "event_rate_per_station", "events_per_station",
                "stations_with_events", "stations_zero_events", "median_duration_d",
                "max_duration_d", "events_by_province", "events_by_year",
                "events_by_month", "events_by_season", "threshold_information_time"]
        res = pd.DataFrame(R)[cols]
        self.put_csv("target-events.csv", res)
        self.sum["targets"] = res.to_dict(orient="records")
        self.addmd("## 7. Exploration des targets — comparaison quantitative",
                   "- T1 (quantiles) , T3 (pics) , T4 (persistance N jours) : "
                   "voir `target-events.csv` et `events/*.csv`.",
                   "- T2 (seuil absolu) : **aucun seuil officiel dans HYDAT** "
                   "→ HUMAN DECISION REQUIRED (documenté TARGET-DESIGN-001.md).",
                   "- Variantes 'whole' = future-informed (marquées) ; 'refhalf' = "
                   "seuil sur 1re moitié (historical/reference) — §11 leakage.")
        self.log("OK  targets")

    # ------------------------------------------------------------------ #
    # PHASE F — saisonnalité (target de référence T1-q99-whole)
    # ------------------------------------------------------------------ #
    def seasonality(self):
        self.log("PHASE F — saisonnalité")
        pf = self.daily_parquet("DLY_FLOWS", FLOW, FLOWSYM, "dly_flows.parquet")
        # P(événement | jour) par mois = jours-évt / jours-station valides du mois
        self.station_thresholds(0.99, "whole-series")
        se = self.q(f"""
            WITH d AS (
              SELECT station, mon, dte, value
              FROM read_parquet('{pf}')
              WHERE dte IS NOT NULL
                AND (CASE WHEN value > 0 OR symbol = 'D' THEN 1 ELSE 0 END) = 1
            ),
            e AS (
              SELECT d.station, d.mon, (d.value > t.q)::INT ex
              FROM d JOIN _thr t USING (station)
            )
            SELECT mon, count(*) FILTER (WHERE ex=1) n_event_days,
                   count(*) n_valid_days,
                   count(*) FILTER (WHERE ex=1)::DOUBLE / count(*) p_event
            FROM e GROUP BY mon ORDER BY mon
        """).fetchdf()
        se = se.set_index("mon").reindex(range(1, 13)).fillna(0)
        se.to_csv(OUT / "seasonality.csv")
        self.sum["seasonality"] = {
            int(k): {"n_event_days": int(v["n_event_days"]),
                     "n_valid_days": int(v["n_valid_days"]),
                     "P_event_day": round(float(v["p_event"]), 6)}
            for k, v in se.iterrows()}
        self.addmd("## 8. Saisonnalité (target T1-q099-whole)",
                   "P(événement | jour) par mois : "
                   + ", ".join(f"m{k}: {v['P_event_day']}"
                               for k, v in self.sum["seasonality"].items()),
                   "Définition P = jours-évt / jours-station valides (mois). "
                   "cf. phase F mission — baseline descriptive, pas de ML.")
        self.log("OK  seasonality")

    # ------------------------------------------------------------------ #
    def finalize(self):
        head = ("# DATA-AUDIT-001 — rapport d'audit (auto-généré)\n\n"
                f"- release : **{RELEASE}** ; fichier : `{DB.name}`\n"
                "- exécuté en lecture seule (ATTACH READ_ONLY)\n"
                f"- horodatage : {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n"
                "- chiffres traçables aux requêtes SQL du script\n---")
        self.md.insert(0, head)
        self.md.append("---\n## Queries\n"
                       "Les requêtes SQL (une par section) sont intégrées dans "
                       "`scripts/audit_hydat.py`, reproduites dans "
                       "`docs/DATA-AUDIT-001.md`.")
        (OUT / "report.md").write_text("\n\n".join(self.md) + "\n")
        (OUT / "summary.json").write_text(
            json.dumps(self.sum, indent=2, ensure_ascii=False, default=str))
        self.log("OK  report.md + summary.json")

    def close(self):
        self.con.close()


def verify(db):
    man = RAWDIR / "MANIFEST.sha256"
    if not man.exists():
        return "?? pas de MANIFEST.sha256"
    exp = None
    for line in man.read_text().splitlines():
        h, _, name = line.partition("  ")
        if name.strip() == db.name:
            exp = h
            break
    if not exp:
        return "?? base absente du manifeste"
    h = hashlib.sha256()
    with db.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return "OK" if h.hexdigest() == exp else "MISMATCH"


def main():
    ap = argparse.ArgumentParser(description="HYDAT-X data audit (lecture seule)")
    ap.add_argument("--db", type=Path, default=DB)
    ap.add_argument("--skip-hash", action="store_true")
    a = ap.parse_args()
    if not a.db.exists():
        print(f"ERREUR : base absente {a.db}", file=sys.stderr)
        return 2
    print("sha256 (vs MANIFEST.sha256) :", verify(a.db))
    au = Audit(a.db)
    t0 = time.time()
    try:
        au.inventory()
        au.stations()
        au.coverage()
        au.quality()
        au.distributions()
        au.extremes()
        au.targets()
        au.seasonality()
        au.finalize()
    finally:
        au.close()
    print(f"terminé en {time.time()-t0:.0f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())