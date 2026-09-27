# JOURNAL DE MISSION — HYDAT-X-M01 — Fiabiliser la référence (avant gel v0.2)

> Statut : **ACTIVE** — Gate B franchi, F-01 corrigé et prouvé (0 violation), CS-08 prouvé.
> Corrections F-02 à F-08 et décisions D1–D6 restent ouvertes. Le présent document ne décrète pas de gel.

## 0. Métadonnées de session

| Champ | Valeur |
|---|---|
| Mission | `HYDAT-X-M01` — Fiabiliser la référence (spéc : `docs/mission-HYDAT-X-M01-fiabiliser-reference-v02.md`) |
| Document hors-tâche (audit amont) | `docs/AUDIT-HYDAT-X-001.md` (lu intégralement) |
| Baseline Git auditeur | `561e630d60b70bc697067e64a9c90aebeb0e6b05` (HEAD `main`) |
| Base brute (hash source) | SHA-256 `9185ea30301229ed90675dc82d71efe4b294d6f0227241e219d4c26d212ef517` (re-vérifié en fin de session : identique) |
| Fichier brut audité | `data/raw/hydat/20260717/sqlite/Hydat.sqlite3` (1 293 741 312 octets) — **lecture seule** |
| Environnement au démarrage | `nix develop` — 16/16 contrôles PASS (`verify_environment.sh`) |
| Worktree | Sale à l'ouverture (19 entrées non suivies, dont l'audit et cette mission) — conservé tel quel |
| Auteur du journal | Agent d'exécution M01 + revue humaine des décisions scientifiques |

## 1. Heure de départ et obligations de preuve

Début d'exécution : `2026-09-24 09:xx UTC`. Les règles d'arrêt du protocole A s'appliquent :
ne jamais geler, taguer ou publier v0.2 sans un `GO` humain explicite (portes D/gel humain).

## 2. Reproduction de F-01 — RÉSULTAT DU GATE B

### 2.1 Ce que l'audit affirmait (falsifiable)

> « **F-01 — lacunes calendaires qui ne coupent pas les runs** » : le pipeline peut placer dans un
> même run deux observations dont les dates ne sont pas consécutives (span != dur).
> Nombre annoncé : 564 événements `T1-q095-refhalf` et 211 événements `T1-q099-refhalf`.

### 2.2 Reproduction rejouable (sonde formelle)

Sonde : `scripts/reproduce_f01_span.py`, rejouable par chemins explicites, p. ex.
`nix develop -c python scripts/reproduce_f01_span.py evaluation/reports/DATA-AUDIT-001/events/T1-q095-refhalf.csv`.
(L'option `--all` n'existe pas ; et le banner de `nix develop` écrit sur **stdout** — lire le JSON
à partir du premier `{`.) Mode de calcul : `span = (end_dte - start_dte).days + 1`,
comparaison à la colonne `dur` — c'est exactement le test discriminant F-01 : « deux observations
placées dans un même run dont les dates ne sont pas consécutives » ⇔ `span != dur`.

Résultat **baseline datée** (avant toute correction), sur les artefacts DATA-AUDIT-001 existants :

| Cible | Dénominateur (lignes) | `span != dur` | Écart max | Gate B |
|---|---|---|---|---|
| `T1-q095-refhalf` | 238 799 | **564** | 4 947 j | **REPRODUIT** |
| `T1-q099-refhalf` | 85 076 | **211** | 4 947 j | **REPRODUIT** |

Exemple d'événement fautif — station `08NJ098`, run annoncé de 3 342 jours mais couvrant
1953-04-22 → 1975-12-31 (8 289 jours calendaires) : une lacune calendaire traverse le run sans le
couper. La sonde est déterministe et sans état ; son `sha256_sortie` pour l'argumentaire baseline
(chemin + nom de fichier) vaut `12c6fbd6ddac6797d1c2796e6ad2434e0414ddff0335a51dffb3e664ba2275f7`.
Aucun commit n'existe : la référence de version est le hash ci-dessus, pas un SHA de commit.

### 2.3 Conséquence protocolaire — Gate B levé

