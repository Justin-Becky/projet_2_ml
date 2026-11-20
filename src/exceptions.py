class ProjetError(Exception):
    """Classe parente de toutes les exceptions du projet : un seul except ProjetError les attrape toutes."""


class DonneeInvalideError(ProjetError):
    """Une saisie ou une donnée n'est pas valide (deck incomplet, winrate ou niveau hors bornes, carte inconnue)."""


class ModeleIntrouvableError(ProjetError, FileNotFoundError):
    """
    Le fichier d'un modèle (.joblib) ou de ses métadonnées (.json) n'existe pas.
    Hérite aussi de FileNotFoundError : un except FileNotFoundError existant l'attrape encore.
    """