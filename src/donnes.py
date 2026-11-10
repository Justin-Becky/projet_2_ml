import requests
from variables_secretes import CR_API_KEY
import pandas as pd
import random
import json
import pyarrow.parquet as pq

louis_tag = '#8LR9RJ99G'

player_cache_file = '../donnees/player_cache.json'
player_tags = {}

def load_cache(file):
    with open(file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_cache(file):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(player_tags, f, ensure_ascii=False, indent=2)

def player_info(player_tag: str) -> tuple:
    """
    Parameters:
    player_tag: player's clash royale tag (str)
    Return:
    player's name and winrate (tuple)
    """

    if player_tag in player_tags:
        return player_tags[player_tag]
    url = f'https://proxy.royaleapi.dev/v1/players/{player_tag.replace('#', '%23')}'
    r = requests.get(url, headers={"Authorization": f"Bearer {CR_API_KEY}"})


    player_win_rate = None

    if r.status_code == 404 or r.status_code == 525 or r.status_code == 520 or r.status_code == 503:
        player = {
            'name': 'Player A',
            'winrate': None
        }

    else:
        r.raise_for_status()
        player = r.json()
        try:
            player_win_rate = round((player['wins']/player['battleCount']), 2)
        except ZeroDivisionError:
            player_win_rate = 0.


    player_tags[player_tag] = (player['name'], player_win_rate)

    return player['name'], player_win_rate

def randomize_players(file):
    new_column_names = ['Joueur_A', 'Joueur_B', 'Date', 'game_mode', 'Joueur_A_carte_1', 'Joueur_A_carte_2', 'Joueur_A_carte_3', 'Joueur_A_carte_4', 'Joueur_A_carte_5', 'Joueur_A_carte_6', 'Joueur_A_carte_7', 'Joueur_A_carte_8', 'Joueur_B_carte_1', 'Joueur_B_carte_2', 'Joueur_B_carte_3', 'Joueur_B_carte_4', 'Joueur_B_carte_5', 'Joueur_B_carte_6', 'Joueur_B_carte_7', 'Joueur_B_carte_8', 'Joueur_A_niveau_carte_1', 'Joueur_A_niveau_carte_2', 'Joueur_A_niveau_carte_3', 'Joueur_A_niveau_carte_4', 'Joueur_A_niveau_carte_5', 'Joueur_A_niveau_carte_6', 'Joueur_A_niveau_carte_7', 'Joueur_A_niveau_carte_8', 'Joueur_B_niveau_carte_1', 'Joueur_B_niveau_carte_2', 'Joueur_B_niveau_carte_3', 'Joueur_B_niveau_carte_4', 'Joueur_B_niveau_carte_5', 'Joueur_B_niveau_carte_6', 'Joueur_B_niveau_carte_7', 'Joueur_B_niveau_carte_8']

    pq_df = pd.read_parquet(file)

    pq_df = pq_df.head(5000)

    pq_df.columns = new_column_names
    pq_df['Joueur_A_winrate'] = 0.0
    pq_df['Joueur_B_winrate'] = 0.0
    pq_df['Joueur_A_gagne'] = True

    player_a_info = ['Joueur_A']
    for i in range(1,9):
        player_a_info += [f'Joueur_A_carte_{i}', f'Joueur_A_niveau_carte_{i}']
    player_b_info = [c.replace("Joueur_A", "Joueur_B", 1) for c in player_a_info]

    for i in pq_df.index:
        roll = random.randint(0,1)
        if roll == 1:
            pq_df.at[i, 'Joueur_A_gagne'] = False
            for a, b in zip(player_a_info, player_b_info):
                pq_df.at[i, a], pq_df.at[i, b] = pq_df.at[i, b], pq_df.at[i, a]
        pq_df.loc[i, 'Joueur_A_winrate'] = player_info(pq_df.loc[i, 'Joueur_A'])[1]

        pq_df.loc[i, 'Joueur_B_winrate'] = player_info(pq_df.loc[i, 'Joueur_B'])[1]

    pq_df.to_parquet('../donnees/data_set_final.parquet')

    return pq_df


player_tags = load_cache(player_cache_file)
try:
    randomize_players('../donnees/2026-06-21_1_copy.parquet')
finally:
    save_cache(player_cache_file)