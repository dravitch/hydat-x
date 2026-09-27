# Gabarit d'audit indépendant

> **Statut : GABARIT NON EXÉCUTÉ.** Remplir ce document ne constitue pas une preuve qu'un
> audit a eu lieu. Dans DELTA-5, son utilisation n'active pas le protocole adversarial, qui
> reste **EN VEILLE jusqu'au deuxième projet**.

<!--
Ce gabarit synthétise les mécanismes les plus robustes observés dans les audits PALLAS v0.1,
v0.3, v0.5.1, v0.5.2 et dans le mandat d'audit v0.7 : baseline immuable, hiérarchie des
preuves, rejeu indépendant, suivi des constats, portée séparée des décisions et conservation
des limites. Supprimer les sections marquées OPTIONNEL lorsqu'elles ne s'appliquent pas.
-->

## 0. Identité de l'audit

| Champ | Valeur |
|---|---|
| Identifiant | `<AUDIT-ID>` |
| Cible auditée | `<projet / cadre / système / dossier>` |
| Type | `<audit initial / réaudit / audit ciblé / addendum>` |
| Question de décision | `<question précise à trancher>` |
| Auditeur | `<nom ou rôle>` |
| Commanditaire | `<nom ou rôle>` |
| Début / fin | `<AAAA-MM-JJ HH:MM TZ>` / `<AAAA-MM-JJ HH:MM TZ>` |
| Référentiel | `<norme, spécification ou critères applicables>` |
| Rapport précédent | `<chemin ou N/A>` |
| Verdict précédent | `<verdict ou N/A>` |

### 0.1 Baseline immuable

| Élément | Valeur résolue par l'auditeur | Méthode de résolution |
|---|---|---|
| Dépôt ou corpus | `<chemin / URI>` | `<commande / manifeste>` |
| Branche | `<branche ou N/A>` | `<commande>` |
| Tag demandé | `<tag ou N/A>` | `<commande>` |
| Commit / version réellement auditée | `<identifiant complet>` | `<résolu indépendamment>` |
| Hash du paquet de preuve | `<SHA-256 ou N/A>` | `<commande>` |
| État de travail initial | `<propre / sale>` | `<détails exacts>` |
| État de travail final | `<propre / sale>` | `<détails exacts>` |
| Éléments exclus | `<liste et justification>` | — |

**Règle d'arrêt :** si la baseline exigée ne peut pas être résolue de manière univoque, arrêter
l'audit. Ne pas remplacer silencieusement un tag absent par la branche courante, ni un corpus
figé par une copie plus récente.

## 1. Mandat, périmètre et interdictions

### 1.1 Objectif principal

> `<Formuler une seule question falsifiable. Exemple : la condition X est-elle réellement
> fermée sur la baseline Y ?>`

### 1.2 Sous-questions

1. `<sous-question>`
2. `<sous-question>`
3. `<sous-question>`

### 1.3 Dans le périmètre

- `<composant, document, période ou comportement>`
- `<...>`

### 1.4 Hors périmètre

- `<élément non audité et raison>`
- `<...>`

### 1.5 Interdictions faites à l'auditeur

- ne pas créditer un chiffre, une case cochée ou une fermeture sur la seule foi d'un journal ;
- ne pas transformer une absence de preuve en succès ou en échec démontré ;
- ne pas modifier la cible pour la faire passer pendant l'audit ;
- ne pas mélanger des portées de décision différentes dans un verdict unique ;
- ne pas supprimer un constat résiduel parce que l'objectif principal est atteint ;
- ne pas utiliser une preuve produite après la baseline sans la déclarer comme telle ;
- ne pas exposer de secret, donnée personnelle ou information exclue du périmètre.

## 2. Règles de preuve

### 2.1 Hiérarchie

Ordre de force par défaut :

1. **preuve dynamique rejouée** sur la baseline figée ;
2. **code, données ou artefact primaire** inspecté directement ;
3. **document ou journal** cohérent avec les artefacts primaires ;
4. **déclaration non reproduite** ;
5. **non vérifiable** dans le périmètre autorisé.

