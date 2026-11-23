import time

from conftest import marche_aleatoire

from dow_backtest import backtest, mesures, strategie


def test_25000_lignes_en_moins_de_2_secondes():
    c = marche_aleatoire(25_000, graine=7)
    t0 = time.perf_counter()
    res = backtest.lancer(c, strategie.etat_tendance(c, 10))
    mesures.calculer(res)
    duree = time.perf_counter() - t0
    assert len(res) == 25_000
    assert duree < 2.0, f"trop lent : {duree:.2f} s"
