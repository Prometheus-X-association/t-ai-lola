'''
Description Exchanger.py
Projet : data-import
@author: azim
@copyright:  2025 LORIA/Université de Lorraine. All rights reserved.
@license: GNU General Public License, Version 3
@version: 1.0
@email:  azim.roussanaly@loria.fr
@date: 26/05/2025
'''
import json
import os
import requests
import logging

class Exchanger:
    def __init__(self):
        self.token = None
        self.refresh_token = None
        # Chargement de la configuration
        self.host = os.getenv("PDC_HOST")
        self.service_key = os.getenv("SERVICE_KEY")
        self.secret_key = os.getenv("SECRET_KEY")
        self.contract = os.getenv("CONTRACT")
        self.purpose = os.getenv("PURPOSE_ID")
        self.resource = os.getenv("RESOURCE_ID")
        if not all([self.host, self.service_key, self.secret_key, self.contract, self.purpose, self.resource]):
            logging.error(f"Error:  at least one parameter missed {e}. Check .env file")
            raise ValueError("At least, one parameter missed")
        logging.info("Parameters loaded successfully from environment variables")

    def login(self):
        url = self.host + "/login"
        headers = {"Content-Type": "application/json"}
        data = {"secretKey": self.secret_key, "serviceKey": self.service_key}
        try:
            # Ajout de la trace de la requête dans le fichier de log
            logging.info(f"Requête POST envoyée à {url} avec les données: {data}")
            response = requests.post(url, json=data, headers=headers)
            if response.status_code != 200:
                logging.error(f"Erreur lors de la connexion: {response.status_code} - {response.text}")
                raise Exception(f"Erreur lors de la connexion: {response.status_code} - {response.text}")
            response_data = response.json()
            # Extraire le contenu brut et le convertir en JSON
            rep = response.content.decode('utf-8')  # Décodage en chaîne de caractères
            content = json.loads(rep).get("content")  # Conversion en dictionnaire JSON
            self.token = content.get("token")
            self.refresh_token = content.get("refreshToken")
            return response_data
        except Exception as e:
            logging.error(f"Une erreur s'est produite: {e}")
            raise e

    def reload(self):
        url = self.host + "/private/configuration/reload"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        try:
            # Ajout de la trace de la requête dans le fichier de log
            logging.info(f"Requête POST envoyée à {url} avec les headers: {headers}")
            response = requests.post(url, headers=headers)
            if response.status_code != 200:
                logging.error(
                    f"Erreur lors du rechargement de la configuration: {response.status_code} - {response.text}")
                raise Exception(
                    f"Erreur lors du rechargement de la configuration: {response.status_code} - {response.text}")
            logging.info(f"Configuration rechargée avec succès: {response.text}")
            return response.json()
        except Exception as e:
            logging.error(f"Une erreur s'est produite lors du rechargement de la configuration: {e}")
            raise e

    def process_exchange(self):
        url = self.host + "/consumer/exchange"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        data = {
            "contract": self.contract,
            "purposeId": self.purpose,
            "resourceId": self.resource
        }
        try:
            response = requests.post(url, json=data, headers=headers)
            logging.info(
                f"Requête POST envoyée à {url} avec les headers:{headers} et les données: {data}")
            response_data = response.json()
            if response.status_code != 200:
                response_data = json.loads(response_data) if isinstance(response_data, str) else response_data
                if not response_data.get("content", {}).get("success", True):
                    raise Exception(response_data.get("content").get("message"))
            return response_data
        except Exception as e:
            logging.error(f"Une erreur s'est produite : {e}")
            raise e


# Exemple d'utilisation
if __name__ == '__main__':
    try:
        exchanger = Exchanger()
        result = exchanger.login()
        print("Token:", exchanger.token)
        print("Refresh Token:", exchanger.refresh_token)
        print(exchanger.process_exchange())
    except Exception as e:
        print(f"Erreur: {e}")
