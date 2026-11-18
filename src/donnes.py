import time
from concurrent.futures import ThreadPoolExecutor

import requests
from variables_secretes import CR_API_KEY
import pandas as pd
import random
import json
import os
from config import player_cache_file, FICHIER_FINALE

NB_LIGNES = 200000
TAILLE_LOT = 500
NB_ESSAIS = 3
CODES_TEMPORAIRES = [429, 500, 502, 504, 503, 520, 522, 525]


def load_cache(file):
    """Chaque entrée est [nom, winrate, nombre_d_echecs]."""
    if not os.path.exists(file):
        return {}
    with open(file, 'r', encoding='utf-8') as f:
        ancien_cache = json.load(f)
    cache = {}
    for tag, info in ancien_cache.items():
        introuvable = len(info) == 3 and info[2] == 404
        if info[1] is not None:
            cache[tag] = [info[0], info[1]]
        elif introuvable:
            cache[tag] = [info[0], None, 404]
    return cache

def save_cache(file):
    fichier_temp = file + ".tmp"
    with open(fichier_temp, 'w', encoding='utf-8') as f:
        json.dump(player_tags, f, ensure_ascii=False, indent=2)
    os.replace(fichier_temp, file)

def telecharger_joueur(player_tag: str):
    url = f'https://proxy.royaleapi.dev/v1/players/{player_tag.replace('#', '%23')}'
    for essai in range(NB_ESSAIS):
        try:
            r = requests.get(url, headers={"Authorization": f"Bearer {CR_API_KEY}"}, timeout=15)
        except (requests.ConnectionError, requests.Timeout):
            time.sleep(2 ** essai)
            continue

        if r.status_code == 404:
            return ["nom_inconnu", None, 404]
        if r.status_code in CODES_TEMPORAIRES:
            time.sleep(2 ** essai)
            continue

        r.raise_for_status()
        player = r.json()
        try:
            player_win_rate = round((player['wins']/player['battleCount']), 2)
        except ZeroDivisionError:
            player_win_rate = 0.

        return [player["name"], player_win_rate]

    return None

def player_info(player_tag: str) -> tuple:
    """
    Parameters:
    player_tag: player's clash royale tag (str)
    Return:
    player's name and winrate (tuple)
    """

    if player_tag not in player_tags:
        info = telecharger_joueur(player_tag)
        if info is None:
            return "nom_inconnu", None
        player_tags[player_tag] = info

    return player_tags[player_tag][0], player_tags[player_tag][1]

def telecharger_joueurs(tags):
    joueurs_manquants = [tag for tag in tags if tag not in player_tags]
    print(f"{len(tags)} joueurs uniques, {len(joueurs_manquants)} joueurs à téléchargé.")

    # Merci claude
    with ThreadPoolExecutor(8) as executor:
        for debut in range(0, len(joueurs_manquants), TAILLE_LOT):
            lot = joueurs_manquants[debut:debut + TAILLE_LOT]
            list(executor.map(player_info, lot))  # une liste pourquoi ?
            save_cache(player_cache_file)
            print(f"{debut + len(lot)}/{len(joueurs_manquants)}")

def randomize_players(file):
    new_column_names = [
                        'Joueur_A', 'Joueur_B', 'Date', 'game_mode', 'Joueur_A_carte_1', 'Joueur_A_carte_2',
                        'Joueur_A_carte_3', 'Joueur_A_carte_4', 'Joueur_A_carte_5', 'Joueur_A_carte_6',
                        'Joueur_A_carte_7', 'Joueur_A_carte_8', 'Joueur_B_carte_1', 'Joueur_B_carte_2',
                        'Joueur_B_carte_3', 'Joueur_B_carte_4', 'Joueur_B_carte_5', 'Joueur_B_carte_6',
                        'Joueur_B_carte_7', 'Joueur_B_carte_8', 'Joueur_A_niveau_carte_1', 'Joueur_A_niveau_carte_2',
                        'Joueur_A_niveau_carte_3', 'Joueur_A_niveau_carte_4', 'Joueur_A_niveau_carte_5',
                        'Joueur_A_niveau_carte_6', 'Joueur_A_niveau_carte_7', 'Joueur_A_niveau_carte_8',
                        'Joueur_B_niveau_carte_1', 'Joueur_B_niveau_carte_2', 'Joueur_B_niveau_carte_3',
                        'Joueur_B_niveau_carte_4', 'Joueur_B_niveau_carte_5', 'Joueur_B_niveau_carte_6',
                        'Joueur_B_niveau_carte_7', 'Joueur_B_niveau_carte_8'
                        ]

    pq_df = pd.read_parquet(file).head(NB_LIGNES)
    pq_df.columns = new_column_names

    player_a_info = ['Joueur_A']
    for i in range(1, 9):
        player_a_info += [f'Joueur_A_carte_{i}', f'Joueur_A_niveau_carte_{i}']
    player_b_info = [c.replace("Joueur_A", "Joueur_B", 1) for c in player_a_info]

    tags = pd.unique(pq_df[['Joueur_A', 'Joueur_B']].to_numpy().ravel())  # Claude quel goat on sauve du temps
    telecharger_joueurs(tags)

    for compteur, i in enumerate(pq_df.index):
        pq_df.at[i, 'Joueur_A_gagne'] = True
        roll = random.randint(0, 1)
        if roll == 1:
            pq_df.at[i, 'Joueur_A_gagne'] = False
            for a, b in zip(player_a_info, player_b_info):
                pq_df.at[i, a], pq_df.at[i, b] = pq_df.at[i, b], pq_df.at[i, a]
        pq_df.loc[i, 'Joueur_A_winrate'] = player_info(pq_df.loc[i, 'Joueur_A'])[1]

        pq_df.loc[i, 'Joueur_B_winrate'] = player_info(pq_df.loc[i, 'Joueur_B'])[1]

    pq_df.to_parquet(FICHIER_FINALE)

    return pq_df


player_tags = load_cache(player_cache_file)  # un dict
