import os
from PySide6.QtWidgets import QApplication

from modele import RegressionLineaire
from donnes import randomize_players, save_cache, player_cache_file
from interface import MainWindow
from config import FICHIER_DONNEES, FICHIER_FINALE

if not os.path.exists(FICHIER_FINALE):
    if os.path.exists(FICHIER_DONNEES):
        try:
            randomize_players(FICHIER_DONNEES)
        finally:
            save_cache(player_cache_file)
    else:
        raise FileNotFoundError("télécharger les parquets et metter les dans donnees")

for nb_ligne in [5000, 20000, 100000, 200000]:
    modele = RegressionLineaire.charger_ou_entrainer(f"regression_{nb_ligne}", nb_ligne, forcer=False)

app = QApplication()
main_window = MainWindow()
main_window.showMaximized()
app.exec()

