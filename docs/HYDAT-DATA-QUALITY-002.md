# HYDAT data quality 002

Source : HYDAT 20260717, SHA-256
`9185ea30301229ed90675dc82d71efe4b294d6f0227241e219d4c26d212ef517`.

## Politique d'observation

Un jour est valide si `value > 0 OR symbol = 'D'`. Les valeurs `0.0` sans symbole restent
ambiguës et sont comptées séparément, sans être transformées silencieusement en zéros réels.
DATA-AUDIT-002 en compte **2 681 846**; **2 788 356** cellules portent le symbole estimé `E`.

## Couverture

La population, le dénominateur, l'observé et la classe d'exploitation sont explicites dans
`evaluation/reports/DATA-AUDIT-002/coverage/station-year-coverage.csv` :

- population : couples station–année avec cellules de débit, jusqu'en 2025;
- `observed_days` : compte brut des jours valides selon la règle ci-dessus;
- `coverage_observed_days` : numérateur borné au dénominateur attendu; les observations hors
  population attendue restent publiées dans `observed_days_above_denominator`, de sorte que
  le ratio ne dépasse jamais 1 sans masquer les jours supplémentaires;
- continu : 365 jours attendus, seuil de référence 80 % = 292 jours (366/293 en année bissextile);
- saisonnier : classification issue de `STN_OPERATION_SCHEDULE` lorsque les mois ne couvrent
  pas JAN–DEC; dénominateur de référence 217 jours, seuil 80 % = 174 jours;
- années sans calendrier saisonnier explicite : classe continue, sans inférence saisonnière.

Sur 171 429 couples station–année, 1 952 sont explicitement saisonniers et 108 253 atteignent
le seuil de couverture. Les calendriers saisonniers comptent 22 377 jours valides au-delà de
leur dénominateur normatif; ils sont exposés séparément et le ratio final reste borné à 1.
La couverture est un attribut publié; M02 ne l'utilise pas pour inventer
un nouveau filtre d'admissibilité absent des décisions D1–D6.
