import pytest
from conftest import marche_aleatoire, prix_complets

from dow_backtest import cli, config, donnees


@pytest.fixture
def faux_marche(tmp_path, monkeypatch):
    """Remplace Yahoo par des prix inventes et ecrit dans un dossier temporaire."""
    c = marche_aleatoire(9000, graine=3, debut="1992-01-02")  # 1992 a ~2026

    def faux_yahoo(symbole):
        return prix_complets(c)

    monkeypatch.setattr(donnees, "telecharger_yahoo", faux_yahoo)
    monkeypatch.setattr(config, "DOSSIER_DONNEES", tmp_path / "data")
    monkeypatch.setattr(config, "DOSSIER_RAPPORTS", tmp_path / "rapports")
    return tmp_path


def test_lancement_complet_produit_tableau_et_graphique(faux_marche, capsys):
    assert cli.executer(["SPY"]) == 0
    sortie = capsys.readouterr().out
    assert "Acheter-garder" in sortie
    assert "Pire baisse" in sortie
    assert list((faux_marche / "rapports").glob("*.png"))
    assert list((faux_marche / "rapports").glob("*.csv"))


def test_periode_cachee_refusee_sans_test_final(faux_marche):
    with pytest.raises(SystemExit, match="periode cachee"):
        cli.executer(["SPY", "--fin", "2020-01-01"])


def test_robustesse_interdite_sur_periode_cachee(faux_marche):
    with pytest.raises(SystemExit, match="interdit"):
        cli.executer(["SPY", "--test-final", "--robustesse"])


def test_robustesse_affiche_chaque_fenetre(faux_marche, capsys):
    assert cli.executer(["SPY", "--robustesse"]) == 0
    sortie = capsys.readouterr().out
    for n in config.FENETRES_ROBUSTESSE:
        assert f"N={n}" in sortie


def test_version_confirmation(faux_marche, capsys):
    assert cli.executer(["SPY", "--confirmation"]) == 0
    assert "Dow confirmation" in capsys.readouterr().out


def test_erreur_de_donnees_message_clair_et_code_1(tmp_path, monkeypatch, capsys):
    def panne(symbole):
        raise ConnectionError("timeout")

    monkeypatch.setattr(donnees, "telecharger_yahoo", panne)
    monkeypatch.setattr(config, "DOSSIER_DONNEES", tmp_path)
    monkeypatch.setattr("sys.argv", ["dow-backtest", "SPY"])
    with pytest.raises(SystemExit) as fin:
        cli.main()
    assert fin.value.code == 1
    assert "reessaie" in capsys.readouterr().err
