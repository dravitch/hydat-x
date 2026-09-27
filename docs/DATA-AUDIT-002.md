# DATA-AUDIT-002 — reconstruction de la référence HYDAT-X

Statut : **READY_FOR_M03_REAUDIT** — aucun gel, commit ou tag.

## Résultat

M02 fournit une chaîne distincte de `scripts/audit_hydat.py`, qui demeure le reproducteur
historique de DATA-AUDIT-001. `scripts/audit_reference.py` reconstruit le cache journalier,
les quatre cibles, la couverture, la qualité, la saisonnalité et deux objets de split.

Le cache refuse toute réutilisation sans manifeste ou si l'empreinte de la source, du code,
des paramètres, du schéma ou du fichier dérivé diverge. Son manifeste est
`registry/datasets/hydat-daily-flows-v2-cache.json`.

## Comparaison contrôlée

Les chiffres DATA-AUDIT-002 ne sont pas directement des « corrections » des volumes anciens :
ils reposent sur une période de référence fixe (≤2010) et une application 2011–2025, alors que
les audits antérieurs utilisaient la première moitié propre à chaque station.

| Audit / cible | Événements | Violations | Stations | Év./station | Durée méd. | Durée max |
|---|---:|---:|---:|---:|---:|---:|
| DATA-AUDIT-001 Q95 | 238 799 | 564 | 5 840 | 40,890 | 3 | 3 663 |
| F01FIX Q95 | 240 067 | 0 | 5 840 | 41,107 | 3 | 3 663 |
| DATA-AUDIT-002 Q95 | 92 634 | 0 | 2 092 | 44,280 | 2 | 678 |
| DATA-AUDIT-001 Q99 | 85 076 | 211 | 5 336 | 15,944 | 2 | 3 663 |
| F01FIX Q99 | 85 629 | 0 | 5 336 | 16,047 | 2 | 3 663 |
| DATA-AUDIT-002 Q99 | 32 819 | 0 | 2 044 | 16,056 | 2 | 663 |

L'écart de population vient de l'exigence d'avoir de l'information avant 2011 et une période
d'application après 2010. Les runs sont en plus bornés aux partitions VALIDATION, TEST et
HOLDOUT afin qu'aucun label ne traverse une frontière temporelle. La chute de durée maximale
ne résulte pas d'un plafond de durée arbitraire.

## Nature des assertions et limites

- **Faits mesurés** : comptes, distributions, couvertures, empreintes et invariants présents
  dans le manifeste et les artefacts hashés.
- **Décisions méthodologiques** : D1–D6, fenêtres temporelles, seuils et règles de split;
  elles sont appliquées mais non gelées.
- **Hypothèses/limites** : le proxy de très haut débit n'est pas une observation d'inondation;
  la pertinence hydrologique des longues séquences et du dénominateur saisonnier devra être
  examinée indépendamment en M03.

## Traçabilité

- source brute inchangée : SHA-256 `9185ea30301229ed90675dc82d71efe4b294d6f0227241e219d4c26d212ef517`;
- manifeste central : `evaluation/reports/DATA-AUDIT-002/manifest.json`;
- inventaire : 22 artefacts analytiques et contractuels avec SHA-256 et taille dans le manifeste;
- tests : cache, source/code modifiés, manifeste absent, anti-fuite, splits, T3/T4,
  invariant de runs et mutation future;
- documentation ECCC : les quatre chemins PDF du manifeste source pointent désormais vers
  le sous-répertoire réel `documentation/`.
