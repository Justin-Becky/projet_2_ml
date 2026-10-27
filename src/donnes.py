import os
import requests

player_tag = '#8LR9RJ99G'
API_KEY = 'w'

url = f"https://api.clashroyale.com/v1/players/{player_tag.replace('#', '%23')}"
r = requests.get(url, headers={"Authorization": f"Bearer {API_KEY}"})
#r.raise_for_status()

joueur = r.json()
print(joueur["name"], joueur["trophies"], joueur["wins"], joueur["losses"])