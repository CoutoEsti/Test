"""Garde-fou avant commit : bloque si les tests ratent ou si un secret est detecte.
Code de sortie 2 = commit bloque. 0 = commit autorise."""
import re
import subprocess
import sys
from pathlib import Path

# A remplir a la creation du projet. Vide = commit bloque.
COMMANDE_TESTS = "uv run ruff check . && uv run pytest"

# Racine du projet : tout est lance d'ici, peu importe le dossier courant.
RACINE = Path(__file__).resolve().parents[2]

FICHIERS_INTERDITS = re.compile(r"(^|/)(\.env(\..*)?|.*\.pem|.*\.key|id_rsa.*)$", re.I)
MOTIFS_SECRETS = [
    re.compile(r"sk-ant-[A-Za-z0-9_-]{10,}"),           # cle Anthropic
    re.compile(r"sk-[A-Za-z0-9]{20,}"),                 # cle style OpenAI
    re.compile(r"AKIA[0-9A-Z]{16}"),                    # cle AWS
    re.compile(r"ghp_[A-Za-z0-9]{30,}"),                # jeton GitHub
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),  # cle privee
    re.compile(r"(?i)(password|passwd|secret|api_key|token)\s*[:=]\s*['\"][^'\"]{6,}['\"]"),
]


def bloquer(message):
    print(message, file=sys.stderr)
    sys.exit(2)


def git(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=RACINE)
    return r.stdout


def verifier_secrets():
    fichiers = [f for f in git("diff", "--cached", "--name-only").splitlines() if f]
    interdits = [f for f in fichiers if FICHIERS_INTERDITS.search(f)]
    if interdits:
        bloquer("Commit bloque : fichier secret prepare pour git : " + ", ".join(interdits)
                + ". Le retirer (git rm --cached NOM) et l'ajouter au .gitignore.")
    ajouts = [l[1:] for l in git("diff", "--cached", "-U0").splitlines()
              if l.startswith("+") and not l.startswith("+++")]
    for ligne in ajouts:
        for motif in MOTIFS_SECRETS:
            if motif.search(ligne):
                bloquer("Commit bloque : secret probable dans le code : " + ligne.strip()[:80]
                        + ". Le mettre dans une variable d'environnement.")


def verifier_tests():
    if not COMMANDE_TESTS:
        bloquer("Commit bloque : COMMANDE_TESTS est vide dans .claude/hooks/garde_fou.py. "
                "La remplir avec la commande de tests du projet.")
    r = subprocess.run(COMMANDE_TESTS, shell=True, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=RACINE)
    if r.returncode != 0:
        fin = (r.stdout + r.stderr)[-1500:]
        bloquer("Commit bloque : les tests ratent.\n" + fin)


if __name__ == "__main__":
    sys.stdin.read()  # Claude Code envoie des infos ici. On n'en a pas besoin.
    verifier_secrets()
    verifier_tests()
    sys.exit(0)
