import os
from PySide6.QtWidgets import QApplication

from modele import RegressionLineaire
from donnes import randomize_players, save_cache, player_cache_file, fichier_final
from interface import MainWindow

FICHIER_BRUT = os.path.join("..", "donnees", "2026-06-21_1.parquet")

if not os.path.exists(fichier_final):
    if os.path.exists(FICHIER_BRUT):
        try:
            randomize_players(FICHIER_BRUT)
        finally:
            save_cache(player_cache_file)
    else:
        raise FileNotFoundError("télécharger les parquets et metter les dans donnees")

for nb_ligne in [5000, 20000, 100000, 200000]:
    modele = RegressionLineaire.charger_ou_entrainer(f"regression_{nb_ligne}", nb_ligne, forcer=False)

app = QApplication()
main_window = MainWindow()
main_window.show()
app.exec()

