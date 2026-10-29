### Request 1
name: Tests
on: [push]

jobs:
test:
runs-on: ubuntu-latest
steps:
- uses: actions/checkout@v7
- uses: actions/setup-python@v7
with:
    python-version: "3.14"
- run: pip install -r requirements.txt
- run: python -m pytest -v
peux tu m'expliquer ligne par ligne se que se code fait

### Request 2
Peux-tu faire la structure du README.md pour un projet "x" respectant ces consignes :
le fichier du projet (Projet INF1007 — De la donnée à l'application)

### Request 3
Explain the process to getting information from clash royal api

### Request 4
can you help me create a variable that i will not push on pycharm
