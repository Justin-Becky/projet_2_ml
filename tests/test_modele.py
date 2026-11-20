import json
import os

import pytest
from exceptions import DonneeInvalideError, ModeleIntrouvableError, ProjetError
from modele import RegressionLineaire, lire_metadonnees, lister_modeles

# ---------- entraînement ----------

def test_train_garde_les_bonnes_colonnes(modele_entraine):
    """Cas usuel : 16 cartes + 16 niveaux + 2 winrates, sans la cible ni les tags des joueurs."""
    assert len(modele_entraine.colonnes) == 34
    assert "Joueur_A_gagne" not in modele_entraine.colonnes
    assert "Joueur_A" not in modele_entraine.colonnes
    assert "Joueur_A_winrate" in modele_entraine.colonnes


def test_score_meilleur_que_le_hasard(modele_entraine):
    """Cas usuel : le modèle doit faire mieux que 50 %, sans être parfait
    (100 % voudrait dire une fuite de la cible)."""
    assert 0.5 < modele_entraine.score < 1.0


def test_train_fichier_absent_leve_une_erreur(tmp_path):
    """Cas d'erreur : le jeu de données n'existe pas."""
    modele = RegressionLineaire("absent", 100)
    with pytest.raises(FileNotFoundError):
        modele.train(str(tmp_path / "inexistant.parquet"))


# ---------- prédiction et validation des saisies ----------

def test_predict_renvoie_une_probabilite(modele_entraine, deck_valide):
    """Cas usuel : la prédiction est un float entre 0 et 1."""
    cartes, niveaux = deck_valide
    proba = modele_entraine.predict(0.6, cartes, niveaux, 0.4, cartes, niveaux)
    assert isinstance(proba, float)
    assert 0.0 <= proba <= 1.0


def test_predict_le_joueur_le_plus_fort_est_favori(modele_entraine, deck_valide):
    """Cas usuel : A avec de meilleurs niveaux et un meilleur winrate doit être favori, et l'inverse."""
    cartes, _ = deck_valide
    a_fort = modele_entraine.predict(0.75, cartes, [16] * 8, 0.35, cartes, [8] * 8)
    a_faible = modele_entraine.predict(0.35, cartes, [8] * 8, 0.75, cartes, [16] * 8)
    assert a_fort > 0.5 > a_faible


def test_bornes_acceptees(modele_entraine, deck_valide):
    """Cas limites : un winrate de 0 ou 1 et des niveaux de 1 ou 16 sont valides (aucune erreur)."""
    cartes, _ = deck_valide
    modele_entraine.valider_joueur(0.0, cartes, [1] * 8)
    modele_entraine.valider_joueur(1.0, cartes, [16] * 8)


@pytest.mark.parametrize("winrate, nb_cartes, niveau", [
    (1.01, 8, 11),  # winrate juste au-dessus de 100 %
    (-0.01, 8, 11),  # winrate négatif
    (0.5, 7, 11),  # deck incomplet
    (0.5, 8, 0),  # niveau sous 1
    (0.5, 8, 17),  # niveau au-dessus de 16
])
def test_saisies_invalides_levent_donnee_invalide(modele_entraine, deck_valide, winrate, nb_cartes, niveau):
    """Cas d'erreur : chaque saisie invalide lève DonneeInvalideError (jamais un plantage)."""
    cartes, _ = deck_valide
    with pytest.raises(DonneeInvalideError):
        modele_entraine.valider_joueur(winrate, cartes[:nb_cartes], [niveau] * nb_cartes)


def test_carte_inconnue_leve_donnee_invalide(modele_entraine, deck_valide):
    """Cas d'erreur : une carte jamais vue à l'entraînement est refusée."""
    cartes, niveaux = deck_valide
    with pytest.raises(DonneeInvalideError):
        modele_entraine.predict(0.5, cartes[:7] + [999], niveaux, 0.5, cartes, niveaux)


# ---------- sauvegarde, chargement et métadonnées ----------

def test_sauvegarde_puis_chargement_donne_la_meme_prediction(modele_entraine, deck_valide,
                                                            dossier_modeles_temporaire):
    """Cas usuel : un modèle rechargé depuis le .joblib prédit exactement la même chose."""
    cartes, niveaux = deck_valide
    fichier = modele_entraine.save_model()
    recharge = RegressionLineaire.load(fichier)

    avant = modele_entraine.predict(0.6, cartes, niveaux, 0.4, cartes, niveaux)
    apres = recharge.predict(0.6, cartes, niveaux, 0.4, cartes, niveaux)
    assert apres == pytest.approx(avant)


def test_metadonnees_json_contient_les_bonnes_informations(modele_entraine, dossier_modeles_temporaire):
    """Cas usuel : le JSON contient ce que l'énoncé demande et le score correspond au modèle."""
    modele_entraine.save_model()
    with open(os.path.join(dossier_modeles_temporaire, "modele_test.json"), encoding="utf-8") as f:
        meta = json.load(f)

    for cle in ("colonnes", "categorielles", "numeriques", "score"):
        assert cle in meta
    assert meta["numeriques"]["niveau"] == [1, 16]
    assert meta["score"] == pytest.approx(modele_entraine.score)
    assert lire_metadonnees("modele_test") == meta


def test_charger_modele_absent_leve_modele_introuvable(tmp_path):
    """Cas d'erreur : charger un .joblib qui n'existe pas."""
    with pytest.raises(ModeleIntrouvableError):
        RegressionLineaire.load(str(tmp_path / "absent.joblib"))


def test_modele_introuvable_est_aussi_une_erreur_du_projet_et_de_fichier():
    """La hiérarchie d'exceptions : un except ProjetError ou FileNotFoundError l'attrape."""
    assert issubclass(ModeleIntrouvableError, ProjetError)
    assert issubclass(ModeleIntrouvableError, FileNotFoundError)


def test_lire_metadonnees_absentes_leve_une_erreur(dossier_modeles_temporaire):
    """Cas d'erreur : le JSON d'un modèle n'existe pas."""
    with pytest.raises(FileNotFoundError):
        lire_metadonnees("absent")


def test_lister_modeles_trie_par_nombre_de_lignes(dossier_modeles_temporaire):
    """Cas usuel : regression_5000 doit venir avant regression_20000 (tri par longueur puis par nom)."""
    for nom in ("regression_20000", "regression_5000", "regression_200000"):
        open(os.path.join(dossier_modeles_temporaire, nom + ".json"), "w").close()
    assert lister_modeles() == ["regression_5000", "regression_20000", "regression_200000"]


def test_lister_modeles_dossier_vide(dossier_modeles_temporaire):
    """Cas limite : aucun modèle sauvegardé."""
    assert lister_modeles() == []


def test_str_et_repr(modele_entraine):
    """Méthodes spéciales : __str__ pour un humain, __repr__ pour déboguer."""
    assert "modele_test" in str(modele_entraine)
    assert "%" in str(modele_entraine)
    assert repr(modele_entraine).startswith("RegressionLineaire(")
