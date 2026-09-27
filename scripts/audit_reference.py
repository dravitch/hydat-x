#!/usr/bin/env python3
"""Reconstruit la référence HYDAT-X M02 et produit DATA-AUDIT-002."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from cache_manager import cache_identity, ensure_cache, sha256_file, write_json_atomic  # noqa:E402
from segmentation import runs, violations  # noqa:E402

RELEASE = "20260717"
DEFAULT_DB = ROOT / "data/raw/hydat" / RELEASE / "sqlite/Hydat.sqlite3"
DEFAULT_OUT = ROOT / "evaluation/reports/DATA-AUDIT-002"
DEFAULT_CACHE = ROOT / "data/canonical/hydat" / RELEASE / "daily-flows-v2.parquet"
DEFAULT_CACHE_MANIFEST = ROOT / "registry/datasets/hydat-daily-flows-v2-cache.json"
TRAIN_END = "2010-12-31"
EVAL_START = "2011-01-01"
EVAL_END = "2025-12-31"
EVALUATION_SPLITS = {
    "VALIDATION": ("2011-01-01", "2015-12-31"),
    "TEST": ("2016-01-01", "2020-12-31"),
    "HOLDOUT": ("2021-01-01", "2025-12-31"),
}
FLOW = [f"FLOW{i}" for i in range(1, 32)]
SYMBOL = [f"FLOW_SYMBOL{i}" for i in range(1, 32)]


def _list_expr(items: list[str]) -> str:
    return "list_value(" + ", ".join(items) + ")"


def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def assert_no_future_threshold(frame: pd.DataFrame, reference_end: str,
                               evaluation_start: str | int) -> None:
    """Refuse une table de seuils dont la référence atteint l'évaluation."""
    if isinstance(evaluation_start, int):
        leaking = pd.to_numeric(frame[reference_end]) >= evaluation_start
    else:
        leaking = pd.to_datetime(frame[reference_end]) >= pd.Timestamp(evaluation_start)
    if leaking.any():
        raise ValueError(
            f"threshold leakage: {int(leaking.sum())} reference rows reach evaluation")


def _threshold_summary(frame: pd.DataFrame, column: str) -> dict:
    values = pd.to_numeric(frame[column]).dropna()
    return {
        "stations_with_threshold": int(frame.station.nunique()),
        "minimum": float(values.min()),
        "median": float(values.median()),
        "maximum": float(values.max()),
    }


def _daily_builder(db: Path):
    def build(destination: Path) -> None:
        con = duckdb.connect()
        con.execute(f"ATTACH '{db}' AS hydat (TYPE sqlite, READ_ONLY)")
        con.execute(f"""
            COPY (
              SELECT station, dte, "value", symbol, yr, mon, dom, no_days, full_month
              FROM (
                SELECT STATION_NUMBER station, YEAR yr, MONTH mon,
                       UNNEST(range(1, 32)) dom,
                       UNNEST({_list_expr(FLOW)}) AS "value",
                       UNNEST({_list_expr(SYMBOL)}) symbol,
                       TRY_CAST(printf('%04d-%02d-%02d', YEAR, MONTH,
                                UNNEST(range(1, 32))) AS DATE) dte,
                       NO_DAYS no_days, FULL_MONTH full_month
                FROM hydat.DLY_FLOWS
              )
              WHERE dom <= no_days AND "value" IS NOT NULL AND dte IS NOT NULL
            ) TO '{destination}' (FORMAT PARQUET, COMPRESSION ZSTD)
        """)
        con.close()
    return build


