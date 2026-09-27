# benchmark/baselines — Baselines de contrôle (B0–B5)

**Mission : REFERENCE-01 — §16.** Évaluées dans **exactement le même protocole** que le candidat
(`benchmark/protocols/reference-v0.2-draft.yaml`), sur les mêmes cibles `-refhalf`
(`benchmark/protocols/target-definitions-v0.1.yaml`).

> **Statut : références d'implémentation posées. Aucune baseline n'est encore entraînée.**
> L'audit produit la matière empirique (saisonnalité, quantiles) nécessaire ; l'entraînement
> (et surtout le gain Δ vs B2 et B5 exigé du candidat) se fera après gel du protocole.

## Règles communes

- Population, découpage, cibles, fuite : identiques au candidat (référentiel v0.2 §3–§7).
- Métriques publlées par cible/saison/symbole et par lead-time (§9).
- Le candidat doit montrer un **gain Δ ≥ +0,05 AUC/PR-AUC vs B2 ET B5** (proposition, D5) dans
  le même protocole — sinon le rendement est attribuable au calendrier ou à l'autocorrélation.

## B0 — Climatologie

`P(VERY_HIGH_FLOW_EVENT | mois)` — probabilité empirique du proxy hydrologique, et non
d'une inondation observée (audit phase F historique, T1-q099-whole) :

```text
m1:0.004   m2:0.004   m3:0.008   m4:0.023   m5:0.027   m6:0.023
m7:0.009   m8:0.003   m9:0.002   m10:0.003  m11:0.004  m12:0.004
```

Prédiction constante par mois du calendrier. Compétiteur redoutable vu le contraste MAM vs
sep/oct (×13) — c'est le minimal à battre.

## B1 — Persistance

`Q(t+H) ≈ Q(t)` — le débit prévu = débit actuel (auto-corrélation journalière élevée des séries
hydrologiques). Pour les cibles de run, « le run en cours continue ».

## B2 — Saison + persistance

Combinaison B0 × B1 (ex. moyennes pondérées des probabilités, ou logit additif saison+état). La
référence « usage commun » de tout système d'alerte trivial.

## B3 — Seuil historique

`dépassement vs seuil historique de la station` — cible = la même notion de seuil haute
(quantile quartier de référence / maximal annuel historique), énoncée en classifieur direct.

## B4 — Modèle statistique simple

Régression logistique sur peu de variables : mois, débit actuel, anomalie vs mois. Borne
supérieure des modèles « simples » (aucun apprentissage profond).

## B5 — Modèle ML indépendant

Random Forest / Gradient Boosting **bien spécifiés** (variables calendaires + débit + bornes
hydrologiques simples), entièrement contenus dans TRAIN (+VALIDATION pour les hyperparamètres) —
le niveau à dépasser pour justifier un prototype plus avancé.

## Fichiers souhaités (au gel)

```
benchmark/baselines/
  README.md                       ← ce fichier
  run_counts_{B0..B5}.yaml        (fichiers d'exécution, seeds, configs)
  results/B-Bn-{target_id}.csv    (sorties métriques)
```