Une preuve de niveau inférieur ne l'emporte pas sur une observation directe contradictoire.
L'absence de test dynamique ne rend pas automatiquement le code faux ; elle limite la force de
la conclusion.

### 2.2 Statuts d'une affirmation

| Statut | Signification |
|---|---|
| `CONFIRMÉE` | L'affirmation est soutenue par une preuve recevable dans son périmètre. |
| `PARTIELLE` | Une partie est soutenue, une réserve matérielle subsiste. |
| `CONTREDITE` | Une preuve recevable démontre que l'affirmation est fausse sur la baseline. |
| `NON_VÉRIFIABLE` | Les artefacts ou droits requis ne sont pas disponibles. |
| `HORS_PÉRIMÈTRE` | L'audit n'est pas autorisé ou conçu pour la trancher. |

### 2.3 Règles de comptage

- rapporter séparément `réussis / échoués / ignorés / non exécutés` ;
- ne jamais appeler « réussis » le nombre total de cas découverts ;
- distinguer une commande verte d'un contrôle réellement discriminant ;
- conserver les codes de sortie, versions d'outils et causes de skip ;
- signaler tout faux positif où le test passe sans atteindre le comportement qu'il prétend
  vérifier.

## 3. Méthode et reproductibilité

### 3.1 Environnement

| Élément | Valeur |
|---|---|
| Système / architecture | `<...>` |
| Environnement reproductible | `<Nix / conteneur / lockfile / aucun>` |
| Versions d'outils | `<...>` |
| Accès réseau | `<autorisé / interdit / partiel>` |
| Identifiants ou données réelles | `<non utilisés / jeu dédié / autre>` |
| Contraintes de l'hôte | `<sandbox, permissions, ressources>` |

### 3.2 Procédure réellement exécutée

| # | Commande ou contrôle | Résultat brut conservé à | Code / état |
|---:|---|---|---|
| 1 | `<commande exacte>` | `<fichier de preuve>` | `<0 / erreur / skip>` |
| 2 | `<inspection ou expérience>` | `<fichier de preuve>` | `<résultat>` |

> Les longues sorties vivent dans un dossier de preuves, pas dans le rapport. Le rapport les
> résume et pointe vers leur emplacement ainsi que leur hash lorsqu'elles sont déterminantes.

### 3.3 Modifications pendant l'audit

| Modification | Emplacement | Motif | Persistante ? | Effet possible sur le verdict |
|---|---|---|---|---|
| `<probe temporaire / aucune>` | `<...>` | `<...>` | `<oui/non>` | `<...>` |

Les probes temporaires doivent rester hors de la cible ou être explicitement identifiées. Un
correctif appliqué pendant l'audit exige une nouvelle baseline et un réaudit ; il ne ferme pas
rétroactivement le constat de la baseline précédente.

## 4. Verdict exécutif

### 4.1 Réponse à la question principale

**Verdict :** `<GO / NO-GO / GO CONDITIONNEL / FERMÉ / FERMÉ AVEC RÉSERVE / OUVERT / autre>`

**Niveau de confiance :** `<élevé / moyen / faible>`, parce que `<preuves et limites>`.

`<Deux à cinq phrases : ce qui est démontré, ce qui empêche un verdict plus favorable et la
portée exacte de la décision.>`

### 4.2 Décisions séparées par portée

| Portée | Verdict | Motif déterminant | Condition de réexamen |
|---|---|---|---|
| `<phase / usage / environnement A>` | `<...>` | `<...>` | `<...>` |
| `<phase / usage / environnement B>` | `<...>` | `<...>` | `<...>` |

Ne pas compenser une faiblesse critique d'une portée par la réussite d'une autre. Exemple
générique : un GO pour simulation ne vaut pas GO pour exploitation réelle.

### 4.3 Constats prioritaires

1. **`<ID>` — `<titre>` :** `<une phrase factuelle>`
2. **`<ID>` — `<titre>` :** `<une phrase factuelle>`
3. **`<ID>` — `<titre>` :** `<une phrase factuelle>`

## 5. Vérification des affirmations

