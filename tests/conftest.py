import os

import pandas as pd
import pytest

from config import FICHIER_FINALE
from modele import RegressionLineaire

# Assez de parties pour un modèle réaliste, assez peu pour que les tests restent rapides
NB_LIGNES_TEST = 5000


@pytest.fixture(scope="session")
def donnees() -> pd.DataFrame:
    """
    Le vrai jeu de données (donnees/data_set_final.parquet), lu une seule fois pour tous les tests.
    Échoue avec un message clair si le fichier n'a pas été poussé dans le dépôt.
    """
    if not os.path.exists(FICHIER_FINALE):
        pytest.fail(f"Jeu de données introuvable : {FICHIER_FINALE}. Il doit être dans le dépôt.")
    return pd.read_parquet(FICHIER_FINALE)


@pytest.fixture(scope="session")
def modele_entraine(donnees) -> RegressionLineaire:
    """Un modèle entraîné une seule fois sur les 5000 premières parties du vrai jeu de données."""
    modele = RegressionLineaire("modele_test", NB_LIGNES_TEST)
    modele.train(FICHIER_FINALE)
    return modele


@pytest.fixture
def dossier_modeles_temporaire(tmp_path, monkeypatch) -> str:
    """
    Remplace le dossier des modèles par un dossier temporaire vide pendant un test :
    les tests n'écrivent jamais dans le vrai dossier modeles/ et ne dépendent pas de ce qu'il contient.
    """
    import modele
    monkeypatch.setattr(modele, "dossier_modeles", str(tmp_path))
    return str(tmp_path)


@pytest.fixture
def deck_valide(modele_entraine) -> tuple[list[int], list[int]]:
    """8 cartes connues du modèle et 8 niveaux valides."""
    return modele_entraine.cartes_connues[:8], [11] * 8
