"""Commande `dow-backtest` : telecharge, applique la Dow Theory, compare, fait le rapport."""

import argparse
import sys
from datetime import date

import pandas as pd

from dow_backtest import backtest, config, donnees, mesures, rapport, strategie, transactions
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
        "--risque",
        type=float,
        default=config.RISQUE_PAR_TRANSACTION,
        help="$ de perte prevue par transaction si le stop (dernier creux) est touche",
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
    p.add_argument(
        "--sans-interet",
        action="store_true",
        help="L'argent comptant ne rapporte rien (par defaut : taux des bons du Tresor)",
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


def _taux(args, fin):
    """Taux de l'argent comptant, ou None si --sans-interet."""
    return None if args.sans_interet else donnees.charger_taux(fin, args.rafraichir)


def _robustesse(args, cloture, debut, fin, taux):
    lignes = {}
    for n in config.FENETRES_ROBUSTESSE:
        decision = _decision(args, cloture, n, fin)
        res = backtest.lancer(cloture, decision, args.frais, debut=debut, taux_annuel=taux)
        lignes[f"N={n}"] = mesures.calculer(res)
    ref_brut = backtest.acheter_et_garder(cloture, args.frais, debut=debut, taux_annuel=taux)
    ref = mesures.calculer(ref_brut)
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
    taux = _taux(args, fin)

    if args.robustesse:
        _robustesse(args, cloture, debut, fin, taux)
        return 0

    nom = "Dow confirmation" if args.confirmation else f"Dow (N={args.fenetre})"
    decision = _decision(args, cloture, args.fenetre, fin)
    strat = backtest.lancer(cloture, decision, args.frais, debut=debut, taux_annuel=taux)
    ref = backtest.acheter_et_garder(cloture, args.frais, debut=debut, taux_annuel=taux)
    debut_reel = strat.index[0].date()
    fin_reelle = strat.index[-1].date()

    interet = "sans interet" if args.sans_interet else f"interet {config.SYMBOLE_TAUX}"
    frais = f"frais {args.frais * 100:.2f} %"
    print(f"{args.symbole} du {debut_reel} au {fin_reelle}, {frais}, {interet}\n")
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

    stops = strategie.niveaux(cloture, args.fenetre)["l1"]
    liste = transactions.extraire(cloture, strat, stops, args.frais, args.risque)
    print("\n" + transactions.texte(transactions.statistiques(liste, args.risque)))
    fichier_transactions = config.DOSSIER_RAPPORTS / f"{base}_transactions.csv"
    liste.to_csv(fichier_transactions, index=False)

    print(f"\nGraphique : {image}")
    print(f"Transactions : {fichier_transactions}")
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
