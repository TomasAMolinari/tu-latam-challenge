import json
import os
from google.oauth2 import service_account

print("---------------------------Ruta de ejecución:---------------------------", os.path.dirname(__file__))  # Verifica la ruta desde donde se está intentando abrir el archivo

# ruta al archivo de credenciales
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), 'gcp-terraform-creds.json')

# cargar las credenciales
credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_FILE)

# cargar configuración de variables de GCP
with open(os.path.join(os.path.dirname(__file__), 'gcp_vars.json'), 'r') as config_file:
    gcp_vars = json.load(config_file)

# configuración para Flask
class flask_config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
    DEBUG = True