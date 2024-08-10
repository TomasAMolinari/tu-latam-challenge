import sys
import os
from google.cloud import bigquery
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from config.config import credentials, gcp_vars

project_id = gcp_vars['project_id']

client = bigquery.Client(credentials=credentials, project=project_id)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def execute_query(query):
    """
    Ejecuta una consulta SQL en BigQuery y devuelve los resultados como una lista de diccionarios.
    :param query: Consulta SQL a ejecutar
    :return: Lista de diccionarios con los resultados de la consulta
    """
    try:
        
        query_job = client.query(query)
        results = query_job.result()

        # Convertir los resultados a una lista de diccionarios
        data = []
        for row in results:
            data.append(dict(row))

        return data

    except Exception as e:
        logger.error(f"Error al ejecutar la consulta en BigQuery: {e}")
        raise

def fetch_data_from_bigquery():
    """
    Ejecuta una consulta SQL para obtener datos desde BigQuery.
    :return: Lista de diccionarios con las primeras 100 filas de la tabla
    """
    query = """
    SELECT id, nombre, apellido, pais
    FROM `tu-latam-challenge.analytics_dataset.analytics_table`
    LIMIT 100
    """
    
    return execute_query(query)

def insert_data(dataset_name, table_name, rows_to_insert):
    """
    Inserta datos en una tabla de BigQuery.
    :param dataset_id: ID del dataset de BigQuery
    :param table_id: ID de la tabla de BigQuery
    :param rows_to_insert: Lista de diccionarios representando las filas a insertar
    :return: Resultado de la operación de inserción
    """
    try:
        table_ref = client.dataset(dataset_name).table(table_name)
        table = client.get_table(table_ref)

        # verifica que el dato a insertar es un solo diccionario y lo convierte en una lista de diccionarios
        # bigquery espera este tipo de datos
        if isinstance(rows_to_insert, dict):
            rows_to_insert = [rows_to_insert]  # envolver en una lista si es un solo diccionario

        errors = client.insert_rows_json(table, rows_to_insert)

        if errors:
            logger.error(f"Errores al insertar datos en BigQuery: {errors}")
            return {"status": "error", "errors": errors}

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Error al insertar datos en BigQuery: {e}")
        raise
