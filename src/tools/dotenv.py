
from dotenv import load_dotenv
import os

# Charger les variables du fichier .env
load_dotenv()

# Vérifier que PYTHONPATH est bien chargé
print(f"PYTHONPATH: {os.getenv('PYTHONPATH')}")