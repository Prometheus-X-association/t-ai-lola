'''
Description send_data_to_receiver.py
Projet : step2
@author: azim
@copyright:  2025 LORIA/Université de Lorraine. All rights reserved.
@license: GNU General Public License, Version 3
@version: 1.0
@email:  azim.roussanaly@loria.fr
@date: 28/06/2025
'''
import json

JSON_FILE = "../dataJson/oulad-data.json"
URL = "http://loria.ovh:8081/post"
TOKEN ="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzZXJ2aWNlX2tleSI6ImF6aW0ifQ._CMXo2uhqxXnvzrQF6QC_7BCkfa3jknxBPjd7_jN5do"
import requests

def send_xapi_statement():
    headers = {
        "X-Experience-API-Version": "1.0.3",
        "Content-Type": "application/json",
        #"Authorization": f"Bearer {TOKEN}"
    }
    try:
        # Chargement des données JSON depuis le fichier
        with open(JSON_FILE, 'r', encoding='utf-8') as file:
             data = file.read()
        if isinstance(data, str):
             data = json.loads(data)
    except:
        print('Erreur lors de la lecture du fichier JSON')
    try:
        response = requests.post(URL, json=data, headers=headers)
        if response.status_code == 200:
            print("Requête réussie :", response.json())
        else:
            print(f"Erreur : {response.status_code} - {response.text}")
    except requests.RequestException as e:
        print(f"Une erreur s'est produite : {e}")

# Appel de la fonction
send_xapi_statement()