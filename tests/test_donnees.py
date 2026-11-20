"""
Tests sur le jeu de données lui-même : ils vérifient les critères de l'énoncé (section 2)
et nos propres choix de préparation, pas le code.
"""
from config import CARTES

CARTES_A = [f"Joueur_A_carte_{i}" for i in range(1, 9)]
CARTES_B = [f"Joueur_B_carte_{i}" for i in range(1, 9)]
NIVEAUX = [f"Joueur_{j}_niveau_carte_{i}" for j in ("A", "B") for i in range(1, 9)]
WINRATES = ["Joueur_A_winrate", "Joueur_B_winrate"]

def test_colonnes_attendues(donnees):
    """Cas usuel : 16 cartes, 16 niveaux, 2 winrates et la cible."""
    for colonne in CARTES_A + CARTES_B + NIVEAUX + WINRATES + ["Joueur_A_gagne"]:
        assert colonne in donnees.columns


def test_taille_minimale(donnees):
    """Critère de l'énoncé : au moins 500 lignes (le maximum de 50 000 a été levé par le professeur)."""
    assert len(donnees) >= 500


def test_cible_equilibree(donnees):
    """
    Le mélange au hasard de A et B (randomize_players) doit donner environ 50 % de victoires de A.
    C'est ce qui justifie l'exactitude comme métrique.
    """
    assert 0.45 < donnees["Joueur_A_gagne"].mean() < 0.55


def test_valeurs_dans_les_bornes(donnees):
    """Cas limites : après le retrait des valeurs manquantes, niveaux entre 1 et 16 et winrates entre 0 et 1."""
    propres = donnees.dropna()
    assert propres[NIVEAUX].min().min() >= 1
    assert propres[NIVEAUX].max().max() <= 16
    assert propres[WINRATES].min().min() >= 0
    assert propres[WINRATES].max().max() <= 1


def test_toutes_les_cartes_existent_dans_l_interface(donnees):
    """Chaque numéro de carte des données doit exister dans config.CARTES, sinon l'interface n'a pas d'image."""
    numeros_connus = set(CARTES.values())
    numeros_donnees = set(donnees[CARTES_A + CARTES_B].stack().unique())
    assert numeros_donnees <= numeros_connus