La mission exigeait : « si F-01 n'est pas reproduit, **ne pas corriger la segmentation** selon une
hypothèse ». Ici F-01 **est reproduit à l'identique** (564 / 211, mêmes dénominateurs que l'audit).
Le Gate B **est donc levé** : la correction de la continuité des runs peut être entreprise, en
préservant la preuve baseline ci-dessus (quelle que soit l'issue de la correction).

**Aucune base brute n'a été ni ne sera modifiée** (hash `9185ea30…ef517` immuable). Les CSV
d'événements ci-dessus sont des dérivations rejouables, pas la base.

## 3. Constats complémentaires portés au journal (état courant)

| ID | Constat | Preuve sur disque | Statut |
|---|---|---|---|
| J01 | 4 chemins PDF manifestés absents (F-05 de l'audit) | `evaluation/reports/DATA-AUDIT-001/` | Confirmé — non traité |
| J02 | 3/4 cibles `refhalf` annoncées (T3/T4) absentes des artefacts | `benchmark/targets/` | Confirmé — non traité |
| J03 | Cache de parquet réutilisé sans identité de source (F-03) | `logs/audit/dly_flows.parquet` | Partiellement traité — identité scellée (§5.5) |
| J04 | Couverture / dénominateur mal nommé (F-02) | `evaluation/reports/DATA-AUDIT-001/` | Confirmé — non traité |

## 4. Non-exécutions (respect de la portée)

- Aucune modification de `data/raw/hydat/20260717/sqlite/Hydat.sqlite3` (baseline brute).
- Aucun tag, commit de gel, ni publication de v0.2 sans GO humain.
- Aucune assertion de validité scientifique des seuils D1–D6 (hors décor).

## 5. Correction F-01 — livrée, testée et prouvée (2026-09-24, 2e itération)

### 5.1 Décision humaine levée avant d'agir

CS-08 était bloqué : `pytest` était absent du devShell et l'installation d'un paquet est hors
portée de la mission (§3.1). **Décision humaine explicite obtenue : « Autoriser pytest au
devShell ».** L'extra `dev` de `pyproject.toml` déclarait déjà `pytest>=8.0` — il n'a donc fallu
**aucune modification de `flake.nix`** (le diff `poppler_utils` préexistant de l'utilisateur est
intact). Installation : `nix develop -c uv sync --extra dev` → `pytest 9.1.1` (49 paquets résolus,
3 ajoutés : `pytest`, `pluggy`, `iniconfig`).

### 5.2 Correctif : une règle, une implémentation, testable

- `scripts/segmentation.py` — module de segmentation calendaire continue. Règle appliquée, celle
  du constat et non une hypothèse de seuil : **tout écart calendaire > 1 jour entre deux journées
  consécutives observées interrompt le run**. L'invariant `span == dur` devient vrai par
  construction. Le module **ne fixe aucun seuil** : les seuils sont fournis par l'appelant sous
  forme de relation `(station, q, cut_date)`, soit la table produite par l'amont. La politique
  d'observation `value > 0 OR symbol = 'D'` est celle déjà déclarée par `audit_hydat.py`.
- Cause racine confirmée dans le code d'origine (`scripts/audit_hydat.py:432-462`) : la
  segmentation ne lit que des journées **présentes** ; une journée absente n'émet pas de ligne, ne
  produit donc pas d'`ex=0`, et laisse la lacune traverser le run.
- `scripts/regenerate_f01_targets.py` — pipeline de régénération. Il réutilise
  `Audit.station_thresholds` pour les seuils (aucune règle inventée) et n'écrit que dans un nouvel
  ID d'audit, **jamais dans `DATA-AUDIT-001`**.

### 5.3 Preuve avant / après (rejouable, base brute inchangée)

| Jeu de données | `T1-q095-refhalf` | `T1-q099-refhalf` |
|---|---|---|
| Baseline `DATA-AUDIT-001` (preuve « avant », non écrite) | 238 799 év., **564** avec `span != dur` | 85 076 év., **211** avec `span != dur` |
| Sortie corrigée `DATA-AUDIT-001-F01FIX/` | 240 067 év., **0** avec `span != dur` | 85 629 év., **0** avec `span != dur` |

L'augmentation du nombre d'événements est le comportement attendu d'un découpage aux lacunes : des
runs monolittéraux qui étaient artificiellement soudés sont scindés. La baseline a été **rejouée
après** correction et restitue toujours 564 / 211 — la preuve « avant » est donc intacte.

Rejeu :

```
nix develop -c python scripts/regenerate_f01_targets.py          # 42,8 s -> 0 violation
nix develop -c python scripts/reproduce_f01_span.py <csv> ...     # sonde Gate B
```

Hash des sorties corrigées (manifeste `DATA-AUDIT-001-F01FIX/manifest.json`) :
`T1-q095-refhalf` → `9c0705479471373f…`, `T1-q099-refhalf` → `eea44d859a697457…`.
Ces hash sont **reproduits à l'identique lors d'une seconde exécution indépendante** : la
dérivation est donc déterministe (propriété vérifiée, pas supposée).

### 5.4 CS-08 — suite métier prouvée

`nix develop -c python -m pytest -q` → **5 passed**. Les tests sont discriminants :

| Test | Nature | Ce qu'il interdit |
|---|---|---|
| `test_consecutive_days_form_one_run` | positif | qu'une suite de jours consécutifs soit scindée à tort |
| `test_calendar_gap_splits_run` | négatif | qu'une lacune calendaire ne coupe pas |
| `test_all_events_span_equals_dur` | invariant | toute sortie violant `span == dur` |
| `test_mutation_old_segmentation_fails_invariant` | **mutation** | une fixture qui ne discriminerait plus : l'ancienne segmentation *doit* échouer dessus |
| `test_no_exceedance_yields_no_events` | régression | un événement sans excès |

Le test de mutation est la garde centrale : si quelqu'un réintroduit la segmentation fautive, la
fixture détecte que le contrôle ne teste plus rien.

### 5.5 F-03 — identité du cache scellée (traitement partiel et assumé)

La régénération réutilisait `logs/audit/dly_flows.parquet` sans justification machine-vérifiable —
c'est le finding F-03, et la session l'avait elle-même rencontré. Le manifeste scelle désormais :

| Élément | Valeur |
|---|---|
| Cache | `logs/audit/dly_flows.parquet`, 293 811 822 o, SHA-256 `c05aa2a5eb0f929a…` |
| Code générateur | `scripts/audit_hydat.py` `8a66610c283e91fa…` |
| Code de segmentation | `scripts/segmentation.py` `f98617fb3be1ed39…` |
| Base source | SHA-256 `9185ea30…ef517` |

**Ce qui reste ouvert dans F-03, et pourquoi ce n'est pas corrigé maintenant :**
`Audit.daily_parquet` (`scripts/audit_hydat.py:93-95`) fait `if p.exists(): return p` — il
accepte un cache existant sans jamais le valider contre sa source. Corriger ce comportement
signifierait modifier le **générateur de la preuve baseline** `DATA-AUDIT-001`, ce qui la rendrait
non reproductible. Arbitrage retenu : `audit_hydat.py` est laissé **strictement intact** (c'est la
preuve « avant ») ; l'identité est scellée à côté, dans le manifeste. Un gestionnaire de cache
validé par hash de source + hash de code reste à faire, et devra vivre dans un module séparé.

## 6. Conclusion de session rejouable — 2026-09-24 (2e itération)

- **Gate B — LEVÉ (F-01 reproduit à l'identique : 564 / 211).** La correction était donc autorisée.
- **Correctif F-01 — LIVRÉ, PROUVÉ.** Segmentation calendaire continue
  (`scripts/segmentation.py`), suite métier 5/5, régénération dans
  `evaluation/reports/DATA-AUDIT-001-F01FIX/` avec **0 événement** violant `span == dur` sur les
  deux cibles régénérées.
- **CS-08 — PROUVÉ** (`pytest 9.1.1`, 5 tests passés dans `nix develop`), après décision humaine
  explicite consignée au §5.1.
- **Base brute intacte** : SHA-256 re-vérifié identique à l'ouverture. **Aucun gel, aucun commit,
  aucun tag, aucune publication v0.2.** `DATA-AUDIT-001` intacte et rejouable.
- **F-03 (partiel)** — identité du cache scellée dans le manifeste.
- **Statut : `PARTIELLE` — la mission reste OUVERTE.** F-01 est corrigé et prouvé ; F-02 à F-06,
  D1–D6 et le réaudit tiers restent ouverts.

### Ce qui reste ouvert (ne rien déclarer gelé avant traitement)

1. **F-02** — couverture / dénominateurs mal nommés (J04).
2. **F-03 (partiel)** — l'identité du cache est désormais scellée dans le manifeste (§5.5), mais
   `Audit.daily_parquet` accepte toujours un cache existant sans validation contre sa source ; à
   traiter dans un module séparé, sans toucher le générateur de la preuve baseline.
3. **F-04** — 3 des 4 cibles `refhalf` promises (T3/T4) toujours absentes (J02).
4. **F-05** — 4 chemins PDF du manifeste toujours absents (J01).
5. **F-06** — régime de split (temporel vs géographique) non tranché ; dépend de D1–D6.
6. **D1–D6** — décisions scientifiques humaines non prises ; le §5 ne tranche aucun seuil.
7. **Réaudit indépendant** de la correction par un tiers, non encore conduit.

Tant que ces points sont ouverts, `CS-01..CS-12` ne sont pas tous satisfaits et la porte de gel
reste fermée.