def threshold_relation(con: duckdb.DuckDBPyConnection, daily: Path, q: float,
                       name: str) -> str:
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE {name} AS
        SELECT station, quantile_cont(value, {q}) q,
               DATE '{EVAL_START}' cut_date,
               min(dte) reference_start, max(dte) reference_end,
               count(*) reference_observations
        FROM read_parquet('{daily}')
        WHERE dte <= DATE '{TRAIN_END}' AND (value > 0 OR symbol='D')
        GROUP BY station
    """)
    return name


def make_run_target(con: duckdb.DuckDBPyConnection, daily: Path, q: float,
                    minimum: int, target_id: str, out: Path) -> tuple[pd.DataFrame, dict]:
    table = "thr_" + target_id.replace("-", "_")
    threshold_relation(con, daily, q, table)
    partitions = []
    for split, (start, end) in EVALUATION_SPLITS.items():
        obs = (f"(SELECT station,dte,value,symbol FROM read_parquet('{daily}') "
               f"WHERE dte BETWEEN DATE '{start}' AND DATE '{end}')")
        partition = runs(con, obs_rel=obs, thr_rel=table, min_dur=minimum)
        partition["split"] = split
        partitions.append(partition)
    frame = pd.concat(partitions, ignore_index=True).sort_values(
        ["station", "start_dte"], ignore_index=True)
    frame.insert(0, "event_id", [f"{target_id}-{i:07d}" for i in range(1, len(frame)+1)])
    frame.insert(1, "target_id", target_id)
    frame["span"] = (pd.to_datetime(frame.end_dte) - pd.to_datetime(frame.start_dte)).dt.days + 1
    target_path = out / "events" / f"{target_id}.csv"
    _write_csv(frame, target_path)
    thresholds = con.execute(f"SELECT * FROM {table} ORDER BY station").fetchdf()
    assert_no_future_threshold(thresholds, "reference_end", EVAL_START)
    threshold_path = out / "targets" / f"{target_id}-thresholds.csv"
    _write_csv(thresholds, threshold_path)
    bad = violations(frame)
    summary = {
        "target_id": target_id,
        "role": "PRIMARY" if target_id == "T1-q095-refhalf" else (
            "RARE-STRESS" if target_id == "T1-q099-refhalf" else "PERSISTENCE-CHALLENGE"),
        "definition": f"value > station TRAIN q{q:g}; calendar-contiguous run within one temporal split; min_duration={minimum}",
        "threshold_quantile": q,
        "threshold_distribution": _threshold_summary(thresholds, "q"),
        "threshold_period": [None, TRAIN_END],
        "application_period": [EVAL_START, EVAL_END],
        "events": int(len(frame)),
        "stations": int(frame.station.nunique()) if len(frame) else 0,
        "events_per_station": float(len(frame) / frame.station.nunique()) if len(frame) else 0.0,
        "median_duration_days": float(frame.dur.median()) if len(frame) else None,
        "max_duration_days": int(frame.dur.max()) if len(frame) else None,
        "span_duration_violations": int(len(bad)),
        "leakage_risk": "controlled: threshold reference_end <= 2010-12-31; application >= 2011-01-01",
        "artifact": str(target_path.relative_to(ROOT)),
        "artifact_sha256": sha256_file(target_path),
        "threshold_artifact": str(threshold_path.relative_to(ROOT)),
        "threshold_artifact_sha256": sha256_file(threshold_path),
    }
    return frame, summary


def make_peak_target(con: duckdb.DuckDBPyConnection, target_id: str,
                     out: Path) -> tuple[pd.DataFrame, dict]:
    con.execute("""
        CREATE OR REPLACE TEMP TABLE peak_thresholds AS
        SELECT STATION_NUMBER station, quantile_cont(PEAK, 0.9) threshold,
               min(YEAR) reference_start_year, max(YEAR) reference_end_year,
               count(*) reference_observations, 2011 evaluation_start_year
        FROM hydat.ANNUAL_INSTANT_PEAKS
        WHERE DATA_TYPE='Q' AND PEAK_CODE='H' AND PEAK IS NOT NULL AND YEAR <= 2010
        GROUP BY STATION_NUMBER
    """)
    frame = con.execute(f"""
        WITH evaluated AS (
          SELECT p.STATION_NUMBER station, p.YEAR event_year,
                 p.MONTH event_month, p.DAY event_day,
                 p.PEAK peak, p.SYMBOL symbol, r.threshold,
                 r.reference_start_year, r.reference_end_year,
                 r.reference_observations
          FROM hydat.ANNUAL_INSTANT_PEAKS p JOIN peak_thresholds r
            ON p.STATION_NUMBER=r.station
          WHERE p.DATA_TYPE='Q' AND p.PEAK_CODE='H' AND p.PEAK IS NOT NULL
            AND p.YEAR BETWEEN 2011 AND 2025 AND p.PEAK > r.threshold
        )
        SELECT * FROM evaluated ORDER BY station, event_year
    """).fetchdf()
    frame.insert(0, "event_id", [f"{target_id}-{i:07d}" for i in range(1, len(frame)+1)])
    frame.insert(1, "target_id", target_id)
    frame["split"] = pd.cut(frame.event_year, bins=[2010, 2015, 2020, 2025],
                            labels=["VALIDATION", "TEST", "HOLDOUT"])
    target_path = out / "events" / f"{target_id}.csv"
    _write_csv(frame, target_path)
    thresholds = con.execute("SELECT * FROM peak_thresholds ORDER BY station").fetchdf()
    assert_no_future_threshold(thresholds, "reference_end_year", 2011)
    threshold_path = out / "targets" / f"{target_id}-thresholds.csv"
    _write_csv(thresholds, threshold_path)
    summary = {
        "target_id": target_id, "role": "EXTREME-CHALLENGE",
        "definition": "annual instantaneous high peak > station q0.9 estimated on TRAIN",
        "threshold_quantile": 0.9, "threshold_period": [None, TRAIN_END],
        "threshold_distribution": _threshold_summary(thresholds, "threshold"),
        "application_period": [EVAL_START, EVAL_END], "events": int(len(frame)),
        "stations": int(frame.station.nunique()),
        "events_per_station": float(len(frame) / frame.station.nunique()) if len(frame) else 0.0,
        "median_duration_days": 1.0 if len(frame) else None,
        "max_duration_days": 1 if len(frame) else None,
        "span_duration_violations": 0,
        "leakage_risk": "controlled: annual-peak threshold uses years <=2010 only",
        "artifact": str(target_path.relative_to(ROOT)),
        "artifact_sha256": sha256_file(target_path),
        "threshold_artifact": str(threshold_path.relative_to(ROOT)),
        "threshold_artifact_sha256": sha256_file(threshold_path),
    }
    return frame, summary


def make_coverage(con: duckdb.DuckDBPyConnection, daily: Path, out: Path) -> pd.DataFrame:
    frame = con.execute(f"""
        WITH valid AS (
          SELECT station, yr, count(*) FILTER (WHERE value>0 OR symbol='D') observed_days,
                 count(*) n_cells,
                 count(*) FILTER (WHERE value=0 AND symbol IS NULL) n_zero_blank,
                 count(*) FILTER (WHERE symbol='E') n_estimated
          FROM read_parquet('{daily}') WHERE yr <= 2025 GROUP BY station,yr
        ), sched AS (
          SELECT STATION_NUMBER station, YEAR yr, MONTH_FROM, MONTH_TO
          FROM hydat.STN_OPERATION_SCHEDULE WHERE DATA_TYPE='Q'
        )
        SELECT v.*, s.MONTH_FROM month_from, s.MONTH_TO month_to,
               CASE WHEN s.MONTH_FROM IS NOT NULL AND s.MONTH_TO IS NOT NULL
                          AND NOT (s.MONTH_FROM='JAN' AND s.MONTH_TO='DEC')
                    THEN 'seasonal' ELSE 'continuous' END operation_class,
               CASE WHEN operation_class='seasonal' THEN 217
                    WHEN yr%400=0 OR (yr%4=0 AND yr%100<>0) THEN 366 ELSE 365 END expected_days,
               CASE WHEN operation_class='seasonal' THEN 174
                    WHEN yr%400=0 OR (yr%4=0 AND yr%100<>0) THEN 293 ELSE 292 END threshold_days_80pct,
               observed_days >= threshold_days_80pct meets_80pct,
               least(observed_days, expected_days) coverage_observed_days,
               greatest(observed_days - expected_days, 0) observed_days_above_denominator,
               least(observed_days, expected_days)::DOUBLE / expected_days coverage_ratio
        FROM valid v LEFT JOIN sched s USING(station,yr)
        ORDER BY station,yr
    """).fetchdf()
    _write_csv(frame, out / "coverage/station-year-coverage.csv")
    return frame


def make_splits(con: duckdb.DuckDBPyConnection, daily: Path, out: Path) -> dict:
    temporal_dir = ROOT / "benchmark/splits/temporal"
    geographic_dir = ROOT / "benchmark/splits/geographic"
    temporal_dir.mkdir(parents=True, exist_ok=True)
    geographic_dir.mkdir(parents=True, exist_ok=True)
    temporal = con.execute(f"""
        SELECT station,
          CASE WHEN dte<=DATE '2010-12-31' THEN 'TRAIN'
               WHEN dte<=DATE '2015-12-31' THEN 'VALIDATION'
               WHEN dte<=DATE '2020-12-31' THEN 'TEST'
               WHEN dte<=DATE '2025-12-31' THEN 'HOLDOUT' END split,
          min(dte) first_date, max(dte) last_date,
          count(*) FILTER (WHERE value>0 OR symbol='D') valid_observations
        FROM read_parquet('{daily}') WHERE dte<=DATE '2025-12-31'
        GROUP BY station,split HAVING split IS NOT NULL AND valid_observations>0
        ORDER BY station,split
    """).fetchdf()
    temporal_path = temporal_dir / "station-periods.csv"
    _write_csv(temporal, temporal_path)
    population = con.execute(f"""
        WITH eligible AS (
          SELECT station FROM read_parquet('{daily}')
          GROUP BY station
          HAVING count(*) FILTER (WHERE dte<=DATE '{TRAIN_END}' AND (value>0 OR symbol='D'))>0
             AND count(*) FILTER (WHERE dte BETWEEN DATE '{EVAL_START}' AND DATE '{EVAL_END}'
                                  AND (value>0 OR symbol='D'))>0
        )
        SELECT e.station, coalesce(s.PROV_TERR_STATE_LOC, 'UNKNOWN') geographic_region,
               s.LATITUDE latitude, s.LONGITUDE longitude
        FROM eligible e LEFT JOIN hydat.STATIONS s ON e.station=s.STATION_NUMBER
        ORDER BY e.station
    """).fetchdf()
    population["region_bucket"] = population.geographic_region.map(
        lambda region: int(_hash_text(region)[:8], 16) % 8)
    population["split"] = population.region_bucket.map(
        lambda bucket: "GEO-TEST" if bucket == 7 else "GEO-TRAIN")
    geographic_path = geographic_dir / "stations.csv"
    _write_csv(population, geographic_path)
    temporal_manifest = {
        "split_id": "TRACK-TEMPORAL-v1", "status": "reference-not-frozen",
        "population": "all stations with >=1 valid observation in the represented period",
        "rules": {"TRAIN": [None, TRAIN_END], "VALIDATION": ["2011-01-01", "2015-12-31"],
                  "TEST": ["2016-01-01", "2020-12-31"],
                  "HOLDOUT": ["2021-01-01", EVAL_END]},
        "station_period_rows": len(temporal), "stations": int(temporal.station.nunique()),
        "artifact": str(temporal_path.relative_to(ROOT)), "sha256": sha256_file(temporal_path),
        "rule": "date-based; same station may occur across temporal partitions",
    }
    geographic_manifest = {
        "split_id": "TRACK-GEOGRAPHIC-v1", "status": "reference-not-frozen",
        "rule": "province/state/territory holdout: SHA256(geographic_region) modulo 8; bucket 7 test",
        "population": "stations with >=1 valid TRAIN and >=1 valid 2011-2025 observation",
        "dates": {"reference_end": TRAIN_END, "evaluation": [EVAL_START, EVAL_END]},
        "stations": len(population),
        "train_stations": int((population.split == "GEO-TRAIN").sum()),
        "test_stations": int((population.split == "GEO-TEST").sum()),
        "train_regions": sorted(population.loc[population.split == "GEO-TRAIN", "geographic_region"].unique().tolist()),
        "test_regions": sorted(population.loc[population.split == "GEO-TEST", "geographic_region"].unique().tolist()),
        "artifact": str(geographic_path.relative_to(ROOT)), "sha256": sha256_file(geographic_path),
    }
    write_json_atomic(temporal_dir / "manifest.json", temporal_manifest)
    write_json_atomic(geographic_dir / "manifest.json", geographic_manifest)
    return {"temporal": temporal_manifest, "geographic": geographic_manifest}


def enrich_target_summaries(summaries: list[dict], events: dict[str, pd.DataFrame],
                            coverage: pd.DataFrame) -> pd.DataFrame:
    """Ajoute saisonnalité et couverture explicitement pour chaque cible."""
    season_rows: list[dict] = []
    by_id = {item["target_id"]: item for item in summaries}
    for target_id, frame in events.items():
        if "start_dte" in frame:
            months = pd.to_datetime(frame.start_dte).dt.month.astype("Int64").astype(str)
        else:
            months = frame.event_month.astype("Int64").astype(str).replace("<NA>", "UNKNOWN")
        counts = months.value_counts().sort_index()
        by_id[target_id]["seasonality"] = {
            "basis": "event start month" if "start_dte" in frame else "annual peak month",
            "events_by_month": {str(month): int(count) for month, count in counts.items()},
        }
        for month, count in counts.items():
            season_rows.append({"target_id": target_id, "month": month, "events": int(count)})
        target_coverage = coverage[
            coverage.station.isin(frame.station.unique()) & coverage.yr.between(2011, 2025)]
        by_id[target_id]["coverage"] = {
            "population": "station-years 2011-2025 for stations with at least one target event",
            "artifact": "evaluation/reports/DATA-AUDIT-002/coverage/station-year-coverage.csv",
            "station_years": int(len(target_coverage)),
            "station_years_meeting_80pct": int(target_coverage.meets_80pct.sum()),
            "share_meeting_80pct": float(target_coverage.meets_80pct.mean()),
            "median_coverage_ratio": float(target_coverage.coverage_ratio.median()),
            "denominators": {"continuous": "292/365 (293/366 leap year)",
                             "seasonal": "174/217"},
        }
    return pd.DataFrame(season_rows)


def artifact_inventory(out: Path, extra_paths: list[Path]) -> dict[str, dict]:
    paths = [p for p in out.rglob("*") if p.is_file() and p.name != "manifest.json"]
    paths.extend(path for path in extra_paths if path.is_file())
    unique = sorted(set(path.resolve() for path in paths), key=str)
    return {
        str(path.relative_to(ROOT)): {"sha256": sha256_file(path), "bytes": path.stat().st_size}
        for path in unique
    }


def run_pipeline(db: Path, out: Path, cache: Path, cache_manifest: Path) -> dict:
    started = time.monotonic()
    source_hash = sha256_file(db)
    identity = cache_identity(
        source_sha256=source_hash,
        generator_files=[Path(__file__), ROOT / "scripts/cache_manager.py"],
        parameters={"table": "DLY_FLOWS", "validity": "value>0 OR symbol='D'",
                    "duckdb_version": duckdb.__version__},
        schema_version="hydat-daily-flow-v2",
    )
    cache_meta, cache_action = ensure_cache(cache, cache_manifest, identity, _daily_builder(db))
    if out.exists():
        for child in out.iterdir():
            if child.is_dir(): shutil.rmtree(child)
            else: child.unlink()
    for name in ["events", "targets", "coverage", "quality", "seasonality", "provenance"]:
        (out / name).mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute(f"ATTACH '{db}' AS hydat (TYPE sqlite, READ_ONLY)")
    coverage = make_coverage(con, cache, out)
    summaries: list[dict] = []
    events: dict[str, pd.DataFrame] = {}
    for q, minimum, target in [
        (0.95, 1, "T1-q095-refhalf"), (0.99, 1, "T1-q099-refhalf"),
        (0.99, 5, "T4-q099-N5-refhalf")]:
        events[target], summary = make_run_target(con, cache, q, minimum, target, out)
        summaries.append(summary)
    events["T3-peak-q09-refhalf"], peak_summary = make_peak_target(
        con, "T3-peak-q09-refhalf", out)
    summaries.append(peak_summary)
    splits = make_splits(con, cache, out)
    quality = {
        "station_year_rows": len(coverage),
        "continuous_rows": int((coverage.operation_class == "continuous").sum()),
        "seasonal_rows": int((coverage.operation_class == "seasonal").sum()),
        "rows_meeting_80pct": int(coverage.meets_80pct.sum()),
        "observed_days_above_denominator": int(coverage.observed_days_above_denominator.sum()),
        "zero_blank_cells": int(coverage.n_zero_blank.sum()),
        "estimated_cells": int(coverage.n_estimated.sum()),
        "coverage_rule": {"continuous": "292/365 (293/366 leap year)", "seasonal": "174/217"},
    }
    write_json_atomic(out / "quality/summary.json", quality)
    seasonality = enrich_target_summaries(summaries, events, coverage)
    _write_csv(seasonality, out / "seasonality/events-by-month.csv")
    environment = {
        "python": platform.python_version(), "platform": platform.platform(),
        "duckdb": duckdb.__version__, "pandas": pd.__version__,
    }
    source = {"path": str(db.relative_to(ROOT)), "sha256": source_hash, "release": RELEASE,
              "access": "DuckDB SQLite attachment READ_ONLY"}
    write_json_atomic(out / "provenance/source.json", source)
    write_json_atomic(out / "provenance/environment.json", environment)
    con.close()
    source_hash_after = sha256_file(db)
    if source_hash_after != source_hash:
        raise RuntimeError("raw source changed during audit")
    extras = [cache_manifest, *sorted((ROOT / "benchmark/targets").glob("*.yaml")),
              *sorted((ROOT / "benchmark/splits/temporal").glob("*")),
              *sorted((ROOT / "benchmark/splits/geographic").glob("*"))]
    artifacts = artifact_inventory(out, extras)
    manifest = {
        "audit_id": "DATA-AUDIT-002", "status": "READY_FOR_M03_REAUDIT",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": {**source, "sha256_after": source_hash_after, "unchanged": True},
        "cache": {**cache_meta, "action": cache_action},
        "periods": {"reference": [None, TRAIN_END], "evaluation": [EVAL_START, EVAL_END]},
        "targets": summaries, "splits": splits, "quality": quality,
        "environment": environment, "artifacts": artifacts,
        "pipeline": {"path": "scripts/audit_reference.py", "sha256": sha256_file(Path(__file__))},
        "elapsed_seconds": round(time.monotonic() - started, 3),
    }
    write_json_atomic(out / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--cache-manifest", type=Path, default=DEFAULT_CACHE_MANIFEST)
    args = parser.parse_args()
    result = run_pipeline(args.db.resolve(), args.out.resolve(), args.cache.resolve(),
                          args.cache_manifest.resolve())
    print(json.dumps({"audit_id": result["audit_id"], "status": result["status"],
                      "elapsed_seconds": result["elapsed_seconds"],
                      "targets": [{"id": x["target_id"], "events": x["events"]}
                                  for x in result["targets"]]}, indent=2))


if __name__ == "__main__":
    main()
