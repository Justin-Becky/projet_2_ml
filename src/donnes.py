import os
import requests
from variables_secretes import CR_API_KEY

player_tag = '#8LR9RJ99G'

url = f'https://api.clashroyale.com/v1/players/{player_tag.replace('#', '%23')}'
r = requests.get(url, headers={"Authorization": f"Bearer {CR_API_KEY}"})
r.raise_for_status()
#print(r.status_code)
#print(r.text)

joueur = r.json()
print(joueur["name"], joueur["trophies"], joueur["wins"], joueur["losses"])