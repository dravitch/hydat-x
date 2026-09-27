# Gabarit de mission et de journal d'exécution

> **Statut : GABARIT NON EXÉCUTÉ.** Une fiche de mission prescrit un travail ; elle ne prouve
> ni son exécution ni sa réussite. Les preuves et le statut réel vivent dans un journal distinct.

<!--
Synthèse de mécanismes observés dans les missions PALLAS M01, M06, M13, M27, M30, M31 et M32 :
baseline vérifiée, reproduction avant correction, critères observables, fenêtres de panne,
preuve avant/après, clôture honnête, gel reproductible, limites transmises et autorisation
humaine explicite avant action à fort impact.

Utilisation recommandée :
1. copier la PARTIE A dans `mission-<PROJET>-<ID>-<titre>.md` avant l'exécution ;
2. copier la PARTIE B dans `mission-<PROJET>-<ID>-journal.md` au début de l'exécution ;
3. ne jamais transformer la fiche prescriptive en journal en cochant silencieusement ses cases ;
4. conserver les deux fichiers et leurs liens réciproques.
-->

# PARTIE A — Fiche prescriptive

# MISSION — `<PROJET>-<ID>` — `<titre orienté résultat>`

## 0. Métadonnées

| Champ | Valeur |
|---|---|
| Mission ID | `<PROJET>-<ID>` |
| Date de création | `<AAAA-MM-JJ>` |
| Auteur / planificateur | `<nom ou rôle>` |
| Exécutant prévu | `<nom, agent ou rôle>` |
| Projet | `<projet>` |
| Statut initial | `<PROPOSÉE / PRÊTE / ACTIVE>` |
| Priorité | `<bloquante / critique / haute / normale / basse>` |
| Type | `<code / documentation / recherche / observation calendaire / migration / gouvernance>` |
| Dépend de | `<missions, commits, décisions ou aucune>` |
| Bloque | `<missions, publication, déploiement ou rien>` |
| Source de vérité | `<audit, ADR, ticket, fichier:section>` |
| Journal attendu | `mission-<PROJET>-<ID>-journal.md` |

### 0.1 Baseline exigée

| Élément | Exigence | Comment la vérifier avant action |
|---|---|---|
| Dépôt / corpus | `<chemin>` | `<commande ou manifeste>` |
| Branche / tag | `<référence>` | `<git rev-parse ...>` |
| Commit de départ | `<SHA complet ou À RÉSOUDRE>` | `<commande indépendante>` |
| État du worktree | `<propre / modifications admises listées>` | `<git status --short>` |
| Environnement | `<Nix / conteneur / lockfile / autre>` | `<commande>` |
| Artefacts d'entrée | `<liste + hashes si nécessaire>` | `<manifeste>` |

**Règle :** un hash annoncé dans la mission n'est pas une preuve. L'exécutant le résout et le
vérifie avant de travailler. Si la baseline n'est pas identifiable ou si le worktree contient
des modifications qui chevauchent la mission, arrêter et consigner le blocage.

### 0.2 Portée d'autorisation

| Action | Autorisée par cette mission ? | Approbation supplémentaire |
|---|---|---|
| Lecture et diagnostic | `<oui/non>` | `<aucune / laquelle>` |
| Modification des fichiers ciblés | `<oui/non>` | `<...>` |
| Création de tests ou probes | `<oui/non>` | `<...>` |
| Commit / tag | `<oui/non>` | `<...>` |
| Réseau / service externe | `<oui/non>` | `<...>` |
| Déploiement, lancement long ou effet externe | `<oui/non>` | `<GO explicite requis>` |
| Suppression / migration irréversible | `<oui/non>` | `<GO explicite requis>` |

Une mission peut autoriser la préparation d'une action sans autoriser son déclenchement. Les
points d'arrêt humains doivent être écrits ici, pas improvisés en fin d'exécution.

## 1. Contexte

### 1.1 Problème observé

`<Décrire le défaut, la lacune ou l'opportunité avec sa preuve précise. Séparer le fait observé
de son interprétation.>`

### 1.2 Pourquoi maintenant

`<Expliquer la dépendance, le risque ou le jalon qui justifie l'ordre de cette mission.>`

### 1.3 État actuel connu

- **Acquis :** `<ce qui est déjà prouvé et ne doit pas être redébattu sans preuve nouvelle>`
- **Défectueux ou manquant :** `<ce qui est précisément en cause>`
- **Inconnu :** `<ce que la mission doit mesurer ou laisser explicitement indéterminé>`
- **Hypothèses de travail :** `<hypothèses réfutables>`

### 1.4 Dépendances et contrats à préserver

