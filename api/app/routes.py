import sys
import os
from flask import Blueprint, jsonify, request
from .bigquery_handler import fetch_data_from_bigquery, insert_data
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from config.config import gcp_vars

bp = Blueprint('routes', __name__)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@bp.route('/data', methods=['GET'])
def get_data():
    """
    GET /data
    - Descripción: Obtiene datos desde BigQuery.
    - Respuestas:
      - 200: Retorna JSON con los datos.
      - 500: Error al obtener datos.
    """
    try:
        
        data = fetch_data_from_bigquery()
        return jsonify(data), 200

    except Exception as e:
        logger.error(f"Error al obtener datos: {e}")
        return jsonify({"error": "Error al obtener datos"}), 500

@bp.route('/add', methods=['POST'])
def add_data():
    """
    POST /insert
    - Descripción: Agrega nuevas filas a la tabla de BigQuery.
    - Parámetros: JSON con 'id', 'nombre', 'apellido', 'pais'.
    - Respuestas:
      - 201: Datos agregados.
      - 400: Datos incompletos.
      - 500: Error al insertar datos o al procesar la solicitud.
    """
    try:
        data = request.get_json()

        # validar campos obligatorios
        required_fields = ['id', 'nombre', 'apellido', 'pais']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Datos incompletos"}), 400

        dataset_name = gcp_vars['bigquery']['dataset_name']
        table_name = gcp_vars['bigquery']['table_name']

        result = insert_data(dataset_name, table_name, data)

        if result['status'] == 'error':
            return jsonify({"error": "Error al insertar datos"}), 500

        return jsonify({"message": "Datos procesados exitosamente"}), 200

    except Exception as e:
        logger.error(f"Error al procesar datos: {e}")
        return jsonify({"error": "Error al procesar datos"}), 500