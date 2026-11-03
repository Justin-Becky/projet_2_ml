import requests
from variables_secretes import CR_API_KEY

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

    player_win_rate = (player['wins']/player['battleCount'])

    return player['name'], round(player_win_rate, 2)

print(player_info(louis_tag))