| Contrat / consommateur | Risque de rupture | Vérification exigée |
|---|---|---|
| `<API, schéma, fichier, processus>` | `<...>` | `<test ou contrôle>` |

## 2. Objectif général

> `<Une phrase décrivant un changement observable. Éviter “améliorer”, “sécuriser” ou “finaliser”
> sans condition mesurable.>`

## 3. Objectifs détaillés

1. `<résultat observable 1>`
2. `<résultat observable 2>`
3. `<résultat observable 3>`

### 3.1 Hors objectifs

- `<travail adjacent explicitement exclu>`
- `<capacité que cette mission ne prétendra pas démontrer>`

### 3.2 Portées de décision séparées

| Portée | Ce que la mission peut démontrer | Ce qu'elle ne démontre pas |
|---|---|---|
| `<simulation / pilote / production / publication>` | `<...>` | `<...>` |

## 4. Protocole de validation

### 4.1 Baseline avant changement

L'exécutant doit reproduire le problème ou mesurer l'état initial avant correction, sauf si cette
reproduction causerait un dommage. Dans ce cas, documenter pourquoi et utiliser une fixture sûre.

| Mesure / probe | Résultat initial attendu | Preuve à conserver |
|---|---|---|
| `<commande ou scénario>` | `<défaut observé>` | `<sortie, fichier, hash>` |

### 4.2 Métriques avant / après

| Métrique | Baseline | Cible | Méthode de mesure |
|---|---:|---:|---|
| `<métrique>` | `<valeur ou À MESURER>` | `<seuil>` | `<commande>` |

Rapporter séparément réussites, échecs, skips et non-exécutés. Ne jamais recopier un chiffre d'un
journal précédent lorsqu'il peut être rejoué.

### 4.3 Tests discriminants

| Risque | Test positif | Test négatif / mutation | Résultat exigé |
|---|---|---|---|
| `<risque>` | `<comportement valide>` | `<défaut injecté>` | `<pass/fail attendu>` |

Un test qui passe parce que le chemin réel n'a jamais été atteint est un faux positif. Lorsque la
mission porte sur une barrière, inclure un défaut qui doit être détecté.

### 4.4 Scénarios de panne ou de concurrence — SI APPLICABLE

| Fenêtre / scénario | État à préserver | Comportement attendu après reprise |
|---|---|---|
| `<avant persistance / après émission / concurrence / corruption>` | `<...>` | `<...>` |

### 4.5 Validation finale

| Contrôle | Commande / méthode | Seuil de succès |
|---|---|---|
| Tests ciblés | `<...>` | `<0 échec>` |
| Suite complète | `<...>` | `<pass/fail/skip attendu>` |
| Qualité / cohérence | `<lint, typecheck, diff check>` | `<...>` |
| Reproductibilité | `<checkout propre / rebuild>` | `<...>` |

## 5. Procédure et gates d'exécution

### Partie A — Préparation et provenance

- lire intégralement les sources de vérité et fichiers ciblés ;
- résoudre la baseline et enregistrer l'état Git initial ;
- identifier les modifications préexistantes à préserver ;
- créer le journal avec statut `ACTIVE`.

### Partie B — Reproduction et mesures initiales

- reproduire le défaut ou mesurer l'état initial ;
- conserver les sorties brutes utiles ;
- confirmer que la mission traite bien la cause observée.

**Gate B :** si le défaut n'est pas reproduit, ne pas appliquer aveuglément le correctif prévu.
Consigner la divergence et réévaluer le mandat.

### Partie C — Exécution

- réaliser les objectifs dans un ordre réduisant le risque ;
- maintenir les contrats déclarés en §1.4 ;
- ajouter les tests avant ou avec le correctif ;
- consigner toute décision non triviale et toute déviation.

### Partie D — Vérification

- rejouer les probes initiales ;
- exécuter les tests ciblés puis la suite complète ;
- comparer avant/après ;
- contrôler le diff, les artefacts et les limites résiduelles.

### Partie E — Action à fort impact — OPTIONNELLE

