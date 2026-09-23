#!/usr/bin/env python3
"""HYDAT-X — make_manifest.py

Génère le manifeste de dataset indépendant :
  registry/datasets/hydat-reference-<release>.yaml

Règles : aucune valeur non mesurée ; `null` lorsque inconnue ; le hash du
fichier SQLite est recalculé à l'exécution (jamais copié depuis une source).

Usage :
  python scripts/make_manifest.py [--release AAAAJJMM] [--out PATH]
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_yaml(p: Path) -> list | dict | None:
    try:
        import yaml  # noqa: PLC0415
    except ImportError:
        print("WARN : pyyaml indisponible — provenance lue de façon minimale", file=sys.stderr)
        return None
    try:
        with p.open() as f:
            return yaml.safe_load(f)
    except Exception as e:  # noqa: BLE001
        print(f"WARN : {p.name} illisible : {e}", file=sys.stderr)
        return None


def latest_release() -> str | None:
    base = ROOT / "data" / "raw" / "hydat"
    releases = sorted((d.name for d in base.iterdir() if d.is_dir() and d.name.isdigit()), reverse=True)
    return releases[0] if releases else None


def find_db(release: str | None) -> Path | None:
    base = ROOT / "data" / "raw" / "hydat"
    cands = list(base.rglob("*.sqlite*")) + list(base.rglob("*.db"))
    cands = [c for c in cands if c.is_file() and c.stat().st_size > 0]
    if release:
        cands = [c for c in cands if f"/{release}/" in str(c)]
    return sorted(cands)[0] if cands else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--release", default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    release = args.release or latest_release()
    if not release:
        print("ERREUR : aucune release HYDAT trouvée (data/raw/hydat/)", file=sys.stderr)
        return 1

    db = find_db(release)
    prov_file = ROOT / "metadata" / "downloads" / f"hydat-{release}-download-manifest.yaml"
    prov = load_yaml(prov_file) if prov_file.exists() else None

    schema_path = ROOT / "metadata" / "stations" / "hydat-schema.json"
    schema = None
    if schema_path.exists():
        schema = json.loads(schema_path.read_text())

    # Artefacts bruts depuis la provenance
    raw_artifacts = []
    if isinstance(prov, list):
        for a in prov:
            raw_artifacts.append({
                "path": f"data/raw/hydat/{release}/"
                + (a.get("filename") or f"documentation/{a.get('artifact')}"),
                "sha256": a.get("sha256"),
            })
    elif isinstance(prov, dict):
        for a in prov.get("artifacts", []) or []:
            raw_artifacts.append({"path": a.get("path"), "sha256": a.get("sha256")})

    retrieved = None
    if isinstance(prov, list) and prov:
        retrieved = prov[0].get("retrieved_at_utc")
    elif isinstance(prov, dict):
        retrieved = prov.get("retrieved_at_utc")

    tables = (schema or {}).get("tables", {})
    manifest = {
        "dataset_id": f"hydat-reference-{release}",
        "name": "HYDAT Reference",
        "source": "ECCC (Environnement et Changement climatique Canada)",
        "release": release,
        "retrieved_at_utc": retrieved,
        "raw_artifacts": raw_artifacts,
        "database": {
            "format": "sqlite",
            "path": str(db.relative_to(ROOT)) if db else None,
            "sha256": sha256_file(db) if db else None,
        },
        "schema": {
            "table_count": (schema or {}).get("table_count"),
            "station_table": (schema or {}).get("station_table_detected"),
        },
        "stations": {
            "count": (schema or {}).get("station_count"),
        },
        "period": (schema or {}).get("period", {"start": None, "end": None}),
        "tables": {t: tables[t]["row_count"] for t in tables},
        "transformations": ["none"],
        "status": "raw-reference",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    out = Path(args.out) if args.out else ROOT / "registry" / "datasets" / f"hydat-reference-{release}.yaml"
    out.parent.mkdir(parents=True, exist_ok=True)

    try:
        import yaml  # noqa: PLC0415
        body = yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True, width=100)
    except ImportError:
        body = json.dumps(manifest, indent=2, ensure_ascii=False)
    out.write_text(body)
    print(f"MANIFEST OK — {out.relative_to(ROOT)} (stations={manifest['stations']['count']}, tables={manifest['schema']['table_count']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())