import os
import sys
import json
from google.cloud import pubsub_v1
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from shared.config.config import credentials,gcp_vars
from shared.gcp_handler.bigquery_handler import insert_data


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("Logger configurado correctamente y listo para usar.")

project_id = gcp_vars['project_id']
subscription_id = gcp_vars['pubsub']['subscription_id']
dataset_name = gcp_vars['bigquery']['dataset_name']
table_name = gcp_vars['bigquery']['table_name']

subscriber = pubsub_v1.SubscriberClient(credentials=credentials)

def callback(message):
    """
    Inserta los datos en BigQuery si son válidos.
    :param data: Diccionario con los datos a insertar
    """
    data = json.loads(message.data.decode("utf-8"))

    # validar campos obligatorios
    required_fields = ['id', 'nombre', 'apellido', 'pais']
    if all(field in data for field in required_fields):
        try:
            # insertar datos en bigquery
            insert_data(dataset_name,table_name,data)
            message.ack()
            logger.info(f"Mensaje procesado y confirmado: {data}")

        except Exception as e:
            message.nack()
            logger.error(f"Error al procesar el mensaje: {e}")
    else:
        message.nack()
        logger.error("Los datos no contienen todas las columnas requeridas. Inserción cancelada.")

def listen_for_messages():
    """
    Escucha mensajes de la suscripción de Pub/Sub y ejecuta un callback al recibir uno.
    """
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    # suscribirse al tópico
    logger.info(f"Escuchando mensajes en {subscription_path}...")
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    try:
        streaming_pull_future.result()
    except KeyboardInterrupt:
        streaming_pull_future.cancel()