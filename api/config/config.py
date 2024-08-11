import json
import os
from google.oauth2 import service_account

# ruta al archivo de credenciales
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), 'gcp-terraform-creds.json')

# cargar las credenciales
credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)

# cargar configuración de variables de GCP
with open(os.path.join(os.path.dirname(__file__), 'gcp_vars.json'), 'r') as config_file:
    gcp_vars = json.load(config_file)

# configuración para Flask
class flask_config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
    DEBUG = True