**Point d'arrêt obligatoire :** `<décrire l'action préparée>`.

Après les Parties A–D, l'exécutant doit s'arrêter, présenter les preuves et attendre le texte
explicite `<GO attendu>` avant de lancer, publier, déployer, supprimer ou engager une observation
longue. Une préparation réussie n'autorise jamais implicitement l'action suivante.

## 6. Instructions à l'exécutant

1. Reproduire ou mesurer avant de corriger.
2. Ne jamais modifier un artefact hors périmètre sans expliquer la dépendance.
3. Préserver les changements préexistants de l'utilisateur.
4. Ne pas affaiblir, supprimer ou skipper un test pour obtenir une suite verte sans justification
   et arbitrage explicites.
5. Rapporter les résultats réellement observés, même s'ils contredisent la mission, un audit ou
   un journal précédent.
6. Ne pas confondre fonction présente, fonction appelée et capacité opérationnelle démontrée.
7. Si une décision d'architecture est prise, consigner alternatives, motif, plafond connu et
   conséquences pour les missions suivantes.
8. Garder les sorties brutes hors du journal lorsqu'elles sont volumineuses, mais conserver leur
   emplacement et leur provenance.
9. Laisser la mission ouverte si un critère bloquant n'est pas atteint.

## 7. Critères de succès

<!-- Tous les statuts commencent à NON ÉVALUÉ. Seul le journal les met à jour après exécution. -->

| ID | Critère observable | Bloquant ? | Statut initial | Preuve exigée |
|---|---|---|---|---|
| CS-01 | `<critère>` | `<oui/non>` | `NON ÉVALUÉ` | `<commande / artefact>` |
| CS-02 | `<critère>` | `<oui/non>` | `NON ÉVALUÉ` | `<...>` |
| CS-03 | `<critère>` | `<oui/non>` | `NON ÉVALUÉ` | `<...>` |

### Règle de clôture

- `CLÔTURÉE` : tous les critères bloquants sont prouvés sur la baseline finale ;
- `PARTIELLE` : des livrables existent, mais au moins un critère bloquant reste non atteint ;
- `BLOQUÉE` : une dépendance ou autorisation empêche toute progression utile ;
- `ANNULÉE` : l'objectif est retiré par décision explicite ;
- `OUVERTE` : exécution ou observation encore en cours.

Une mission calendaire n'est pas clôturée parce que son dispositif fonctionne. Une campagne de
12 minutes ne satisfait pas un critère de 72 heures, même si le superviseur, les logs et le
redémarrage contrôlé sont correctement livrés.

## 8. Interdictions spécifiques

- `<action interdite>`
- `<contournement interdit>`
- `<affirmation que la mission ne doit pas produire>`

## 9. Livrables et format attendu

| Livrable | Emplacement | Contenu minimum | Autoritaire ? |
|---|---|---|---|
| Journal | `mission-<PROJET>-<ID>-journal.md` | preuves, écarts, statut réel | oui pour l'exécution |
| Code / document | `<chemin>` | `<...>` | `<oui/non>` |
| Preuves brutes | `<dossier>` | sorties, logs, manifestes | oui pour les observations |
| ADR / décision | `<chemin ou N/A>` | choix structurant | oui pour la décision |

### 9.1 Condition de handoff

`<État minimal permettant à la mission suivante de démarrer sans supposer un résultat non prouvé.>`

---

# PARTIE B — Journal probant

# JOURNAL — `<PROJET>-<ID>` — `<titre>`

> **Ce journal décrit ce qui a réellement été exécuté.** Il ne doit pas recopier les objectifs
> comme s'ils étaient accomplis.

## J0. Identité et état

| Champ | Valeur observée |
|---|---|
| Mission | `<lien vers la fiche prescriptive>` |
| Statut réel | `<ACTIVE / OUVERTE / PARTIELLE / BLOQUÉE / CLÔTURÉE / ANNULÉE>` |
| Début / fin | `<horodatages + fuseau>` |
| Exécutant | `<nom ou agent>` |
| Baseline initiale | `<branche/tag + SHA complet>` |
| Baseline finale | `<SHA complet ou worktree non commité>` |
| État Git initial | `<propre / changements listés>` |
| État Git final | `<propre / changements listés>` |
| Environnement | `<versions / lock / contraintes>` |

## J1. Verdict de mission

**Statut :** `<...>`

`<Deux à cinq phrases distinguant : livrables produits, critères réellement atteints, critères
non atteints et effet sur la mission suivante.>`

### J1.1 Résumé des critères

| ID | Statut réel | Preuve | Commentaire honnête |
|---|---|---|---|
| CS-01 | `<PASS / FAIL / PARTIEL / NON ÉVALUÉ>` | `<chemin / sortie>` | `<...>` |

La mission ne peut être `CLÔTURÉE` si un critère bloquant est `FAIL`, `PARTIEL` ou
`NON ÉVALUÉ`.

## J2. Baseline et reproduction avant changement

| Contrôle | Attendu d'après la mission | Observé réellement | Preuve |
|---|---|---|---|
| `<probe>` | `<...>` | `<...>` | `<...>` |

**Divergences avec le mandat :** `<aucune ou liste>`.

## J3. Travail exécuté

### J3.1 Partie A — `<nom>`

- `<action réalisée>`
- `<résultat>`
- `<fichiers affectés>`

### J3.2 Partie B — `<nom>`

- `<...>`

### J3.3 Action à fort impact — SI APPLICABLE

| Élément | Valeur |
|---|---|
| Point d'arrêt atteint | `<oui/non>` |
| GO explicite reçu | `<citation ou référence, sans donnée sensible>` |
| Action déclenchée | `<oui/non>` |
| Horodatage | `<...>` |
| Résultat immédiat | `<...>` |

Si aucun GO n'a été reçu, écrire clairement `PRÉPARÉE, NON LANCÉE` plutôt que `terminée`.

## J4. Avant / après

| Élément | Avant réellement observé | Après réellement observé | Interprétation limitée à |
|---|---|---|---|
| `<métrique ou comportement>` | `<...>` | `<...>` | `<portée>` |

## J5. Validation réellement rejouée

| Commande / expérience | Réussis | Échoués | Skippés | Non exécutés | Code / résultat |
|---|---:|---:|---:|---:|---|
| `<commande>` | `<n>` | `<n>` | `<n>` | `<n>` | `<...>` |

### J5.1 Tests négatifs et faux positifs

| Test négatif / mutation | Résultat attendu | Résultat observé | Contrôle discriminant ? |
|---|---|---|---|
| `<...>` | `<échec / rejet>` | `<...>` | `<oui/non + raison>` |

### J5.2 Reproductibilité

- checkout ou corpus propre : `<oui/non>` ;
- rebuild depuis sources figées : `<oui/non/non applicable>` ;
- hashes d'artefacts vérifiés : `<n/n ou N/A>` ;
- contraintes de l'hôte et skips : `<...>`.

## J6. Décisions et déviations

| ID | Décision ou déviation | Alternatives | Motif | Conséquence |
|---|---|---|---|---|
| D-01 | `<...>` | `<...>` | `<...>` | `<...>` |

Une décision initialement raisonnable peut être invalidée par une preuve ultérieure. Ne pas
effacer la décision : ajouter un addendum daté qui explique l'inversion et son déclencheur.

## J7. Livrables

| Livrable | Chemin | État | Provenance / hash si utile |
|---|---|---|---|
| `<...>` | `<...>` | `<créé/modifié/préparé/non lancé>` | `<...>` |

## J8. Ce qui n'a pas été fait

- `<objectif non exécuté et raison>`
- `<test ou accès indisponible>`
- `<action préparée mais non autorisée>`

Cette section est obligatoire. Une absence explicite est plus utile qu'un silence interprété
comme réussite.

## J9. Limites et dettes résiduelles

| ID | Limite | Impact | Acceptée pour cette portée ? | Destination |
|---|---|---|---|---|
| L-01 | `<...>` | `<...>` | `<oui/non>` | `<mission suivante / backlog / audit>` |

Éviter « hors périmètre » sans destination lorsqu'une limite affecte la mission suivante.

## J10. Conséquences et handoff

- **Débloque :** `<mission ou action>`
- **Ne débloque pas :** `<portée encore interdite>`
- **Preuve à transmettre :** `<artefact>`
- **Baseline suivante recommandée :** `<tag / commit / corpus>`
- **Prochaine action discriminante :** `<test ou décision>`

## J11. Clôture

**Décision :** `<CLÔTURÉE / PARTIELLE / OUVERTE / BLOQUÉE / ANNULÉE>`

**Justification :** `<référence aux critères de J1.1, sans déclaration générale non prouvée>`

**Date et décideur de clôture :** `<...>`

### J11.1 Addendum après clôture — SI PREUVE NOUVELLE

Lorsqu'un environnement réel, un audit ou un rejeu ultérieur contredit le journal :

1. conserver le résultat initial et son contexte ;
2. ajouter un addendum daté ou un nouveau journal relié ;
3. décrire la nouvelle preuve et ce qu'elle invalide ;
4. rouvrir le critère concerné si nécessaire ;
5. ne pas maquiller rétroactivement la mission comme si l'erreur n'avait jamais existé.

## J12. Intégrité et distribution

| Élément | Valeur |
|---|---|
| Baseline exécutée | `<SHA / tag / version>` |
| Dossier de preuves | `<chemin>` |
| Manifeste externe | `<chemin ou N/A>` |
| Copie distribuée depuis | `<commit / release / paquet>` |

Ne pas insérer dans le journal son propre hash final ni le commit qui le contiendra. Enregistrer
ces valeurs après production dans un manifeste externe, un tag annoté ou une attestation séparée.
