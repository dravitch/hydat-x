from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from cache_manager import (  # noqa: E402
    CacheValidationError,
    cache_identity,
    ensure_cache,
    sha256_file,
    validate_cache,
)
from audit_reference import assert_no_future_threshold  # noqa: E402

AUDIT = ROOT / "evaluation/reports/DATA-AUDIT-002"


def _identity(source: Path, generator: Path) -> dict:
    return cache_identity(
        source_sha256=sha256_file(source), generator_files=[generator],
        parameters={"table": "fixture"}, schema_version="test-v1")


def test_valid_cache_is_accepted(tmp_path: Path):
    source, generator = tmp_path / "source", tmp_path / "generator.py"
    source.write_text("source")
    generator.write_text("code")
    cache, manifest = tmp_path / "cache.bin", tmp_path / "cache.json"
    calls = []

    def build(path: Path):
        calls.append(path)
        path.write_text("payload")

    identity = _identity(source, generator)
    ensure_cache(cache, manifest, identity, build)
    _, action = ensure_cache(cache, manifest, identity, build)
    assert action == "accepted"
    assert len(calls) == 1


def test_cache_is_refused_when_source_changes(tmp_path: Path):
    source, generator = tmp_path / "source", tmp_path / "generator.py"
    source.write_text("v1")
    generator.write_text("code")
    cache, manifest = tmp_path / "cache.bin", tmp_path / "cache.json"
    ensure_cache(cache, manifest, _identity(source, generator), lambda p: p.write_text("data"))
    source.write_text("v2")
    with pytest.raises(CacheValidationError, match="identité"):
        validate_cache(cache, manifest, _identity(source, generator))


def test_cache_is_refused_when_generator_code_changes(tmp_path: Path):
    source, generator = tmp_path / "source", tmp_path / "generator.py"
    source.write_text("source")
    generator.write_text("v1")
    cache, manifest = tmp_path / "cache.bin", tmp_path / "cache.json"
    ensure_cache(cache, manifest, _identity(source, generator), lambda p: p.write_text("data"))
    generator.write_text("v2")
    with pytest.raises(CacheValidationError, match="identité"):
        validate_cache(cache, manifest, _identity(source, generator))


def test_cache_without_manifest_is_refused(tmp_path: Path):
    source, generator = tmp_path / "source", tmp_path / "generator.py"
    source.write_text("source")
    generator.write_text("code")
    cache = tmp_path / "cache.bin"
    cache.write_text("orphan")
    with pytest.raises(CacheValidationError, match="manifeste absent"):
        validate_cache(cache, tmp_path / "missing.json", _identity(source, generator))


def test_temporal_split_has_strict_non_overlapping_boundaries():
    manifest = json.loads((ROOT / "benchmark/splits/temporal/manifest.json").read_text())
    rules = manifest["rules"]
    assert rules["TRAIN"][1] < rules["VALIDATION"][0]
    assert rules["VALIDATION"][1] < rules["TEST"][0]
    assert rules["TEST"][1] < rules["HOLDOUT"][0]
    rows = pd.read_csv(ROOT / manifest["artifact"])
    limits = {name: tuple(bounds) for name, bounds in rules.items()}
    for split, group in rows.groupby("split"):
        lower, upper = limits[split]
        if lower is not None:
            assert (group.first_date >= lower).all()
        assert (group.last_date <= upper).all()


@pytest.mark.parametrize("target", ["T1-q095-refhalf", "T1-q099-refhalf",
                                     "T4-q099-N5-refhalf"])
def test_run_events_do_not_cross_temporal_split_boundaries(target: str):
    rows = pd.read_csv(AUDIT / f"events/{target}.csv")
    limits = {
        "VALIDATION": ("2011-01-01", "2015-12-31"),
        "TEST": ("2016-01-01", "2020-12-31"),
        "HOLDOUT": ("2021-01-01", "2025-12-31"),
    }
    for split, group in rows.groupby("split"):
        lower, upper = limits[split]
        assert (group.start_dte >= lower).all()
        assert (group.end_dte <= upper).all()