| ID | Affirmation auditée | Source de l'affirmation | Observation indépendante | Preuve | Statut |
|---|---|---|---|---|---|
| C-01 | `<affirmation exacte>` | `<fichier:ligne>` | `<ce qui a été observé>` | `<dynamique/code/doc>` | `<statut>` |
| C-02 | `<...>` | `<...>` | `<...>` | `<...>` | `<...>` |

Inclure les affirmations positives, les cases cochées, les chiffres annoncés, les fermetures de
constats et les capacités décrites dans les runbooks. Vérifier spécialement qu'un chemin existe
au point d'exécution réel, pas seulement comme fonction ou texte non appelé.

## 6. Résultats d'exécution

| Vérification | Attendu | Observé | Pass / Fail / Skip | Preuve brute |
|---|---|---|---|---|
| `<suite ou expérience>` | `<critère>` | `<chiffres exacts>` | `<...>` | `<chemin + hash>` |

### 6.1 Tests négatifs et capacité de détection

| Défaut injecté ou cas adversarial | Contrôle censé le détecter | Détecté ? | Conclusion |
|---|---|---|---|
| `<entrée invalide / artefact corrompu / mutation>` | `<test ou gate>` | `<oui/non>` | `<...>` |

Un contrôle qui ne rencontre jamais le défaut visé ne prouve pas qu'il fonctionne. Lorsque le
risque le justifie, inclure au moins une mutation ou une probe qui doit échouer.

## 7. Analyse par axe

<!-- Adapter les axes au référentiel. Ne conserver que des axes définis avant l'observation. -->

### 7.1 Axe A — `<nom>`

**État :** `<satisfait / partiel / non satisfait / non vérifiable>`

- **Acquis :** `<...>`
- **Écart :** `<...>`
- **Preuve déterminante :** `<...>`
- **Limite de la preuve :** `<...>`

### 7.2 Axe B — `<nom>`

**État :** `<...>`

- **Acquis :** `<...>`
- **Écart :** `<...>`
- **Preuve déterminante :** `<...>`
- **Limite de la preuve :** `<...>`

### 7.3 Axe C — `<nom>`

**État :** `<...>`

- **Acquis :** `<...>`
- **Écart :** `<...>`
- **Preuve déterminante :** `<...>`
- **Limite de la preuve :** `<...>`

## 8. Findings détaillés

<!-- Dupliquer cette section pour chaque finding. -->

### `<ID>` — `<titre court>`

| Champ | Contenu |
|---|---|
| Sévérité | `<bloquante / critique / élevée / moyenne / faible>` |
| État | `<OUVERT / PARTIELLEMENT_FERMÉ / FERMÉ / NON_VÉRIFIABLE>` |
| Portée | `<contrôle / composant / phase / projet>` |
| Cible | `<fichier, fonction, processus ou exigence>` |
| Type | `<logique / empirique / sécurité / statistique / opérationnel / provenance>` |

**Constat falsifiable :** `<une phrase affirmative, précise et réfutable>`

**Preuve :**

- `<commande, sortie, fichier:ligne, donnée ou hash>`
- `<preuve indépendante complémentaire>`

**Reproduction :**

```text
<étapes minimales et résultat attendu/observé>
```

**Mécanisme et impact :** `<comment le défaut produit concrètement une conséquence, sans
confondre possibilité abstraite et chemin réellement accessible>`

**Ce qui réfuterait le finding :** `<preuve qui démontrerait que l'objection est fausse>`

**Condition minimale de fermeture :** `<résultat observable, pas seulement “corriger le code”>`

**Réserve résiduelle après fermeture :** `<ce que la correction ne prouverait toujours pas>`

## 9. Suivi des constats antérieurs — OPTIONNEL POUR UN RÉAUDIT

| ID antérieur | État revendiqué | Vérification indépendante | État audité | Réserve / nouveau finding |
|---|---|---|---|---|
| `<ID>` | `<fermé / ouvert>` | `<preuve rejouée>` | `<fermé / partiel / ouvert>` | `<...>` |

Règles :

- une correction de code ne ferme pas nécessairement la capacité opérationnelle ;
- un test contrôlé ne remplace pas une observation longue si la durée fait partie du critère ;
- une fermeture partielle reste visible ;
- les constats nouveaux reçoivent de nouveaux identifiants ;
- ne pas réécrire un ancien rapport : produire un addendum ou un nouveau rapport qui conserve
  la trace de l'erreur et de sa correction.

