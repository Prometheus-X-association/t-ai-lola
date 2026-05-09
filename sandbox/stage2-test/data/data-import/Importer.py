'''
Description Importer.py
Projet : step2
@author: azim
@copyright:  2025 LORIA/Université de Lorraine. All rights reserved.
@license: GNU General Public License, Version 3
@version: 1.0
@email:  azim.roussanaly@loria.fr
@date: 28/06/2025
'''
import logging
import os
import requests

class Importer:
    def __init__(self):
        self.host = os.getenv('RECEIVER_HOST')
        self.user = os.getenv('RECEIVER_USER')
        self.password = os.getenv('RECEIVER_PASSWORD')
        self.dir = os.getenv('RECEIVER_DATA_DIR')
        os.makedirs(self.dir, exist_ok=True)
        self.filename = os.getenv('RECEIVER_DATA_FILENAME')
        self.token = None
        if not all([self.host, self.user, self.password, self.dir, self.filename]):
            logging.error("Environment variables RECEIVER_* must be set.")
            raise ValueError("Environment variables RECEIVER_* must be set.")

    def login(self):
        url = self.host + "/login"
        headers = {"Content-Type": "application/json"}
        credentials = {"service_key": self.user, "secret_key": self.password}
        try:
            # Envoi de la requête POST
            response = requests.post(url, json=credentials, headers=headers)
            # Vérification du statut de la réponse
            if response.status_code == 200:
                self.token = response.json().get("token")
                return self.token
            else:
                logging.error(f"Erreur : {response.status_code} - {response.text}")
        except requests.RequestException as e:
            logging.error(f"Error in /login (credentials error) : {e}")
            raise e

    def save(self, data):
        filepath = os.path.join(self.dir, self.filename)
        try:
            import json
            with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            logging.info(f"Data saved in :  {filepath}")
        except Exception as e:
            logging.warning(f"Error in {filepath} : {e}")

    def load(self):
        url = self.host + '/get'
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        try:
            # Envoi de la requête GET
            response = requests.get(url, headers=headers)
            # Vérification du statut de la réponse
            if response.status_code == 200:
                logging.info(f"Data are imported successfully from {url}")
                self.save(response.json())
                return response.json()
            else:
                logging.error(f"Error : {response.status_code} - {response.text}")
        except requests.RequestException as e:
            logging.error(f"Error in /get : {e}")
            raise e