def test_geographic_split_has_no_station_overlap():
    rows = pd.read_csv(ROOT / "benchmark/splits/geographic/stations.csv")
    train = set(rows.loc[rows.split == "GEO-TRAIN", "station"])
    test = set(rows.loc[rows.split == "GEO-TEST", "station"])
    assert train
    assert test
    assert train.isdisjoint(test)
    assert rows.station.is_unique
    train_regions = set(rows.loc[rows.split == "GEO-TRAIN", "geographic_region"])
    test_regions = set(rows.loc[rows.split == "GEO-TEST", "geographic_region"])
    assert train_regions.isdisjoint(test_regions)


@pytest.mark.parametrize("target", ["T1-q095-refhalf", "T1-q099-refhalf",
                                     "T4-q099-N5-refhalf"])
def test_thresholds_use_no_future_observation(target: str):
    rows = pd.read_csv(AUDIT / f"targets/{target}-thresholds.csv")
    assert (rows.reference_end <= "2010-12-31").all()
    assert (rows.cut_date == "2011-01-01").all()


def test_peak_thresholds_use_no_future_observation():
    rows = pd.read_csv(AUDIT / "targets/T3-peak-q09-refhalf-thresholds.csv")
    assert (rows.reference_end_year <= 2010).all()
    assert (rows.evaluation_start_year == 2011).all()


@pytest.mark.parametrize("target", ["T3-peak-q09-refhalf", "T4-q099-N5-refhalf"])
def test_challenge_target_is_materialized(target: str):
    rows = pd.read_csv(AUDIT / f"events/{target}.csv")
    assert len(rows) > 0
    assert rows.target_id.eq(target).all()


@pytest.mark.parametrize("target", ["T1-q095-refhalf", "T1-q099-refhalf",
                                     "T4-q099-N5-refhalf"])
def test_all_runs_have_equal_span_and_duration(target: str):
    rows = pd.read_csv(AUDIT / f"events/{target}.csv")
    span = (pd.to_datetime(rows.end_dte) - pd.to_datetime(rows.start_dte)).dt.days + 1
    assert span.eq(rows.dur).all()


def test_mutation_future_threshold_is_detected():
    """Mutation test: moving one reference end into evaluation must fail the invariant."""
    rows = pd.read_csv(AUDIT / "targets/T1-q095-refhalf-thresholds.csv").head(3)
    assert_no_future_threshold(rows, "reference_end", "2011-01-01")
    mutated = rows.copy()
    mutated.loc[mutated.index[0], "reference_end"] = "2012-01-01"
    with pytest.raises(ValueError, match="threshold leakage"):
        assert_no_future_threshold(mutated, "reference_end", "2011-01-01")


def test_coverage_has_explicit_bounded_denominators():
    rows = pd.read_csv(AUDIT / "coverage/station-year-coverage.csv")
    assert set(rows.operation_class) == {"continuous", "seasonal"}
    assert rows.coverage_ratio.between(0, 1).all()
    assert (rows.loc[rows.operation_class == "seasonal", "expected_days"] == 217).all()
    assert (rows.loc[rows.operation_class == "seasonal", "threshold_days_80pct"] == 174).all()


def test_each_target_summary_has_complete_f04_evidence():
    manifest = json.loads((AUDIT / "manifest.json").read_text())
    for target in manifest["targets"]:
        assert target["definition"]
        assert target["threshold_period"] and target["application_period"]
        assert target["threshold_distribution"]["stations_with_threshold"] > 0
        assert target["events"] > 0 and target["stations"] > 0
        assert target["seasonality"]["events_by_month"]
        assert target["coverage"]["station_years"] > 0
        assert target["leakage_risk"]


def test_manifest_hashes_all_declared_artifacts():
    manifest = json.loads((AUDIT / "manifest.json").read_text())
    assert len(manifest["artifacts"]) >= 20
    for relative, identity in manifest["artifacts"].items():
        path = ROOT / relative
        assert path.is_file(), relative
        assert path.stat().st_size == identity["bytes"]
        assert sha256_file(path) == identity["sha256"]


def test_audit_manifest_is_ready_but_not_frozen():
    manifest = json.loads((AUDIT / "manifest.json").read_text())
    assert manifest["status"] == "READY_FOR_M03_REAUDIT"
    assert all(split["status"] == "reference-not-frozen"
               for split in manifest["splits"].values())
