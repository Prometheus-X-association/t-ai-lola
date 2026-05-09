'''
Description main.py
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

from Exchanger import Exchanger
from Importer import Importer
from LRSFeeder import LRSFeeder
from dotenv import load_dotenv

# Configuration du logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
# Chargement des variables d'environnement depuis le fichier .env
if os.path.exists('.env'):
    load_dotenv('.env')
elif os.path.exists('../.env'):
    load_dotenv('../.env')
else:
    logging.warning("No .env found!")
try:
    if os.getenv('EXCHANGE_MODE', False).lower() == 'true':
        #Activation du PDC
        logging.info("Starting the data exchange process...")
        exchanger = Exchanger()
        exchanger.login()
        exchanger.reload()
        exchanger.process_exchange()
        logging.info("Data exchange process completed successfully.")
    if os.getenv('IMPORT_MODE', False).lower() == 'true':
        #Activation de l'import
        logging.info("Starting the data import process...")
        importer = Importer()
        importer.login()
        data = importer.load()
        logging.info("Data import process completed successfully.")
    if os.getenv('FEED_MODE', False).lower() == 'true':
        #Activation LRS
        logging.info("Sending statements to LRS...")
        feeder = LRSFeeder()
        feeder.send()
        logging.info("LRS feeded successfully.")
except Exception as e:
    logging.error(f"An error occurred: {e}")
    exit(1)
