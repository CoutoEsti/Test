"""Applique les decisions aux prix, avec frais, et calcule l'evolution du capital.

Decision prise a la cloture du jour t -> ordre execute a la cloture du jour t+1
-> le gain ou la perte compte a partir du jour t+2. Prudent : aucun prix du futur n'est utilise.
"""

import pandas as pd

from dow_backtest import config

DELAI_EXECUTION = 2  # jours entre la decision et le premier rendement compte


def lancer(
    cloture: pd.Series,
    decision: pd.Series,
    frais: float = config.FRAIS_PAR_TRANSACTION,
    capital_initial: float = config.CAPITAL_INITIAL,
    debut: str | None = None,
) -> pd.DataFrame:
    """Tableau jour par jour : rendement_marche, investi, frais, rendement, capital.

    `debut` : premier jour evalue. Les decisions peuvent utiliser l'historique d'avant
    (comme dans la vraie vie). Si on est deja investi ce jour-la, on paie l'achat d'entree.
    """
    decision = decision.reindex(cloture.index).fillna(0)
    rendement_marche = cloture.pct_change().fillna(0.0)
    investi = decision.shift(DELAI_EXECUTION).fillna(0).astype(int)
    # L'ordre passe a la cloture de la veille : les frais tombent ce jour-la (veille du rendement).
    changement = investi.diff().abs().shift(-1).fillna(0)
    cout = changement * frais
    rendement = investi * rendement_marche - cout
    if debut is not None:
        garder = cloture.index >= pd.Timestamp(debut)
        rendement_marche, investi, cout, rendement = (
            x[garder] for x in (rendement_marche, investi, cout, rendement)
        )
        if rendement.empty:
            raise ValueError(f"Aucun jour a evaluer apres {debut}.")
        rendement_marche = rendement_marche.copy()
        rendement_marche.iloc[0] = 0.0
        rendement = (investi * rendement_marche - cout).copy()
        if investi.iloc[0] == 1:  # entree au premier jour evalue
            rendement.iloc[0] -= frais
            cout = cout.copy()
            cout.iloc[0] += frais
    capital = capital_initial * (1 + rendement).cumprod()
    return pd.DataFrame(
        {
            "rendement_marche": rendement_marche,
            "investi": investi,
            "frais": cout,
            "rendement": rendement,
            "capital": capital,
        }
    )


def acheter_et_garder(
    cloture: pd.Series,
    frais: float = config.FRAIS_PAR_TRANSACTION,
    capital_initial: float = config.CAPITAL_INITIAL,
    debut: str | None = None,
) -> pd.DataFrame:
    """Reference : toujours investi, avec les memes regles d'execution et de frais."""
    toujours = pd.Series(1, index=cloture.index)
    return lancer(cloture, toujours, frais, capital_initial, debut)
