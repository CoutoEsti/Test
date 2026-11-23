---
name: angles-morts
description: Checklist des sujets qu'un non-programmeur oublie (securite, donnees, sauvegardes, argent, couts, dependances, documentation). Utiliser avant de construire une partie qui touche ces sujets, et avant de brancher un courtier ou de l'argent reel.
---

# Angles morts
Pour chaque point lie a la tache en cours :
- Reponse deja dans docs/structure.md : l'appliquer.
- Sinon : poser UNE question courte avec une recommandation. Noter la reponse dans docs/structure.md.
- Point inutile pour ce projet : noter "pas necessaire" + raison.
Projet de niveau LEGER : seuls les points utiles sont gardes ici.

## Securite
- Secrets hors du code et hors de git (cle de courtier ou d'API : variable d'environnement, fichier .env ignore)

## Donnees
- Sauvegardes : frequence, duree de conservation. Restauration TESTEE au moins une fois
- Donnees de marche : ajustees (dividendes, splits) ? Trous, doublons, jours feries ?
- Biais du futur : aucune decision ne doit utiliser un prix posterieur a sa date
- Biais du survivant : tester des actions encore cotees aujourd'hui gonfle les resultats

## Utilisation
- Argent, dates, fuseaux : arrondis, devise, fuseau de reference
- Performance : tester avec beaucoup de donnees (25 000 lignes, pas 10)

## Vie du projet
- Retour a la version precedente en un geste
- Formateur, linter et tests automatiques a chaque envoi (CI)
- Dependances : licences OK ? (eviter AGPL si le code est partage)
- Documentation : toi dans 6 mois comprends le projet

## Avant tout argent reel (pas prevu pour l'instant)
- Simulation en direct ("paper trading") plusieurs mois avant
- Limite de perte, taille de position, que faire si le programme plante en pleine journee
- Impots et declarations selon le pays
