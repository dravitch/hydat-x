#!/usr/bin/env python3
"""HYDAT-X — inspect_hydat.py

Ouvre la base HYDAT SQLite en LECTURE SEULE (jamais modifiée), inventorie le
schéma (tables, colonnes, types, comptages), détecte la table de stations,
produit un rapport JSON/TXT et un inventaire des stations en Parquet (+ CSV).

Sorties :
  metadata/stations/hydat-schema.json
  metadata/stations/hydat-schema.txt
  metadata/stations/station-inventory.parquet
  metadata/stations/station-inventory.csv

Usage :
  python scripts/inspect_hydat.py [--release AAAAJJMM] [--db PATH] [--outdir PATH]
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def norm(name: str) -> str:
    """Identifiant de colonne normalisé : MAJUSCULES alphanumériques, sans artéfact."""
    return re.sub(r"[^A-Z0-9]", "", str(name).upper())


STATION_TABLE_RE = re.compile(r"(^STATION|STATIONLIST|^STND$)", re.IGNORECASE)
ID_COLS = ("STATIONNUMBER", "STATIONNO", "STATIONNUM", "STNUMBER")
NAME_COLS = ("STATIONNAME", "STNNAME", "NAME")


def find_db(release: str | None) -> Path | None:
    base = ROOT / "data" / "raw" / "hydat"
    if release:
        cands = list((base / release / "sqlite").glob("*"))
        cands += list((base / release).rglob("*.sqlite*"))
        cands += list((base / release).rglob("*.db"))
    else:
        cands = list(base.rglob("*.sqlite*")) + list(base.rglob("*.db"))
    seen = set()
    for c in sorted(cands):
        if c.is_file() and c.stat().st_size > 0 and c not in seen:
            seen.add(c)
            return c
    return None


def table_info(con: sqlite3.Connection, table: str) -> tuple[list[dict], int]:
    cols = [{"name": r[1], "type": r[2]} for r in con.execute(f"PRAGMA table_info({quote(table)})")]
    n = con.execute(f"SELECT COUNT(*) FROM {quote(table)}").fetchone()[0]
    return cols, n


def quote(ident: str) -> str:
    return f'"{ident.replace(chr(34), chr(34) * 2)}"'


def pick(station_idx: int, tables: list[str], columns: dict[str, list[dict]], rowcounts: dict[str, int]) -> int | None:
    """Sélectionne la table de stations parmi les candidates (heuristique documentée)."""
    candidates = [i for i, t in enumerate(tables) if STATION_TABLE_RE.search(t)]
    score: list[tuple[int, int]] = []
    for i in candidates:
        cols = {norm(c["name"]) for c in columns[tables[i]]}
        s = 0
        s += 3 if cols & set(ID_COLS) else 0
        s += 2 if cols & set(NAME_COLS) else 0
        s += 2 if any("LATITUD" in k for k in cols) else 0
        s += 2 if any("LONGITUD" in k for k in cols) else 0
        s += 1 if "STATIONNUMBER" in cols else 0
        s += 1 if rowcounts.get(tables[i], 0) < 50_000 else 0  # table de référentiel, pas de série
        score.append((s, i))
    if not score:
        return station_idx if station_idx < len(tables) else None
    score.sort(reverse=True)
    return score[0][1]


COLUMNS = {
    "station_id": ("STATIONNUMBER", "STATIONNO", "STATIONNUM", "STNUMBER"),
    "station_name": ("STATIONNAME", "NAME"),
    "latitude": ("LATITUDE",),
    "longitude": ("LONGITUDE",),
    "province": ("PROVTERRSTATELOCCODE", "PROVTERRSTATE", "PROVINCE", "PROVTERR"),
    "drainage_area": ("DRAINAGEAREAGROSS", "DRAINAGEAREAEFFECT", "DRAINAGEAREATOTAL", "DRAINAGEAREA"),
    "status": ("STATIONSTATUS", "STATUS", "OPERATION", "HYDROLOGICSTATUS"),
    "elevation": ("ELEVATION",),
}


def normalized_cols(columns_with_types: list[dict]) -> dict[str, str]:
    out: dict[str, str] = {}
    for c in columns_with_types:
        k = norm(c["name"])
        if k not in out:
            out[k] = c["name"]
    return out


def pick_column(cols: dict[str, str], aliases: tuple[str, ...]) -> str | None:
    for a in aliases:
        if a in cols:
            return cols[a]
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--release", default=None, help="release HYDAT (AAAAJJMM)")
    ap.add_argument("--db", default=None, help="chemin explicite vers la base SQLite")
    ap.add_argument("--outdir", default=None, help="répertoire de sortie (défaut metadata/stations)")
    args = ap.parse_args()

    outdir = Path(args.outdir) if args.outdir else ROOT / "metadata" / "stations"
    outdir.mkdir(parents=True, exist_ok=True)

    db = Path(args.db) if args.db else find_db(args.release)
    if db is None or not db.exists():
        print(f"ERREUR : base SQLite introuvable (release={args.release})", file=sys.stderr)
        return 1

    release = args.release or db.parents[1].name
    try:
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    except sqlite3.Error as e:
        print(f"ERREUR : ouverture lecture seule échouée : {e}", file=sys.stderr)
        return 1

    tables = [r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]

    columns: dict[str, list[dict]] = {}
    rowcounts: dict[str, int] = {}
    for t in tables:
        try:
            columns[t], rowcounts[t] = table_info(con, t)
        except sqlite3.Error as e:
            print(f"WARN table {t}: {e}", file=sys.stderr)
            columns[t], rowcounts[t] = [], -1

    # Détection station (heuristique documentée dans le rapport JSON)
    station_idx = 0
    station_table = None
    for i, t in enumerate(tables):
        if STATION_TABLE_RE.search(t):
            station_idx = i
            break
    chosen = pick(station_idx, tables, columns, rowcounts)
    station_table = tables[chosen] if chosen is not None else None

    report = {
        "database": str(db),
        "release": release,
        "tables": {
            t: {"columns": columns[t], "row_count": rowcounts[t]} for t in tables
        },
        "table_count": len(tables),
        "station_table_detected": station_table,
        "station_table_heuristic": "regex STATION* + score colonnes id/nom/lat/long + taille<50k",
    }

    # Inventaire stations
    inventory = None
    station_count = 0
    period = {"start": None, "end": None}
    if station_table is not None:
        cols = normalized_cols(columns[station_table])
        mapping = {k: pick_column(cols, aliases) for k, aliases in COLUMNS.items()}
        sel = ", ".join(f"{quote(c)} AS {quote(k)}" for k, c in mapping.items() if c)
        try:
            df = None
            import pandas as pd  # noqa: PLC0415
            if sel:
                df = pd.read_sql_query(f"SELECT {sel} FROM {quote(station_table)}", con)
                inventory = df
                station_count = int(len(df))
            # Période depuis la table de stations si des colonnes idoines existent
            yf = pick_column(cols, ("YEARFROM", "YEARFROMDATE", "RECORDSTART", "STARTYEAR"))
            yt = pick_column(cols, ("YEARTO", "YEAREND", "RECORDEND", "ENDYEAR"))
            if yf and yt:
                lo, hi = con.execute(f"SELECT MIN({quote(yf)}), MAX({quote(yt)}) FROM {quote(station_table)}").fetchone()
                period = {"start": lo, "end": hi}
        except Exception as e:  # noqa: BLE001
            print(f"WARN inventaire stations : {e}", file=sys.stderr)

    # Période dérivée : STN_DATA_RANGE (référentiel de couverture station/type),
    # puis table de séries (YEAR/MONTH) si la première est absente.
    if period.get("start") is None:
        if "STN_DATA_RANGE" in rowcounts:
            cols = normalized_cols(columns["STN_DATA_RANGE"])
            yf = pick_column(cols, ("YEARFROM",))
            yt = pick_column(cols, ("YEARTO",))
            if yf and yt:
                try:
                    lo, hi = con.execute(
                        f"SELECT MIN({quote(yf)}), MAX({quote(yt)}) FROM {quote('STN_DATA_RANGE')}").fetchone()
                    period = {"start": lo, "end": hi}
                except sqlite3.Error:
                    pass
    if period.get("start") is None:
        for cand in ("DLY_FLOWS", "DAILY_MEANS", "MLY_FLOWS", "MONTHLY_MEANS"):
            if cand in rowcounts and 0 < rowcounts[cand] < 30_000_000:
                cols = normalized_cols(columns[cand])
                ey = pick_column(cols, ("YEAR",))
                em = pick_column(cols, ("MONTH",))
                d = pick_column(cols, ("DATE", "OBSERVEDDATE", "DATEOBSERVATION", "DATETIME"))
                if d:
                    try:
                        lo, hi = con.execute(f"SELECT MIN({quote(d)}), MAX({quote(d)}) FROM {quote(cand)}").fetchone()
                        period = {"start": lo, "end": hi}
                    except sqlite3.Error:
                        pass
                elif ey:
                    yexpr = f"{quote(ey)}*100 + COALESCE({quote(em)},1)" if em else quote(ey)
                    try:
                        lo, hi = con.execute(f"SELECT MIN({yexpr}), MAX({yexpr}) FROM {quote(cand)}").fetchone()
                        period = {"start": lo, "end": hi}
                    except sqlite3.Error:
                        pass
                if period.get("start") is not None:
                    break

    report["station_count"] = station_count
    report["period"] = period

    jpath = outdir / "hydat-schema.json"
    jpath.write_text(json.dumps(report, indent=2, ensure_ascii=False))

    lines = ["HYDAT-X — schéma (inspection lecture seule)", f"base : {db}", f"release : {release}"]
    lines.append(f"tables : {len(tables)}")
    if station_table:
        lines.append(f"table de stations détectée : {station_table}")
    for t in tables:
        lines.append(f"- {t}  ({rowcounts[t]} lignes)")
        for c in columns[t]:
            lines.append(f"    {c['name']} : {c['type']}")
    (outdir / "hydat-schema.txt").write_text("\n".join(lines) + "\n")

    if inventory is not None:
        pinv = outdir / "station-inventory.parquet"
        civ = outdir / "station-inventory.csv"
        inventory.to_parquet(pinv, index=False)
        inventory.to_csv(civ, index=False)
    else:
        print("WARN : aucun inventaire de stations produit (table non détectée)", file=sys.stderr)

    print(f"INSPECT OK — release={release} tables={len(tables)} stations={station_count} "
          f"période={period.get('start')}→{period.get('end')} table_stations={station_table}")
    return 0


if __name__ == "__main__":
    sys.exit(main())