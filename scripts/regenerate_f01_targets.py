"""regenerate_f01_targets.py — HYDAT-X M01 Partie C/D : régénération corrigée de F-01.

Régénère les cibles `refhalf` avec la segmentation calendaire continue
(`scripts/segmentation.py`) au lieu de la segmentation fautive d'origine
(`Audit.events_runs`, qui ne voit que les journées présentes et laisse donc
les lacunes calendaires traverser les runs).

Garanties :
  * base brute JAMAIS modifiée (lecture seule via le pipeline amont) ;
  * seuils IDENTIQUES à ceux de l'audit amont (on réutilise
    `Audit.station_thresholds`, aucune règle de seuil inventée) ;
  * DATA-AUDIT-001 (preuve « avant ») INACTÉ : tout sort dans un nouvel ID
    d'audit explicitement relié, conformément à la mission ;
  * preuve Gate B rejouée sur la sortie : 0 événement avec span != dur.

Usage :
    nix develop -c python scripts/regenerate_f01_targets.py
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from audit_hydat import Audit, DB, FLOW, FLOWSYM  # noqa: E402
from segmentation import runs, violations  # noqa: E402

OUT = ROOT / "evaluation" / "reports" / "DATA-AUDIT-001-F01FIX"
EVENTS = OUT / "events"

# (label, qfrac, min_dur) — mêmes cibles refhalf que celles matérialisées par l'amont.
TARGETS = [
    ("T1-q095-refhalf", 0.95, 1),
    ("T1-q099-refhalf", 0.99, 1),
]


def sha256f(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    EVENTS.mkdir(parents=True, exist_ok=True)

    aud = Audit(DB)  # ATTACH READ_ONLY sur la base brute
    base_sha = sha256f(DB)

    # ---- F-03 : sceller l'identite du cache AVANT de s'en servir -------------
    # Le parquet journalier est reutilise tel quel : sans cette scelle, la
    # derivation n'est pas reproductible (c'est le finding F-03 de l'audit).
    cache = aud.daily_parquet("DLY_FLOWS", FLOW, FLOWSYM, "dly_flows.parquet")
    cache_identity = {
        "chemin": str(cache.relative_to(ROOT)),
        "sha256": sha256f(cache),
        "octets": cache.stat().st_size,
        "genere_par_code_sha256": {
            "scripts/audit_hydat.py": sha256f(ROOT / "scripts" / "audit_hydat.py"),
            "scripts/segmentation.py": sha256f(ROOT / "scripts" / "segmentation.py"),
        },
        "source_base_sha256": base_sha,
        "note": "cache reutilise tel quel ; identite scellee ici (F-03). "
                "Une regeneration doit reproduire ce sha256.",
    }
    print(f"  [F01FIX] cache scelle : {cache_identity['chemin']} "
          f"sha256={cache_identity['sha256'][:16]}… "
          f"({cache_identity['octets']:,} o)", flush=True)

    manifest = {
        "audit_id": "DATA-AUDIT-001-F01FIX",
        "relie_a": "DATA-AUDIT-001 (preuve avant, intacte)",
        "finding": "F-01",
        "correction": "segmentation calendaire continue (lacune = separateur)",
        "source_base": str(DB),
        "source_base_sha256": base_sha,
        "cache_identity": cache_identity,
        "seuils": "reutilises tels quels (Audit.station_thresholds, politique"
                  " reference-first-half) — aucun seuil invente",
        "cible": [],
    }

    for label, qfrac, min_dur in TARGETS:
        aud.station_thresholds(qfrac, "reference-first-half")
        ev = runs(
            aud.con,
            obs_rel=f"read_parquet('{cache}')",
            thr_rel="_thr",
            min_dur=min_dur,
        )
        bad = violations(ev)
        path = EVENTS / f"{label}.csv"
        ev.to_csv(path, index=False)
        item = {
            "cible": label,
            "qfrac": qfrac,
            "min_dur": min_dur,
            "n_events": int(len(ev)),
            "span_ne_dur": int(len(bad)),
            "sha256": sha256f(path),
            "fichier": str(path.relative_to(ROOT)),
        }
        manifest["cible"].append(item)
        print(f"  [F01FIX] {label}: {len(ev):,} événements | span!=dur = {len(bad)} "
              f"| {item['sha256'][:16]}…", flush=True)

    (OUT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")

    total_bad = sum(c["span_ne_dur"] for c in manifest["cible"])
    print(f"\nTOTAL span!=dur sur les cibles regenerees : {total_bad} "
          f"(invariant CS-01 attendu : 0) — {time.time() - t0:.1f}s")
    if total_bad != 0:
        print("ECHEC : la correction n'est pas prouvee", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
