import pandas as pd
import pytest
from conftest import serie

from dow_backtest import backtest


def test_prix_plat_le_capital_baisse_seulement_des_frais():
    c = serie([100] * 20)
    res = backtest.acheter_et_garder(c, frais=0.01, capital_initial=1000)
    assert res["capital"].iloc[-1] == pytest.approx(1000 * 0.99)


def test_toujours_investi_sans_frais_egale_le_marche():
    c = serie([100, 101, 99, 105, 110, 108, 120])
    res = backtest.acheter_et_garder(c, frais=0.0, capital_initial=1000)
    # Decision au jour 0 -> achat a la cloture du jour 1 -> gains a partir du jour 2
    assert res["capital"].iloc[-1] == pytest.approx(1000 * 120 / 101)


def test_decision_executee_le_lendemain_jamais_le_jour_meme():
    c = serie([100, 110, 121, 133.1, 146.41, 161.05])  # +10 % par jour
    decision = pd.Series([0, 0, 1, 1, 1, 1], index=c.index)
    res = backtest.lancer(c, decision, frais=0.0)
    assert list(res["investi"]) == [0, 0, 0, 0, 1, 1]
    # Le gain du jour de la decision (jour 2) et du jour d'execution (jour 3) n'est PAS pris
    assert res["rendement"].iloc[2] == 0
    assert res["rendement"].iloc[3] == 0
    assert res["rendement"].iloc[4] == pytest.approx(0.10)


def test_frais_payes_a_chaque_achat_et_vente():
    c = serie([100] * 10)
    decision = pd.Series([1, 1, 0, 0, 1, 1, 1, 0, 0, 0], index=c.index)
    res = backtest.lancer(c, decision, frais=0.01, capital_initial=1000)
    assert res["frais"].sum() == pytest.approx(0.04)  # 2 achats + 2 ventes
    assert res["capital"].iloc[-1] == pytest.approx(1000 * 0.99**4)


def test_debut_evalue_seulement_la_periode_demandee_et_paie_l_entree():
    c = serie([100, 100, 100, 100, 110, 121])
    toujours = pd.Series(1, index=c.index)
    res = backtest.lancer(
        c, toujours, frais=0.01, capital_initial=1000, debut=str(c.index[3].date())
    )
    assert res.index[0] == c.index[3]
    assert res["capital"].iloc[-1] == pytest.approx(1000 * 0.99 * 1.21)
    assert res["frais"].sum() == pytest.approx(0.01)


def test_debut_apres_les_donnees_est_une_erreur():
    c = serie([100, 101])
    with pytest.raises(ValueError):
        backtest.acheter_et_garder(c, debut="2050-01-01")


def test_argent_comptant_rapporte_le_taux():
    c = serie([100] * 253)
    taux = pd.Series(0.05, index=c.index)
    jamais = pd.Series(0, index=c.index)
    res = backtest.lancer(c, jamais, frais=0.0, capital_initial=1000, taux_annuel=taux)
    # 252 jours d'interet (le premier jour n'a pas de taux "de la veille")
    assert res["capital"].iloc[-1] == pytest.approx(1000 * (1 + 0.05 / 252) ** 252)


def test_pas_d_interet_les_jours_investis():
    c = serie([100, 101, 99, 105, 110, 108, 120])
    taux = pd.Series(0.05, index=c.index)
    debut = str(c.index[2].date())
    avec = backtest.acheter_et_garder(c, frais=0.0, debut=debut, taux_annuel=taux)
    sans = backtest.acheter_et_garder(c, frais=0.0, debut=debut)
    assert avec["capital"].iloc[-1] == pytest.approx(sans["capital"].iloc[-1])


def test_anti_triche_le_taux_utilise_est_celui_de_la_veille():
    c = serie([100] * 5)
    taux = pd.Series([0.0, 0.0, 2.52, 0.0, 0.0], index=c.index)  # pic au jour 2
    jamais = pd.Series(0, index=c.index)
    res = backtest.lancer(c, jamais, frais=0.0, taux_annuel=taux)
    assert list(res["taux_jour"]) == pytest.approx([0, 0, 0, 0.01, 0])  # touche le jour 3


def test_taux_avec_dates_differentes_des_prix():
    c = serie([100] * 6)
    avant = c.index[0] - pd.Timedelta(days=10)
    taux = pd.Series([0.0252], index=[avant])  # une seule valeur, connue avant les prix
    res = backtest.lancer(c, pd.Series(0, index=c.index), frais=0.0, taux_annuel=taux)
    assert res["taux_jour"].iloc[1:].tolist() == pytest.approx([0.0001] * 5)
