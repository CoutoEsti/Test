import pandas as pd
import pytest
from conftest import marche_aleatoire, serie

from dow_backtest.pivots import BAS, HAUT, trouver_pivots


def test_zigzag_connu():
    #          0  1  2  3  4  5  6  7  8  9 10 11 12
    valeurs = [1, 2, 3, 5, 3, 2, 1, 2, 4, 6, 4, 3, 2]
    c = serie(valeurs)
    p = trouver_pivots(c, fenetre=2)
    hauts = p[p["type"] == HAUT]
    bas = p[p["type"] == BAS]
    assert list(hauts["date_pivot"]) == [c.index[3], c.index[9]]
    assert list(hauts["prix"]) == [5, 6]
    assert list(bas["date_pivot"]) == [c.index[6]]
    assert list(bas["prix"]) == [1]


def test_confirmation_n_jours_apres_le_pivot():
    c = serie([1, 2, 3, 5, 3, 2, 1, 2, 4, 6, 4, 3, 2])
    p = trouver_pivots(c, fenetre=2)
    for _, ligne in p.iterrows():
        assert (
            c.index.get_loc(ligne["date_confirmation"]) == c.index.get_loc(ligne["date_pivot"]) + 2
        )


def test_plateau_donne_un_seul_sommet():
    p = trouver_pivots(serie([1, 2, 5, 5, 5, 2, 1, 0]), fenetre=2)
    assert len(p[p["type"] == HAUT]) == 1


def test_les_n_derniers_jours_ne_sont_jamais_des_pivots():
    c = serie([1, 2, 3, 4, 5, 6, 7, 10])  # le 10 final n'est pas encore confirme
    assert trouver_pivots(c, fenetre=2).empty


def test_fenetre_invalide():
    with pytest.raises(ValueError):
        trouver_pivots(serie([1, 2, 3]), fenetre=0)


@pytest.mark.parametrize("fenetre", [3, 10])
def test_anti_triche_couper_le_futur_ne_change_pas_le_passe(fenetre):
    """Les pivots connus au jour X sont les memes, qu'on ait ou non les donnees d'apres X."""
    c = marche_aleatoire(800, graine=fenetre)
    complet = trouver_pivots(c, fenetre)
    for coupe in [100, 357, 600, 799]:
        x = c.index[coupe]
        tronque = trouver_pivots(c.loc[:x], fenetre)
        attendu = complet[complet["date_confirmation"] <= x].reset_index(drop=True)
        pd.testing.assert_frame_equal(tronque, attendu)
