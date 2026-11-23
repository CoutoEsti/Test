"""SEUL endroit qui parle a Yahoo Finance. Telecharge, nettoie et garde une copie locale."""

import os
import re
from collections.abc import Callable
from pathlib import Path

import pandas as pd

from dow_backtest import config

COLONNES = ["Open", "High", "Low", "Close", "Volume"]


class ErreurDonnees(Exception):
    """Probleme de donnees, avec un message lisible pour l'utilisateur."""


def telecharger_yahoo(symbole: str) -> pd.DataFrame:
    """Tout l'historique journalier, ajuste pour les dividendes et les splits."""
    import yfinance as yf

    return yf.download(
        symbole,
        period="max",
        interval="1d",
        auto_adjust=True,
        progress=False,
        multi_level_index=False,
        timeout=30,
    )


def nettoyer(brut: pd.DataFrame, symbole: str) -> pd.DataFrame:
    """Colonnes standard, dates triees, sans doublon ni prix invalide."""
    if brut is None or brut.empty:
        raise ErreurDonnees(f"Aucune donnee recue pour {symbole}. Symbole inconnu ?")
    df = brut.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    manquantes = [c for c in COLONNES if c not in df.columns]
    if manquantes:
        raise ErreurDonnees(f"Colonnes manquantes pour {symbole} : {manquantes}")
    df = df[COLONNES]
    df.index = pd.to_datetime(df.index)
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)
    df.index = df.index.normalize()
    df.index.name = "Date"
    df = df[~df.index.duplicated(keep="last")].sort_index()
    df = df.dropna(subset=["Close"])
    if df.empty:
        raise ErreurDonnees(f"Aucun prix de cloture valide pour {symbole}.")
    if (df["Close"] <= 0).any():
        raise ErreurDonnees(f"Prix negatif ou nul dans les donnees de {symbole}.")
    return df


def fichier_cache(symbole: str, dossier: Path) -> Path:
    return dossier / (re.sub(r"[^A-Za-z0-9]", "_", symbole) + ".csv")


def _ecrire_tout_ou_rien(df: pd.DataFrame, fichier: Path) -> None:
    """Ecrit dans un fichier temporaire puis le renomme : jamais de fichier a moitie ecrit."""
    fichier.parent.mkdir(parents=True, exist_ok=True)
    temporaire = fichier.with_suffix(".tmp")
    df.to_csv(temporaire)
    os.replace(temporaire, fichier)


def charger(
    symbole: str,
    debut: str | None = None,
    fin: str | None = None,
    dossier: Path | None = None,
    source: Callable[[str], pd.DataFrame] | None = None,
    rafraichir: bool = False,
) -> pd.DataFrame:
    """Prix journaliers de `symbole` entre `debut` et `fin` (inclus).

    Utilise la copie locale si elle existe. `rafraichir=True` force un nouveau telechargement.
    """
    dossier = dossier if dossier is not None else config.DOSSIER_DONNEES
    source = source if source is not None else telecharger_yahoo
    fichier = fichier_cache(symbole, dossier)
    if fichier.exists() and not rafraichir:
        try:
            df = pd.read_csv(fichier, index_col="Date", parse_dates=True)
            df = nettoyer(df, symbole)
        except (ValueError, KeyError, ErreurDonnees) as e:
            raise ErreurDonnees(
                f"Copie locale illisible : {fichier}. Relance avec --rafraichir. ({e})"
            ) from e
    else:
        try:
            brut = source(symbole)
        except Exception as e:  # Yahoo peut echouer de mille facons
            raise ErreurDonnees(
                f"Telechargement de {symbole} impossible ({e}). "
                "Verifie ta connexion et reessaie dans quelques minutes."
            ) from e
        df = nettoyer(brut, symbole)
        _ecrire_tout_ou_rien(df, fichier)

    resultat = df.loc[debut:fin]
    if resultat.empty:
        raise ErreurDonnees(
            f"Aucune donnee pour {symbole} entre {debut} et {fin}. "
            f"Donnees disponibles : {df.index[0].date()} a {df.index[-1].date()}."
        )
    return resultat
