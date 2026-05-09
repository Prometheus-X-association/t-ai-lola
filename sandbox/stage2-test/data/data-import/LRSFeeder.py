'''
Description LRSFeeder.py
Projet : step2
@author: azim
@copyright:  2025 LORIA/Université de Lorraine. All rights reserved.
@license: GNU General Public License, Version 3
@version: 1.0
@email:  azim.roussanaly@loria.fr
@date: 29/06/2025
'''
import logging
import os
import json
import requests

class LRSFeeder:
    '''
    A class to handle sending statements to a Learning Record Store (LRS).
    '''
    def __init__(self):
        self.host = os.getenv('APP_URL')
        self.basic = os.getenv('TRAX_B64')
        self.endpoint = os.getenv('TRAX_ENDPOINT')
        self.json_file = os.path.join(os.getenv('RECEIVER_DATA_DIR'), os.getenv('RECEIVER_DATA_FILENAME'))
        if not all([self.host, self.basic, self.endpoint]):
            logging.error("Environment variables TRAX* must be set.")
            raise ValueError("Environment variables TRAX* must be set.")

    def send(self):
        try:
            with open(self.json_file, 'r', encoding='utf-8') as file:
                json_data = json.load(file)
        except Exception as e:
            logging.error(f"Error reading JSON file {self.json_file}: {e}")
            raise e
        try:
            # Charger les données JSON si elles sont sous forme de chaîne
            if isinstance(json_data, str):
                data = json.loads(json_data)
            else:
                data = json_data
            # Vérifier que les données contiennent une liste
            if not isinstance(data, list):
                raise ValueError("Wrong statements list in json file")
            # Parcourir chaque élément de la liste et appliquer le traitement
            for item in data:
                self.post(item)
        except Exception as e:
            print(f"Une erreur s'est produite : {e}")

    def post(self, statement):
        try:
            url = self.host + self.endpoint
            headers = {
                "X-Experience-API-Version": "1.0.3",
                "Content-Type": "application/json",
                "Authorization": f"Basic {self.basic}"
            }
            # Envoi de la requête POST
            response = requests.post(url, json=statement, headers=headers)
            # Vérification du statut de la réponse
            if not response.status_code == 200:
                logging.warning(f"Error {response.status_code} for statement :{statement} :  - {response.text}")
        except requests.RequestException as e:
            logging.error(f"An error occurred while sending the statement {statement} : {e}")

