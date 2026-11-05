import requests
from variables_secretes import CR_API_KEY
import pandas as pd
import random
import pyarrow.parquet as pq

louis_tag = '#8LR9RJ99G'

def player_info(player_tag: str) -> tuple:
    """
    Parameters:
    player_tag: player's clash royale tag (str)
    Return:
    player's name and winrate (tuple)
    """
    url = f'https://proxy.royaleapi.dev/v1/players/{player_tag.replace('#', '%23')}'
    r = requests.get(url, headers={"Authorization": f"Bearer {CR_API_KEY}"})
    r.raise_for_status()

    player = r.json()
    try:
        player_win_rate = (player['wins']/player['battleCount'])
    except ValueError('Battle Count invalide: division par 0'):
        player_win_rate = 0

    return player['name'], round(player_win_rate, 2)

def randomize_players(file):
    new_column_names = ['Joueur_A', 'Joueur_B', 'Date', 'game_mode', 'Joueur_A_carte_1', 'Joueur_A_carte_2',
                        'Joueur_A_carte_3', 'Joueur_A_carte_4', 'Joueur_A_carte_5', 'Joueur_A_carte_6',
                        'Joueur_A_carte_7', 'Joueur_A_carte_8', 'Joueur_B_carte_1', 'Joueur_B_carte_2',
                        'Joueur_B_carte_3', 'Joueur_B_carte_4', 'Joueur_B_carte_5', 'Joueur_B_carte_6',
                        'Joueur_B_carte_7', 'Joueur_B_carte_8', 'Joueur_A_niveau_carte_1', 'Joueur_A_niveau_carte_2',
                        'Joueur_A_niveau_carte_3', 'Joueur_A_niveau_carte_4', 'Joueur_A_niveau_carte_5',
                        'Joueur_A_niveau_carte_6', 'Joueur_A_niveau_carte_7', 'Joueur_A_niveau_carte_8',
                        'Joueur_B_niveau_carte_1', 'Joueur_B_niveau_carte_2', 'Joueur_B_niveau_carte_3',
                        'Joueur_B_niveau_carte_4', 'Joueur_B_niveau_carte_5', 'Joueur_B_niveau_carte_6',
                        'Joueur_B_niveau_carte_7', 'Joueur_B_niveau_carte_8']

    pq_df = pd.read_parquet(file)

    pq_df.columns = new_column_names
    pq_df['Joueur_A_winrate'] = 0
    pq_df['Joueur_B_winrate'] = 0
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
        try:
            pq_df.loc[i, 'Joueur_A_winrate'] = player_info(pq_df.loc[i, 'Joueur_A'])[1]
        except:
            pq_df.loc[i, 'Joueur_A_winrate'] = -1
        try:
            pq_df.loc[i, 'Joueur_B_winrate'] = player_info(pq_df.loc[i, 'Joueur_B'])[1]
        except:
            pq_df.loc[i, 'Joueur_B_winrate'] = -1

    pq_df.to_parquet(file)

    return pq_df




randomize_players('../donnees/2026-06-21_1_copy.parquet')

print(player_info(louis_tag))