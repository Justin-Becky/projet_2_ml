import requests
from variables_secretes import CR_API_KEY
import pandas as pd
import donnees

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
    player_tags = []
    pq_df = pd.read_parquet(file)
    for row in pq_df.iterrows():
        player_tags.append(row[0])
    print(player_tags[0])



    randomized_df = pd.DataFrame(
        {
            'player_A_tag',
            'player_B_tag',
            'player_A_winrate',
            'player_B_winrate',
            'player_A_card_0',
            'player_A_card_1',
            'player_A_card_2',
            'player_A_card_3',
            'player_A_card_4',
            'player_A_card_5',
            'player_A_card_6',
            'player_A_card_7',
            'player_B_card_0',
            'player_B_card_1',
            'player_B_card_2',
            'player_B_card_3',
            'player_B_card_4',
            'player_B_card_5',
            'player_B_card_6',
            'player_B_card_7',
            'player_A_card_0_level',
            'player_A_card_1_level',
            'player_A_card_2_level',
            'player_A_card_3_level',
            'player_A_card_4_level',
            'player_A_card_5_level',
            'player_A_card_6_level',
            'player_A_card_7_level',
            'player_B_card_0_level',
            'player_B_card_1_level',
            'player_B_card_2_level',
            'player_B_card_3_level',
            'player_B_card_4_level',
            'player_B_card_5_level',
            'player_B_card_6_level',
            'player_B_card_7_level',
        }
    )

randomize_players('../donnees/2026-06-21_1.parquet')
print(player_info(louis_tag))