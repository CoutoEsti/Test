"""Applique les decisions aux prix, avec frais et interets, et calcule l'evolution du capital.

Decision prise a la cloture du jour t -> ordre execute a la cloture du jour t+1
-> le gain ou la perte compte a partir du jour t+2. Prudent : aucun prix du futur n'est utilise.
Quand on n'est pas investi, l'argent comptant rapporte le taux connu la veille.
"""

import pandas as pd

from dow_backtest import config

DELAI_EXECUTION = 2  # jours entre la decision et le premier rendement compte


def taux_par_jour(taux_annuel: pd.Series | None, index: pd.Index) -> pd.Series:
    """Taux du jour = taux annuel connu a la cloture de la veille / jours de bourse par an."""
    if taux_annuel is None:
        return pd.Series(0.0, index=index)
    connu = taux_annuel.reindex(taux_annuel.index.union(index)).ffill().reindex(index)
    return (connu.shift(1) / config.JOURS_BOURSE_PAR_AN).fillna(0.0)


def lancer(
    cloture: pd.Series,
    decision: pd.Series,
    frais: float = config.FRAIS_PAR_TRANSACTION,
    capital_initial: float = config.CAPITAL_INITIAL,
    debut: str | None = None,
    taux_annuel: pd.Series | None = None,
) -> pd.DataFrame:
    """Tableau jour par jour : rendement_marche, investi, frais, taux_jour, rendement, capital.

    `debut` : premier jour evalue. Les decisions peuvent utiliser l'historique d'avant
    (comme dans la vraie vie). Si on est deja investi ce jour-la, on paie l'achat d'entree.
    `taux_annuel` : interet de l'argent comptant (None = aucun interet).
    """
    decision = decision.reindex(cloture.index).fillna(0)
    jours = pd.DataFrame(index=cloture.index)
    jours["rendement_marche"] = cloture.pct_change().fillna(0.0)
    jours["investi"] = decision.shift(DELAI_EXECUTION).fillna(0).astype(int)
    # L'ordre passe a la cloture de la veille : les frais tombent ce jour-la.
    jours["frais"] = jours["investi"].diff().abs().shift(-1).fillna(0) * frais
    jours["taux_jour"] = taux_par_jour(taux_annuel, cloture.index)

    if debut is not None:
        jours = jours[jours.index >= pd.Timestamp(debut)].copy()
        if jours.empty:
            raise ValueError(f"Aucun jour a evaluer apres {debut}.")
        jours.iloc[0, jours.columns.get_loc("rendement_marche")] = 0.0
        if jours["investi"].iloc[0] == 1:  # entree au premier jour evalue
            jours.iloc[0, jours.columns.get_loc("frais")] += frais

    investi = jours["investi"]
    jours["rendement"] = (
        investi * jours["rendement_marche"] + (1 - investi) * jours["taux_jour"] - jours["frais"]
    )
    jours["capital"] = capital_initial * (1 + jours["rendement"]).cumprod()
    return jours


def acheter_et_garder(
    cloture: pd.Series,
    frais: float = config.FRAIS_PAR_TRANSACTION,
    capital_initial: float = config.CAPITAL_INITIAL,
    debut: str | None = None,
    taux_annuel: pd.Series | None = None,
) -> pd.DataFrame:
    """Reference : toujours investi, avec les memes regles d'execution, de frais et d'interet."""
    toujours = pd.Series(1, index=cloture.index)
    return lancer(cloture, toujours, frais, capital_initial, debut, taux_annuel)
