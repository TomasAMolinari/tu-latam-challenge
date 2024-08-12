import sys
import os
from google.cloud import bigquery
from google.oauth2 import service_account
from faker import Faker

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from shared.config.config import credentials, gcp_vars

project_id = gcp_vars['project_id']
dataset_name = gcp_vars['bigquery']['dataset_name']
table_name = gcp_vars['bigquery']['table_name']

client = bigquery.Client(credentials=credentials, project=project_id)

table_ref = client.dataset(dataset_name).table(table_name)

faker = Faker()

rows_to_insert = []

for _ in range(200):
    row = {
        "id": faker.uuid4(),               # ID único
        "nombre": faker.first_name(),      # Nombre 
        "apellido": faker.last_name(),     # Apellido
        "pais": faker.country()            # País
    }
    rows_to_insert.append(row)

errors = client.insert_rows_json(table_ref, rows_to_insert)

if errors == []:
    print("Todos los datos fueron insertados correctamente.")
else:
    print("Se encontraron errores al insertar los datos: {}".format(errors))