## 10. Matrice des risques résiduels

| ID | Risque | Mécanisme concret | Barrière actuelle | Force de preuve | Sévérité | Condition de levée |
|---|---|---|---|---|---|---|
| `<ID>` | `<événement redouté>` | `<chaîne causale>` | `<contrôle réel>` | `<dynamique/code/doc>` | `<...>` | `<preuve attendue>` |

La sévérité, l'état épistémique et la décision sont trois dimensions différentes. Un risque
grave peut être non vérifiable ; une preuve solide peut porter sur un défaut mineur.

## 11. Éléments non vérifiables et limites

L'audit n'a pas pu confirmer :

- `<élément>` — cause : `<accès, donnée, temps, sécurité, périmètre>` ;
- `<élément>` — preuve requise : `<...>`.

Effets possibles sur le verdict : `<aucun / réserve / décision bloquée>`.

### 11.1 Preuves absentes ou postérieures

| Preuve attendue | État | Conséquence honnête |
|---|---|---|
| `<artefact>` | `<absent / postérieur / inaccessible>` | `<indéterminé, réserve, hors périmètre>` |

## 12. Conditions de passage et plan de réaudit

| Priorité | Condition observable | Propriétaire | Échéance | Preuve exigée | Portée débloquée |
|---:|---|---|---|---|---|
| 1 | `<condition>` | `<rôle>` | `<date>` | `<test, artefact, observation>` | `<...>` |

**Ordre recommandé :** commencer par les preuves susceptibles de changer la décision, pas
simplement par les corrections les moins coûteuses.

**Nouvelle baseline requise :** `<tag / commit / dossier de preuve>`

**Critère d'arrêt du prochain audit :** `<condition explicite>`

## 13. Comparaison avec l'audit précédent — OPTIONNEL

| Axe ou finding | Audit précédent | Audit courant | Évolution expliquée par |
|---|---|---|---|
| `<...>` | `<...>` | `<...>` | `<preuve nouvelle>` |

Un score ne doit évoluer que si une preuve nouvelle le justifie. La moyenne arithmétique ne
doit jamais masquer un veto, une preuve manquante ou une portée restée NO-GO.

## 14. Conclusion et décision

**Question principale :** `<réponse brève et exacte>`

**Décision par portée :**

- `<portée A>` : **`<verdict>`** — `<raison>` ;
- `<portée B>` : **`<verdict>`** — `<raison>`.

**Prochaine preuve discriminante :** `<une preuve ou expérience>`

**Constats restant ouverts :** `<IDs>`

**Réserve de validité :** ce rapport s'applique uniquement à la baseline et au périmètre
identifiés en §0–1. Toute correction, nouvelle donnée ou modification matérielle exige un
nouvel audit ou un addendum explicitement relié à cette version.

## 15. Intégrité et distribution du rapport

| Élément | Valeur |
|---|---|
| Baseline auditée | `<identifiant déjà résolu en §0.1>` |
| Manifeste externe de distribution | `<chemin ou identifiant>` |
| Hash du rapport consigné dans ce manifeste | `<SHA-256, enregistré hors de ce fichier>` |
| Hash du dossier de preuves | `<SHA-256, arbre ou manifeste externe>` |
| Emplacement des sorties brutes | `<chemin>` |
| Copie distribuée depuis | `<commit, release ou artefact signé>` |

Ne pas insérer dans le rapport son propre hash final ni le commit qui le contiendra : toute
modification destinée à ajouter cette valeur la rendrait immédiatement obsolète. Enregistrer
ces identifiants dans un manifeste externe, une release ou une attestation signée.

Avant diffusion :

- vérifier que tous les commits cités existent réellement ;
- vérifier les chemins et ancres de preuve ;
- exécuter les gardes de provenance disponibles ;
- conserver les chiffres bruts de tests ;
- ne pas distribuer une copie détachée sans commit ou hash permettant de l'identifier ;
- appliquer les règles de confidentialité et de publication du projet.
