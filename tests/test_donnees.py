import pandas as pd
import pytest
from conftest import prix_complets, serie

from dow_backtest import donnees
from dow_backtest.donnees import ErreurDonnees


def faux_yahoo(compteur=None):
    def source(symbole):
        if compteur is not None:
            compteur.append(symbole)
        return prix_complets(serie(range(100, 130)))

    return source


def test_nettoyer_aplatit_trie_et_retire_doublons():
    brut = prix_complets(serie([10, 11, 12]))
    brut = pd.concat([brut.iloc[[2]], brut, brut.iloc[[1]]])  # desordre + doublons
    brut.columns = pd.MultiIndex.from_product([brut.columns, ["SPY"]])
    brut.index = brut.index.tz_localize("America/New_York")
    propre = donnees.nettoyer(brut, "SPY")
    assert list(propre.columns) == donnees.COLONNES
    assert propre.index.is_monotonic_increasing
    assert not propre.index.duplicated().any()
    assert propre.index.tz is None
    assert list(propre["Close"]) == [10, 11, 12]


def test_nettoyer_retire_les_clotures_vides():
    brut = prix_complets(serie([10, 11, 12]))
    brut.iloc[1, brut.columns.get_loc("Close")] = float("nan")
    assert len(donnees.nettoyer(brut, "X")) == 2


@pytest.mark.parametrize(
    "brut",
    [
        pd.DataFrame(),
        prix_complets(serie([10, -1, 12])),
        prix_complets(serie([10, 11])).drop(columns=["Volume"]),
    ],
    ids=["vide", "prix-negatif", "colonne-manquante"],
)
def test_nettoyer_refuse_les_donnees_invalides(brut):
    with pytest.raises(ErreurDonnees):
        donnees.nettoyer(brut, "X")


def test_charger_utilise_la_copie_locale_au_deuxieme_appel(tmp_path):
    appels = []
    premier = donnees.charger("SPY", dossier=tmp_path, source=faux_yahoo(appels))

    def internet_coupe(symbole):
        raise ConnectionError("pas d'Internet")

    second = donnees.charger("SPY", dossier=tmp_path, source=internet_coupe)
    assert appels == ["SPY"]
    pd.testing.assert_frame_equal(premier, second, check_freq=False)
    assert not list(tmp_path.glob("*.tmp"))  # ecriture tout ou rien


def test_rafraichir_retelecharge(tmp_path):
    appels = []
    donnees.charger("SPY", dossier=tmp_path, source=faux_yahoo(appels))
    donnees.charger("SPY", dossier=tmp_path, source=faux_yahoo(appels), rafraichir=True)
    assert appels == ["SPY", "SPY"]


def test_panne_de_telechargement_donne_un_message_clair(tmp_path):
    def panne(symbole):
        raise ConnectionError("timeout")

    with pytest.raises(ErreurDonnees, match="reessaie"):
        donnees.charger("SPY", dossier=tmp_path, source=panne)
    assert not list(tmp_path.iterdir())  # rien d'ecrit a moitie


def test_charger_filtre_les_dates(tmp_path):
    df = donnees.charger("SPY", "2000-01-05", "2000-01-10", dossier=tmp_path, source=faux_yahoo())
    assert df.index[0] == pd.Timestamp("2000-01-05")
    assert df.index[-1] == pd.Timestamp("2000-01-10")


def test_periode_sans_donnees_est_une_erreur_claire(tmp_path):
    with pytest.raises(ErreurDonnees, match="disponibles"):
        donnees.charger("SPY", "1990-01-01", "1990-12-31", dossier=tmp_path, source=faux_yahoo())


def test_copie_locale_corrompue(tmp_path):
    donnees.charger("SPY", dossier=tmp_path, source=faux_yahoo())
    donnees.fichier_cache("SPY", tmp_path).write_text("n'importe quoi")
    with pytest.raises(ErreurDonnees, match="--rafraichir"):
        donnees.charger("SPY", dossier=tmp_path, source=faux_yahoo())


def test_nom_de_fichier_sans_caractere_special(tmp_path):
    assert donnees.fichier_cache("^DJI", tmp_path).name == "_DJI.csv"
