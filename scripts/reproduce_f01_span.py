#!/usr/bin/env python3
"""Son de reproduction F-01 — continuité calendaire des runs.

Sonde rejouable demandée par la mission `HYDAT-X-M01` (Gate B).
But : vérifier sur les artefacts DATA-AUDIT-001 publiés si une même séquence
(station, régime) contient des lacunes calendaires qui ne coupent pas le run,
c.-à-d. si `span != dur` pour un événement.

Usage :
    python3 scripts/reproduce_f01_span.py [CSV...]
Sortie : JSON probant (denominator, span!=dur, écart max, exemple), hash du
résultat. Le nombre tiré d'HYDAT-AUDIT-001 est cité pour comparaison.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import date, datetime
from pathlib import Path

AUDIT_CLAIMS = {
    "T1-q095-refhalf": {"span_ne_dur": 564, "denominator": 238_799},
    "T1-q099-refhalf": {"span_ne_dur": 211, "denominator": 85_076},
}


def parse_iso(s: str) -> date:
    return datetime.strptime(s.strip(), "%Y-%m-%d").date()


def analyse(path: Path) -> dict:
    total = 0
    span_ne_dur = 0
    ecart_max = 0
    exemple = None
    with path.open(newline="", encoding="utf-8") as fh:
        header = fh.readline().strip().split(",")
        assert header == [
            "station",
            "dur",
            "start_dte",
            "end_dte",
        ], f"structure inattendue {header!r} dans {path.name}"
        for line in fh:
            if not line.strip():
                continue
            station, dur_s, start_s, end_s = line.strip().split(",")
            dur = int(dur_s)
            start = parse_iso(start_s)
            end = parse_iso(end_s)
            span = (end - start).days + 1
            total += 1
            if span != dur:
                span_ne_dur += 1
                ecart = span - dur
                if abs(ecart) > ecart_max:
                    ecart_max = abs(ecart)
                    exemple = {"station": station, "dur": dur, "span": span,
                               "start": start.isoformat(), "end": end.isoformat()}
    return {
        "fichier": path.name,
        "denominator": total,
        "span_ne_dur": span_ne_dur,
        "ecart_max_jours": ecart_max,
        "exemple": exemple,
    }


def main(argv: list[str]) -> int:
    if not argv:
        default = Path("evaluation/reports/DATA-AUDIT-001/events")
        if not default.exists():
            print("usage: reproduce_f01_span.py <events.csv...>", file=sys.stderr)
            return 2
        argv = [
            str(default / "T1-q095-refhalf.csv"),
            str(default / "T1-q099-refhalf.csv"),
        ]

    results = []
    for arg in argv:
        p = Path(arg)
        if not p.exists():
            results.append({"fichier": p.name, "erreur": "ABSENT"})
            continue
        r = analyse(p)
        claim = AUDIT_CLAIMS.get(
            p.stem if "refhalf" in p.name else p.name, {}
        )
        r["audit_span_ne_dur"] = claim.get("span_ne_dur")
        r["audit_denominator"] = claim.get("denominator")
        if r.get("span_ne_dur") is not None:
            r["conformite_audit"] = (
                r["span_ne_dur"] == claim.get("span_ne_dur")
                and r["denominator"] == claim.get("denominator")
            )
            r["gate_b"] = (
                "DIVERGENCE"
                if r["span_ne_dur"] != claim.get("span_ne_dur")
                else "REPRODUIT"
            )
        results.append(r)

    blob = json.dumps(results, ensure_ascii=False, indent=2, sort_keys=True)
    digest = hashlib.sha256(blob.encode()).hexdigest()
    out = {"mode_reproduction": "span = (end - start).days + 1 ; comparaison span vs dur",
           "baseline_audit": "AUDIT-HYDAT-X-001", "sha256_sortie": digest, "resultats": results}
    print(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
