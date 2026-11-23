"""Commande `dow-backtest` : telecharge, applique la Dow Theory, compare, fait le rapport."""

import argparse
import sys
from datetime import date

import pandas as pd

from dow_backtest import backtest, config, donnees, mesures, rapport, strategie
from dow_backtest.donnees import ErreurDonnees


def _arguments(argv):
    p = argparse.ArgumentParser(
        prog="dow-backtest",
        description="Teste la Dow Theory sur l'historique et la compare a 'acheter et garder'.",
    )
    p.add_argument("symbole", nargs="?", default=config.SYMBOLE_DEFAUT, help="ex: SPY")
    p.add_argument("--debut", default=None, help="AAAA-MM-JJ (defaut : debut du developpement)")
    p.add_argument("--fin", default=None, help="AAAA-MM-JJ (defaut : fin du developpement)")
    p.add_argument("--fenetre", type=int, default=config.FENETRE_PIVOT, help="N jours (pivots)")
    p.add_argument(
        "--frais",
        type=float,
        default=config.FRAIS_PAR_TRANSACTION,
        help="ex: 0.001 = 0,1 %% par transaction",
    )
    p.add_argument(
        "--confirmation",
        action="store_true",
        help="Version 2 : signaux des Dow Jones industrielles + transports",
    )
    p.add_argument(
        "--robustesse",
        action="store_true",
        help="Compare plusieurs fenetres (periode de developpement seulement)",
    )
    p.add_argument(
        "--test-final",
        action="store_true",
        help="Periode cachee (2016 a aujourd'hui). A faire UNE seule fois.",
    )
    p.add_argument("--rafraichir", action="store_true", help="Re-telecharge les donnees")
    return p.parse_args(argv)


def _periode(args):
    """Choisit la periode et protege la periode cachee."""
    if args.test_final:
        if args.robustesse:
            sys.exit("Erreur : --robustesse est interdit sur la periode cachee (surajustement).")
        return args.debut or config.DEBUT_TEST_FINAL, args.fin or date.today().isoformat()
    debut = args.debut or config.DEBUT_DEVELOPPEMENT
    fin = args.fin or config.FIN_DEVELOPPEMENT
    if pd.Timestamp(fin) >= pd.Timestamp(config.DEBUT_TEST_FINAL):
        sys.exit(
            f"Erreur : la periode demandee touche la periode cachee (a partir de "
            f"{config.DEBUT_TEST_FINAL}). Ajoute --test-final si c'est voulu."
        )
    return debut, fin


def _decision(args, cloture, fenetre, fin):
    """Decision jour par jour (1 = investi), calculee seulement avec les donnees jusqu'a `fin`."""
    if not args.confirmation:
        return strategie.etat_tendance(cloture, fenetre)
    etats = []
    for indice in config.INDICES_DOW:
        prix = donnees.charger(indice, fin=fin, rafraichir=args.rafraichir)["Close"]
        etats.append(strategie.etat_tendance(prix, fenetre))
    combine = strategie.confirmation(*etats)
    # Jours ou l'indice n'a pas de prix : on garde la derniere decision connue.
    return combine.reindex(cloture.index, method="ffill").fillna(0)


def _robustesse(args, cloture, debut, fin):
    lignes = {}
    for n in config.FENETRES_ROBUSTESSE:
        res = backtest.lancer(cloture, _decision(args, cloture, n, fin), args.frais, debut=debut)
        lignes[f"N={n}"] = mesures.calculer(res)
    ref = mesures.calculer(backtest.acheter_et_garder(cloture, args.frais, debut=debut))
    lignes["Acheter-garder"] = ref
    print(f"\nRobustesse {args.symbole} {debut} -> {fin}\n")
    print(rapport.tableau(lignes))


def executer(argv=None) -> int:
    args = _arguments(argv)
    debut, fin = _periode(args)
    if args.test_final:
        print("ATTENTION : periode cachee. Le resultat ne compte que si c'est la premiere fois.")
        print("Ne change plus aucun reglage apres l'avoir vu.\n")

    # On charge l'historique jusqu'a `fin` (rien apres) : la strategie ne voit pas le futur.
    prix = donnees.charger(args.symbole, fin=fin, rafraichir=args.rafraichir)
    cloture = prix["Close"]

    if args.robustesse:
        _robustesse(args, cloture, debut, fin)
        return 0

    nom = "Dow confirmation" if args.confirmation else f"Dow (N={args.fenetre})"
    decision = _decision(args, cloture, args.fenetre, fin)
    strat = backtest.lancer(cloture, decision, args.frais, debut=debut)
    ref = backtest.acheter_et_garder(cloture, args.frais, debut=debut)
    debut_reel = strat.index[0].date()
    fin_reelle = strat.index[-1].date()

    print(f"{args.symbole} du {debut_reel} au {fin_reelle}, frais {args.frais * 100:.2f} %\n")
    print(rapport.tableau({nom: mesures.calculer(strat), "Acheter-garder": mesures.calculer(ref)}))

    suffixe = "confirmation" if args.confirmation else f"N{args.fenetre}"
    nom_symbole = donnees.fichier_cache(args.symbole, config.DOSSIER_RAPPORTS).stem
    base = f"{nom_symbole}_{debut_reel}_{fin_reelle}_{suffixe}"
    image = rapport.graphique(
        {nom: strat, "Acheter-garder": ref},
        f"{args.symbole} : {nom} contre acheter-garder",
        config.DOSSIER_RAPPORTS / f"{base}.png",
    )
    strat.to_csv(config.DOSSIER_RAPPORTS / f"{base}.csv")
    print(f"\nGraphique : {image}")
    print(f"Detail jour par jour : {config.DOSSIER_RAPPORTS / (base + '.csv')}")
    return 0


def main() -> None:
    try:
        sys.exit(executer())
    except ErreurDonnees as e:
        print(f"Erreur de donnees : {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
