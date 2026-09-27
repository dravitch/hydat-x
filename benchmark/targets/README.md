# benchmark/targets/

Ce répertoire contient les **définitions M02 non gelées** (un YAML par cible). Le registre
`benchmark/protocols/target-definitions-v0.1.yaml` est conservé comme preuve historique;
le protocole courant pointe directement vers ce répertoire.

État M02 : quatre définitions de référence, produites mais non gelées :

- `T1-q095-refhalf.yaml` — cible primaire.
- `T1-q099-refhalf.yaml` — stress rare.
- `T3-peak-q09-refhalf.yaml` — challenge extrême.
- `T4-q099-N5-refhalf.yaml` — challenge de persistance.
- Événements : `evaluation/reports/DATA-AUDIT-002/events/*.csv`.

Ces fichiers restent `reference-not-frozen` jusqu'à la ré-audition M03 :

```
T1-q099-refhalf.yaml
T1-q095-refhalf.yaml
T3-peak-q09-refhalf.yaml
T4-q099-N5-refhalf.yaml
```

Chaque fichier décrit : population, quantile+base, règle de run, période, rôle,
horizon, `threshold_information_time=historical_reference`, artefacts d'événements associés.
