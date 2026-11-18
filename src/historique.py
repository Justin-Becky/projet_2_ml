import csv
import os
from datetime import datetime
from config import FICHIER_HISTORIQUE, COLONNES_HISTORIQUE

def creer_entree(nom_modele: str, winrate_a: float, cartes_a: list[int], niveaux_a: list[int],
                 winrate_b: float, cartes_b: list[int], niveaux_b: list[int], proba_a: float) -> dict:
    """
    Construit une ligne d'historique à partir d'une prédiction.

    Les listes de cartes et de niveaux sont transformées en texte ("1 2 3 ...") pour tenir dans une case du CSV.
    Renvoie un dict dont les clés sont COLONNES_HISTORIQUE.
    """
    return {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "modele": nom_modele,
        "winrate_a": winrate_a,
        "winrate_b": winrate_b,
        "cartes_a": " ".join(str(c) for c in cartes_a),
        "niveaux_a": " ".join(str(n) for n in niveaux_a),
        "cartes_b": " ".join(str(c) for c in cartes_b),
        "niveaux_b": " ".join(str(n) for n in niveaux_b),
        "proba_a": round(proba_a, 4),
        "favori": "Joueur A" if proba_a >= 0.5 else "Joueur B",
    }


def ajouter_prediction(entree: dict, fichier: str = FICHIER_HISTORIQUE) -> None:
    """
    Ajoute une ligne à la fin du fichier CSV d'historique.

    Crée le fichier (avec la ligne d'en-tête) s'il n'existe pas encore.
    """
    fichier_existe = os.path.exists(fichier)
    os.makedirs(os.path.dirname(fichier), exist_ok=True)
    with open(fichier, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLONNES_HISTORIQUE)
        if not fichier_existe:
            writer.writeheader()
        writer.writerow(entree)


def lire_historique(fichier: str = FICHIER_HISTORIQUE) -> list[dict]:
    """
    Lit tout l'historique.

    Renvoie une liste de dict (une par prédiction), la plus récente en premier.
    Renvoie une liste vide si le fichier n'existe pas encore.
    """
    if not os.path.exists(fichier):
        return []
    with open(fichier, newline="", encoding="utf-8") as f:
        lignes = list(csv.DictReader(f))
    # Les lignes sont ajoutées à la fin du fichier : on inverse pour avoir la plus récente en premier
    return lignes[::-1]
