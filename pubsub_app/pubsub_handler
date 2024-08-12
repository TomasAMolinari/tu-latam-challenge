import base64
import json
from bigquery_handler import insert_data

def process_pubsub_message(payload):
    try:
        if "data" not in payload:
            raise ValueError("No hay datos en el mensaje de Pub/Sub")
        
        message_data = base64.b64decode(payload["data"]).decode("utf-8")
        message_json = json.loads(message_data)
        
        insert_data(message_json)
        
    except Exception as e:
        print(f"Error al prcoesa el mensaje de Pub/Sub: {e}")
        raise
