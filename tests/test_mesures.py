import math

import pandas as pd
import pytest

from dow_backtest import mesures


def resultat(capitaux, investi=None, debut="2000-01-01", frequence="D"):
    index = pd.date_range(debut, periods=len(capitaux), freq=frequence)
    capital = pd.Series(capitaux, index=index, dtype=float)
    depart = capitaux[0]
    rendement = capital.pct_change().fillna(capital.iloc[0] / depart - 1)
    investi = pd.Series(investi if investi is not None else [1] * len(capitaux), index=index)
    return pd.DataFrame({"capital": capital, "rendement": rendement, "investi": investi})


def test_capital_double_en_un_an_donne_100_pourcent_par_an():
    index = pd.to_datetime(["2001-01-01", "2002-01-01"])
    res = pd.DataFrame(
        {"capital": [100.0, 200.0], "rendement": [0.0, 1.0], "investi": [1, 1]}, index=index
    )
    m = mesures.calculer(res)
    assert m["rendement_total"] == pytest.approx(1.0)
    assert m["rendement_annuel"] == pytest.approx(1.0, rel=1e-3)  # 365 / 365.25 jours


def test_pire_baisse_calculee_a_la_main():
    m = mesures.calculer(resultat([100, 120, 60, 90, 130]))
    assert m["pire_baisse"] == pytest.approx(-0.5)  # de 120 a 60


def test_pas_de_baisse_donne_zero():
    assert mesures.calculer(resultat([100, 110, 120]))["pire_baisse"] == 0


def test_transactions_et_temps_investi():
    m = mesures.calculer(resultat([100] * 6, investi=[1, 1, 0, 0, 1, 0]))
    assert m["transactions"] == 4  # entree au depart, sortie, entree, sortie
    assert m["temps_investi"] == pytest.approx(0.5)


def test_sharpe_non_defini_si_aucune_variation():
    m = mesures.calculer(resultat([100] * 5, investi=[0] * 5))
    assert math.isnan(m["sharpe"])


def test_sharpe_mesure_le_rendement_au_dessus_du_taux():
    index = pd.date_range("2000-01-01", periods=4, freq="D")
    taux_jour = pd.Series([0.001, 0.002, 0.001, 0.002], index=index)
    res = pd.DataFrame(
        {
            "capital": (1 + taux_jour).cumprod() * 100,
            "rendement": taux_jour,  # rapporte exactement le taux : aucun excedent
            "investi": 0,
            "taux_jour": taux_jour,
        }
    )
    assert math.isnan(mesures.calculer(res)["sharpe"])
