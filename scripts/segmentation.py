"""segmentation.py — HYDAT-X M01 : segmentation calendaire continue des runs.

Corrige le finding `F-01` de `AUDIT-HYDAT-X-001` : la segmentation d'origine
(`scripts/audit_hydat.py::Audit.events_runs`) n'émet de ligne que pour les journées
PRÉSENTES dans le registre. Une journée calendaire sans observation n'est donc pas
visible du fenêtrage `sum(ex=0)`, et ne coupe pas le run : un événement peut
couvrir une plage calendaire non continue (`span != dur`).

Règle appliquée ici — celle énoncée par le constat, sans hypothèse de seuil :

    tout écart calendaire > 1 jour entre deux journées consécutives observées
    interrompt le run (la lacune est un séparateur)

Après segmentation, l'invariant `span == dur` est vrai par construction pour tout
événement retourné.

Le module ne fixe AUCUN seuil : les seuils sont fournis par l'appelant sous la
forme d'une relation `(station, q, cut_date)`, c'est-à-dire la table de seuils déjà
produite par le pipeline amont (`station_thresholds`). La politique d'observation
`value > 0 OR symbol = 'D'` est celle déclarée par `audit_hydat.py` et n'est pas
remodulée ici.

Usage (pipeline, base ~1 Go) :

    import duckdb, segmentation
    con = duckdb.connect()
    runs = segmentation.runs(con, obs_rel="read_parquet('dly_flows.parquet')",
                             thr_rel="read_parquet('thresholds.parquet')",
                             min_dur=1)
    bad = segmentation.violations(runs)     # doit être vide
"""

from __future__ import annotations

import pandas as pd

# relation d'observations : colonnes attendues = station, dte, value, symbol
# relation de seuils      : colonnes attendues = station, q, cut_date
_RUNS_TEMPLATE = """
WITH obs AS (
    SELECT {station} AS station, {date} AS dte, {value} AS value, {symbol} AS symbol
    FROM {obs_rel}
    WHERE {date} IS NOT NULL AND {value} IS NOT NULL
      AND ({value} > 0 OR {symbol} = 'D')
),
thr AS (
    SELECT station, q, cut_date FROM {thr_rel}
),
j AS (
    SELECT o.station, o.dte, o.value, t.q, t.cut_date
    FROM obs o JOIN thr t USING (station)
    WHERE t.cut_date IS NULL OR o.dte >= t.cut_date
),
ex AS (
    SELECT station, dte, (value > q) AS ex
    FROM j
),
lagged AS (
    SELECT station, dte, ex,
           LAG(dte) OVER w AS prev_dte,
           LAG(ex)  OVER w AS prev_ex
    FROM ex
    WINDOW w AS (PARTITION BY station ORDER BY dte)
),
marked AS (
    SELECT station, dte, ex,
           CASE WHEN ex
                     AND (prev_ex IS NULL
                          OR NOT prev_ex
                          OR date_diff('day', prev_dte, dte) > 1)
                THEN 1 ELSE 0 END AS starts_run
    FROM lagged
),
grp AS (
    SELECT station, dte, ex,
           SUM(starts_run) OVER (PARTITION BY station ORDER BY dte) AS rid
    FROM marked
)
SELECT station, COUNT(*) AS dur, MIN(dte) AS start_dte, MAX(dte) AS end_dte
FROM grp
WHERE ex
GROUP BY station, rid
HAVING COUNT(*) >= {min_dur}
ORDER BY station, start_dte
"""


def runs_sql(obs_rel: str, thr_rel: str, min_dur: int = 1,
             station: str = "station", date: str = "dte",
             value: str = "value", symbol: str = "symbol") -> str:
    """Retourne le SQL de segmentation calendaire continue (interpolation sûre)."""
    for name, rel in (("obs", obs_rel), ("thr", thr_rel)):
        if not isinstance(rel, str) or not rel.strip():
            raise ValueError(f"{name}_rel doit être une relation SQL non vide")
    if min_dur < 1:
        raise ValueError("min_dur doit être >= 1")
    return _RUNS_TEMPLATE.format(
        obs_rel=obs_rel, thr_rel=thr_rel, min_dur=int(min_dur),
        station=station, date=date, value=value, symbol=symbol)


def runs(con, obs_rel: str, thr_rel: str, min_dur: int = 1, **cols) -> pd.DataFrame:
    """Exécute la segmentation et renvoie les événements (DataFrame)."""
    return con.execute(runs_sql(obs_rel, thr_rel, min_dur, **cols)).fetchdf()


def violations(events: pd.DataFrame) -> pd.DataFrame:
    """Retourne les événements violant l'invariant `span == dur` (doit être vide)."""
    ev = events.copy()
    start = pd.to_datetime(ev["start_dte"])
    end = pd.to_datetime(ev["end_dte"])
    span = (end - start).dt.days + 1
    dur = pd.to_numeric(ev["dur"])
    ev["span"] = span
    return ev[span != dur].reset_index(drop=True)
