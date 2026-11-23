"""Tableau texte et graphique : strategie contre "acheter et garder"."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # pas de fenetre : on ecrit un fichier
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

LIBELLES = {
    "rendement_total": ("Rendement total", "pct"),
    "rendement_annuel": ("Rendement par an", "pct"),
    "pire_baisse": ("Pire baisse", "pct"),
    "volatilite": ("Volatilite par an", "pct"),
    "sharpe": ("Ratio de Sharpe", "nombre"),
    "transactions": ("Transactions", "entier"),
    "temps_investi": ("Temps investi", "pct"),
    "capital_final": ("Capital final ($)", "argent"),
}


def _formater(valeur, genre: str) -> str:
    if pd.isna(valeur):
        return "n/d"
    if genre == "pct":
        return f"{valeur * 100:,.1f} %"
    if genre == "entier":
        return f"{int(valeur):,}"
    if genre == "argent":
        return f"{valeur:,.0f}"
    return f"{valeur:.2f}"


def tableau(colonnes: dict[str, dict]) -> str:
    """colonnes = {"Nom de la colonne": mesures}. Renvoie un tableau texte aligne."""
    noms = list(colonnes)
    largeur = max(len(lib) for lib, _ in LIBELLES.values()) + 2
    lignes = ["".ljust(largeur) + "".join(n.rjust(18) for n in noms)]
    for cle, (libelle, genre) in LIBELLES.items():
        valeurs = "".join(_formater(colonnes[n].get(cle), genre).rjust(18) for n in noms)
        lignes.append(libelle.ljust(largeur) + valeurs)
    return "\n".join(lignes)


def graphique(courbes: dict[str, pd.DataFrame], titre: str, fichier: Path) -> Path:
    """Evolution du capital (echelle log) et periodes investies de la premiere courbe."""
    fichier.parent.mkdir(parents=True, exist_ok=True)
    fig, (haut, bas) = plt.subplots(
        2, 1, figsize=(11, 6.5), sharex=True, gridspec_kw={"height_ratios": [4, 1]}
    )
    for nom, resultat in courbes.items():
        haut.plot(resultat.index, resultat["capital"], label=nom, linewidth=1.2)
    haut.set_yscale("log")
    haut.set_ylabel("Capital ($, echelle log)")
    haut.set_title(titre)
    haut.grid(True, alpha=0.3)
    haut.legend()
    premier = next(iter(courbes.values()))
    bas.fill_between(premier.index, premier["investi"], step="post", alpha=0.5)
    bas.set_ylabel("Investi")
    bas.set_yticks([0, 1])
    bas.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(fichier, dpi=120)
    plt.close(fig)
    return fichier
