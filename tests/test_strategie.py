import pandas as pd
import pytest
from conftest import marche_aleatoire, serie, zigzag

from dow_backtest.strategie import confirmation, etat_tendance


def test_escalier_montant_donne_un_achat():
    # Sommets et creux de plus en plus hauts
    c = zigzag([+10, -5] * 8 + [+10])
    etat = etat_tendance(c, fenetre=2)
    assert etat.iloc[-1] == 1
    assert etat.iloc[:10].eq(0).all()  # pas de signal avant d'avoir assez de pivots


def test_escalier_descendant_apres_une_hausse_donne_une_vente():
    c = zigzag([+10, -5] * 6 + [-10, +5] * 6 + [-10])
    etat = etat_tendance(c, fenetre=2)
    assert etat.max() == 1  # on a ete investi pendant la hausse
    assert etat.iloc[-1] == 0  # on est sorti pendant la baisse


def test_escalier_descendant_seul_ne_donne_jamais_d_achat():
    c = zigzag([-10, +5] * 10)
    assert etat_tendance(c, fenetre=2).eq(0).all()


def test_valeurs_seulement_0_ou_1(aleatoire):
    assert set(etat_tendance(aleatoire, 10).unique()) <= {0, 1}


@pytest.mark.parametrize("fenetre", [3, 10])
def test_anti_triche_couper_le_futur_ne_change_pas_les_decisions(fenetre):
    c = marche_aleatoire(1200, graine=42 + fenetre)
    complet = etat_tendance(c, fenetre)
    for coupe in [150, 500, 901, 1199]:
        x = c.index[coupe]
        pd.testing.assert_series_equal(etat_tendance(c.loc[:x], fenetre), complet.loc[:x])


def test_confirmation_des_deux_indices():
    a = serie([0, 1, 1, 1, 0, 0, 1, 0])
    b = serie([0, 0, 1, 1, 1, 0, 0, 0])
    #  attendu : les deux a 1 -> 1, les deux a 0 -> 0, sinon on garde
    assert list(confirmation(a, b)) == [0, 0, 1, 1, 1, 0, 0, 0]
