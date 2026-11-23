import math

import pandas as pd
import pytest
from conftest import serie

from dow_backtest import transactions


def cas_simple():
    #             0    1    2    3    4    5    6   7   8
    c = serie([100, 100, 110, 120, 115, 100, 100, 90, 90])
    investi = pd.Series([0, 0, 1, 1, 0, 0, 1, 1, 0], index=c.index)
    stops = pd.Series([90, 95, 95, 95, 95, 95, 99, 99, 99], index=c.index, dtype=float)
    return c, pd.DataFrame({"investi": investi}), stops


def test_transactions_calculees_a_la_main():
    c, res, stops = cas_simple()
    t = transactions.extraire(c, res, stops, frais=0.0, risque=100)
    assert len(t) == 2
    # 1 : achat jour 1 a 100, vente jour 3 a 120, stop 90 -> 10 parts -> +200 $ = +2 R
    assert t.loc[0, "prix_achat"] == 100 and t.loc[0, "prix_vente"] == 120
    assert t.loc[0, "stop"] == 90
    assert t.loc[0, "gain_dollars"] == pytest.approx(200)
    assert t.loc[0, "gain_R"] == pytest.approx(2)
    # 2 : achat jour 5 a 100, vente jour 7 a 90, stop 95 -> 20 parts -> -200 $ = -2 R
    assert t.loc[1, "gain_dollars"] == pytest.approx(-200)
    assert t.loc[1, "rendement"] == pytest.approx(-0.10)
    assert not t["ouverte"].any()


def test_statistiques_calculees_a_la_main():
    c, res, stops = cas_simple()
    s = transactions.statistiques(transactions.extraire(c, res, stops, frais=0.0, risque=100))
    assert s["taux_reussite"] == pytest.approx(0.5)
    assert s["total_dollars"] == pytest.approx(0)
    assert s["facteur_profit"] == pytest.approx(1.0)
    assert s["pertes_au_dela_du_risque"] == 1  # -2 R : la vente arrive apres le stop
    assert s["pire_baisse_dollars"] == pytest.approx(-200)
    assert "Taux de reussite" in transactions.texte(s)


def test_frais_reduisent_le_gain():
    c, res, stops = cas_simple()
    t = transactions.extraire(c, res, stops, frais=0.01, risque=100)
    # 10 parts, frais 1 % sur 100 $ (achat) + 120 $ (vente) par part = 22 $
    assert t.loc[0, "gain_dollars"] == pytest.approx(200 - 22)


def test_transaction_encore_ouverte_a_la_fin():
    c = serie([100, 100, 110, 120])
    res = pd.DataFrame({"investi": [0, 0, 1, 1]}, index=c.index)
    stops = pd.Series(90.0, index=c.index)
    t = transactions.extraire(c, res, stops, frais=0.0)
    assert t.loc[0, "ouverte"]
    assert t.loc[0, "prix_vente"] == 120


def test_deja_investi_au_premier_jour_evalue():
    c = serie([100, 105, 110, 120, 130])
    res = pd.DataFrame({"investi": [1, 1, 0]}, index=c.index[2:])  # fenetre commence au jour 2
    stops = pd.Series(100.0, index=c.index)
    t = transactions.extraire(c, res, stops, frais=0.0, risque=100)
    assert t.loc[0, "date_achat"] == c.index[2]  # achete au 1er jour evalue, a 110
    assert t.loc[0, "prix_achat"] == 110 and t.loc[0, "prix_vente"] == 120


def test_anti_triche_le_stop_est_celui_du_jour_de_la_decision():
    c, res, stops = cas_simple()
    avant = transactions.extraire(c, res, stops, frais=0.0)
    triche = stops.copy()
    triche.iloc[[1, 2, 3, 5, 6, 7, 8]] = 1.0  # changer les stops connus APRES chaque decision
    apres = transactions.extraire(c, res, triche, frais=0.0)
    pd.testing.assert_frame_equal(avant, apres)


def test_stop_au_dessus_du_prix_pas_de_taille():
    c, res, stops = cas_simple()
    stops.iloc[0] = 150.0
    t = transactions.extraire(c, res, stops, frais=0.0)
    assert math.isnan(t.loc[0, "gain_dollars"])
    assert t.loc[0, "rendement"] == pytest.approx(0.20)  # le rendement en % reste calcule


def test_aucune_transaction():
    c = serie([100, 101, 102])
    res = pd.DataFrame({"investi": [0, 0, 0]}, index=c.index)
    t = transactions.extraire(c, res, pd.Series(90.0, index=c.index))
    assert transactions.texte(transactions.statistiques(t)) == "Aucune transaction."
