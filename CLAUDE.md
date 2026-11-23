# dow-backtest

IMPORTANT - Section ecrite par l'utilisateur. Ne jamais la modifier, la reformuler ou la deplacer.
User pas programmeur. Il ne relit pas le code : Claude verifie a sa place.
Phrases courtes, une idee par phrase. Technique permis, mais vulgariser apres.
Prioriser faire le projet.
Pas de flatterie. Corriger les erreurs directement.
Ne pas changer une bonne reponse parce que l'utilisateur insiste.

## Projet
- Niveau : LEGER
- Type : outil Python en ligne de commande
- But : tester si la Dow Theory bat "acheter et garder" sur l'historique, frais inclus
- Techno : Python 3.12+, uv, pandas, numpy, yfinance, matplotlib, pytest, ruff
- Ordi de travail : Windows (Claude travaille aussi dans le cloud Linux)
- Donnees : Yahoo Finance via yfinance, copie locale dans data/ (hors git)
- Deploiement : aucun, roule en local
- Budget mensuel : 0 $. Aucun service payant sans accord de l'utilisateur.
- Periode cachee : 2016 a aujourd'hui. Jamais regardee sans demande explicite (--test-final).
- Structure et decisions : docs/structure.md (a jour a chaque changement)
- Suivi : docs/A-faire.md, docs/Fait.md

## Commandes
- Installer : uv sync
- Lancer : uv run dow-backtest SPY
- Tests : uv run pytest
- Linter / formateur : uv run ruff check . && uv run ruff format .

## Garde-fous automatiques (ne pas contourner)
- .claude/hooks/garde_fou.py bloque tout commit si les tests ratent ou si un secret est detecte.
- Commit bloque : lire le message, corriger la cause. Jamais --no-verify, jamais desactiver le hook.

## Regles
1. Reutiliser avant de creer. Chercher si ca existe deja. Si oui, reutiliser, jamais une variante a cote.
   Meme chose ecrite 2 fois = s'arreter et proposer un element commun.
2. Une seule source. Reglages dans src/dow_backtest/config.py. Yahoo seulement via donnees.py.
   Les autres modules passent par ces couches, jamais directement.
3. Ne rien supprimer ni changer sans demande. Comportement bizarre possiblement voulu : le signaler.
   Rien au-dela de la demande. Pas de refactoring autour d'un bug. Ne pas toucher a ml/.
4. Demander, ne pas deviner. Valeur par defaut, techno, plugin, tache risquee : "voici ce que je ferais, OK ?".
   Aucun plugin ni librairie ajoute sans dire pourquoi, son cout, sa licence, et verifier qu'il existe.
5. Preuve avant "fini". Avant de construire : ecrire en 2-3 lignes ce qui prouve que ca marche.
   Toute nouvelle regle recoit son test. Toute regle de strategie recoit un test anti-triche (futur).
   Montrer la preuve (sortie des tests, capture). Etape non testee : le dire tel quel.
6. Pannes. Message clair + Reessayer, jamais un ecran vide ou un 0 qui cache l'erreur.
   Operation en plusieurs etapes : tout ou rien, jamais a moitie faite.
7. Petits morceaux. Un changement a la fois, commit entre chaque, sur une branche.
   Fusion dans la principale seulement sur le go de l'utilisateur.
8. Expliquer apres chaque changement : ce qui a change (2-3 phrases) et ce que l'utilisateur peut verifier.
9. Angles morts. Sujet donnees, securite, argent, comptes, couts, deploiement : utiliser le skill angles-morts.
   Reponse notee dans docs/structure.md.
10. Audits. Lire A-faire.md et Fait.md avant. Ne pas resignaler ce qui est "voulu" ou "ecarte".

## Sortie
- Reponse d'abord. Pas de preambule. Ne pas reformuler la demande.
- Code : la solution la plus simple qui marche. Pas d'abstraction a usage unique.
- Typographie ASCII : pas de tiret long, pas de guillemets courbes.

Les instructions de l'utilisateur ecrasent ce fichier.
