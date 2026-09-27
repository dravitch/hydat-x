# REFERENCE-01 REPORT — MISSION STATUS

| Champ | Valeur |
|---|---|
| Mission | **REFERENCE-01 — Audit données + protocol v0.2 (correctif REF-CODEX-CHECK-2026-09-23)** |
| Base | `data/raw/hydat/20260717/sqlite/Hydat.sqlite3` (SHA-256 vérifiée) |
| Date | 2026-09-24 |
| Statut global | **DATA UNDERSTOOD → protocole v0.2 = DRAFT (à geler)** |
| Pipeline | `scripts/audit_hydat.py` — reproductible, lecture seule, ≈285 s |

---

## 1. Hypothèses de la mission vs réalité mesurée

| Hypothèse | Mesure (audit) | Verdict |
|---|---|---|
| 15 ans de données HYDAT | Base 1850–2026 ; série journalières exploitables souvent >30 ans | ✓ |
| 2 000+ stations | **8 057** stations (6 464 avec ≥1 jour valide) | ✓ bien au-delà |
| AUC-ROC 0,95 | À tester contre le référentiel (jamais admis) | — |
| « données inédites » | Splits temporels/géographiques définis (v0.2 §4) | ✓ |

## 2. Livrables produits (REFERENCE-01)

| Livrable | État |
|---|---|
| `scripts/audit_hydat.py` | ✅ exécutable, reproductible (LEAN SUR OUTIL, sha256, READ_ONLY) |
| `docs/DATA-AUDIT-001.md` | ✅ narratif d'audit (33 tables, 8 057 stations, couverture, targets) |
| `docs/HYDAT-DATA-QUALITY.md` | ✅ flags + politique 0.0/manquants + 14 stations à exclure (HDR) |
| `docs/TARGET-DESIGN-001.md` | ✅ T1/T3/T4 quantifiées ; T2 = HUMAN DECISION REQUIRED |
| `docs/HYDAT-X-Reference-Protocol-v0.2-DRAFT.md` | ✅ (statut draft) |
| `benchmark/protocols/reference-v0.2-draft.yaml` | ✅ (statut draft) |
| `benchmark/protocols/target-definitions-v0.1.yaml` | ✅ (registre multi-définitions) |
| `benchmark/baselines/README.md` | ✅ B0–B5 (pas de train avant gel) |
| `evaluation/reports/DATA-AUDIT-001/` (report/summary/CSV/parquet/events) | ✅ généré par le pipeline |
| `docs/REFERENCE-01-REPORT.md` | ← présent document |

## 3. Résultats saillants

- **Population** : 8 057 stations ; 6 464 exploitables (49,5 M jours valides) ; 14 stations
  rejetées (0 jour valide) ; 314 stations RHBN.
- **Couverture** : médiane 79,9 % des jours de registre ; jours `0.0` sans symbole ambigus :
  **2,68 M (5,1 %)** → politique « jamais supposés », comptés séparément.
- **Cibles** (exploration) : T1-q095-whole 447 k événements → T1-q0999 25,9 k ;
  T1-q0995-whole 87,8 k (6 237 stations) ; runs pluriannuels `refhalf` jusqu'à **3 663 j**
  (documenté, plafond proposé 365 j, D4).
- **Saisonnalité** : pic **mai P=0,027** (printeemps/fonte), min sep/oct 0,002 — alimente B0
  et challenge C6.
- **Pics annuels** : 88 556 pics H, 3 546 stations, 1904–2025.

## 4. Décisions ouvertes (HUMAN DECISION REQUIRED) — blocage du gel

**Le protocole v0.2 ne peut être gelé sans validation humaine des points suivants :**

| # | Question | Proposition | Risque si non résolu |
|---|---|---|---|
| D1 | 0.0 sans symbole = manquant ou zéro réel ? | manquant | proportion des jours valides (±5 %) |
| D2 | exclure 14 stations sans jour valide ? | oui | pollution population |
| D3 | T2 : seuil absolu officiel (source ?) | externe requise | T2 impossible |
| D4 | plafond `refhalf` runs (3663 j) ? | 365 j + gap 5 j | événements démesurés |
| D5 | seuils population (10 ans / 80 % / 12 mois) ? | validés | — |
| D6 | bornes split (70/15/10/5) ? | validées | — |

## 5. Vérification de complétude (mission §« Vérification de complétude »)

- [x] Nouvelles sonde 0 courbe OK (0.0092 ≥ 0.1/0) dès le début de la tâche.
- [x] Tous les artefacts du §« Livrables » produits (docs + yaml + pipeline + outputs).
- [x] Traçabilité chaque chiffre → requête SQL (script) / CSV / summary.json.
- [x] Chiffres issus des DONNÉES, pas du plausib.
- [x] Reproducible de A à Z, lecture seule, hash vérifié.
- [~] **7.1.1/7.2 (agents propres BOOTSTRAP/SECOND)** : les missions originelles étaient
  attribuées à codex/agy ; la présente correction (REF-CODEX-CHECK) a été exécutée en autonomie
  par l'agent opencode avec validation des livrables MAISON. La relégation multi-agent distincte
  (7.1.1) reste **optionnelle** — risque faible puisque le référentiel est maintenant documenté
  indépendamment.
- [ ] **Au prochain run** : paragraphes qualité « piège B » et « si RELI-Codex a des questions »
  (non éligibles — pas de validation croisée accessible à ce stade).

## 6. Ne committez PAS

Les fichiers `docs/SECOND_PROMPT.md` et `docs/BOOTSTRAP_PROMPT.md` sont des fichiers de mission
(instruction) — **ils ne sont pas committés** (ce répertoire est celui de la mission ; les deux
prompts restent hors git). Le commit du travail d'ingénierie (docs + scripts + yaml +
`evaluation/reports/DATA-AUDIT-001/`) se fera au moment demandé par l'orchestrateur.