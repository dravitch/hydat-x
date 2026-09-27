"""test_f01_continuity.py — CS-01 / CS-08 : tests métier de la continuité calendaire.

Tests DISCRIMINANTS (mission §4.3) :
  * positif  : jours consécutifs au-dessus du seuil -> UN run, span == dur
  * négatif  : une journée calendaire SANS observation entre deux excès
               -> DEUX runs (la lacune coupe) ; span == dur sur chacun
  * négatif  : l'ancienne segmentation (sans coupure calendaire) NE coupe PAS
               -> la mutation détecte bien le défaut F-01
  * invariant : span == dur pour tous les événements retournés

Ces tests n'utilisent que des fixtures minimales (aucune lecture de la base brute).
"""

import pandas as pd
import pytest

from scripts.segmentation import runs, violations, runs_sql

# ---------------------------------------------------------------------------
# fixtures minimales
# ---------------------------------------------------------------------------


@pytest.fixture
def mini_thresholds(tmp_path):
    """Deux stations, seuil unique = 10.0, sans cut_date (whole-series)."""
    p = tmp_path / "thr.parquet"
    pd.DataFrame({
        "station": ["S1", "S2"],
        "q": [10.0, 10.0],
        "cut_date": [None, None],
    }).to_parquet(p)
    return f"read_parquet('{p}')"


@pytest.fixture
def mini_obs(tmp_path):
    """Observations minimales : quelques jours, dont un 'trou' calendaire (J2 absent)."""
    # S1 : J1=20, J2 ABSENT (lacune), J3=20  -> doit produire DEUX runs
    # S2 : J1=20, J2=20, J3=20              -> doit produire UN run (3 j)
    #      plus J5=20 sans J4                 -> un 2e run (lacune J4)
    rows = [
        ("S1", "2020-01-01", 20.0, None),  # au-dessus
        ("S1", "2020-01-03", 20.0, None),  # au-dessus, J2 manquant (lacune)
        ("S1", "2020-01-04", 5.0, None),   # sous seuil -> coupe
        ("S2", "2020-01-01", 20.0, "D"),
        ("S2", "2020-01-02", 20.0, None),
        ("S2", "2020-01-03", 20.0, None),
        ("S2", "2020-01-05", 20.0, None),  # J4 manquant (lacune)
    ]
    df = pd.DataFrame(rows, columns=["station", "dte", "value", "symbol"])
    df["dte"] = pd.to_datetime(df["dte"])
    p = tmp_path / "obs.parquet"
    df.to_parquet(p)
    return f"read_parquet('{p}')"


@pytest.fixture
def con():
    import duckdb

    c = duckdb.connect()
    yield c
    c.close()


# ---------------------------------------------------------------------------
# test positif : jours consécutifs -> un seul run
# ---------------------------------------------------------------------------


def test_consecutive_days_form_one_run(con, mini_obs, mini_thresholds):
    ev = runs(con, mini_obs, mini_thresholds)
    s2 = ev[ev["station"] == "S2"].reset_index(drop=True)
    # S2 : J1..J3 consécutifs -> run unique de 3 jours, span == dur == 3
    first = s2[pd.to_datetime(s2["start_dte"]) == pd.Timestamp("2020-01-01")]
    assert len(first) == 1
    assert int(first.iloc[0]["dur"]) == 3
    assert int(first.iloc[0]["dur"]) == (first.iloc[0]["end_dte"]
                                         - first.iloc[0]["start_dte"]).days + 1


# ---------------------------------------------------------------------------
# test négatif : une lacune calendaire coupe le run
# ---------------------------------------------------------------------------


def test_calendar_gap_splits_run(con, mini_obs, mini_thresholds):
    ev = runs(con, mini_obs, mini_thresholds)
    s1 = ev[ev["station"] == "S1"].sort_values("start_dte").reset_index(drop=True)
    # S1 : J1 (exces) | lacune J2 | J3 (exces) -> DEUX runs distincts
    assert len(s1) == 2, "la lacune calendaire doit scinder le run en deux"
    # chacun des deux runs a une seule journée
    assert list(s1["dur"]) == [1, 1]
    # la lacune (2020-01-02) n'est couverte par aucun run
    covered = {d for r in s1.itertuples() for d in
               pd.date_range(r.start_dte, r.end_dte)}
    assert pd.Timestamp("2020-01-02") not in covered


def test_all_events_span_equals_dur(con, mini_obs, mini_thresholds):
    ev = runs(con, mini_obs, mini_thresholds)
    bad = violations(ev)
    assert bad.empty, f"{len(bad)} événements violent span==dur"


# ---------------------------------------------------------------------------
# test de mutation : l'ancienne segmentation (sans coupure calendaire)
# reproduit le défaut F-01 -> le test est bien discriminant
# ---------------------------------------------------------------------------


def test_mutation_old_segmentation_fails_invariant(con, mini_obs, mini_thresholds):
    """La segmentation SANS LAG-gap produit span != dur (defaut F-01)."""
    old_sql = f"""
    WITH obs AS (
        SELECT station, dte, value, symbol FROM {mini_obs}
        WHERE dte IS NOT NULL AND value IS NOT NULL
          AND (value > 0 OR symbol = 'D')
    ),
    j AS (
        SELECT o.station, o.dte, (o.value > 10.0) AS ex
        FROM obs o
    ),
    r AS (
        SELECT station, dte, ex,
               sum(CASE WHEN NOT ex THEN 1 ELSE 0 END)
                   OVER (PARTITION BY station ORDER BY dte) AS grp
        FROM j
    )
    SELECT station, COUNT(*) AS dur, MIN(dte) AS start_dte, MAX(dte) AS end_dte
    FROM r WHERE ex GROUP BY station, grp ORDER BY station
    """
    ev_old = con.execute(old_sql).fetchdf()
    bad_old = violations(ev_old)
    # l'ancienne version DOIT violer l'invariant sur la fixture à lacune
    assert not bad_old.empty, (
        "la mutation est supposede échouer (span != dur) ; "
        "si elle passe, la fixture ne discrimine plus"
    )


# ---------------------------------------------------------------------------
# test de régression : sortie vide sur entrées sans excès
# ---------------------------------------------------------------------------


def test_no_exceedance_yields_no_events(tmp_path):
    import duckdb

    obs = pd.DataFrame({
        "station": ["S3", "S3"],
        "dte": pd.to_datetime(["2021-05-01", "2021-05-02"]),
        "value": [1.0, 2.0],
        "symbol": [None, None],
    })
    p = tmp_path / "obs2.parquet"
    obs.to_parquet(p)
    thr = pd.DataFrame({"station": ["S3"], "q": [10.0], "cut_date": [None]})
    t = tmp_path / "thr2.parquet"
    thr.to_parquet(t)
    c = duckdb.connect()
    ev = runs(c, f"read_parquet('{p}')", f"read_parquet('{t}')")
    c.close()
    assert ev.empty
