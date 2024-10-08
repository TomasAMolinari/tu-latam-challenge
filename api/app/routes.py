import sys
import os
from flask import Blueprint, jsonify, request
from shared.gcp_handler.bigquery_handler import *
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from shared.config.config import gcp_vars

bp = Blueprint('routes', __name__)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@bp.route('/records', methods=['GET'])
def get_records():
    """
    GET /records
    - Descripción: Obtiene múltiples registros de BigQuery.
    - Parámetros opcionales:
      - limit (int): Número máximo de registros a retornar (por defecto 100).
      - offset (int): Número de registros a omitir para paginación (por defecto 0).
    - Respuestas:
      - 200: Lista de registros obtenidos.
      - 500: Error al obtener registros o al procesar la solicitud.
    """
    try:
        limit = request.args.get('limit', default=100, type=int)
        offset = request.args.get('offset', default=0, type=int)

        results = fetch_records_from_bigquery(limit=limit, offset=offset)

        return jsonify(results), 200

    except Exception as e:
        logger.error(f"Error al obtener registros: {e}")
        return jsonify({"error": "Error al obtener registros"}), 500

@bp.route('/records/<id>', methods=['GET'])
def get_record_by_id(id):
    """
    GET /records/<id>
    - Descripción: Obtiene un solo registro de BigQuery basado en el ID.
    - Parámetros de ruta:
      - id (str): El identificador único del registro a recuperar.
    - Respuestas:
      - 200: Registro encontrado.
      - 404: Registro no encontrado.
      - 500: Error al obtener el registro o al procesar la solicitud.
    """
    try:
        result = fetch_single_record_from_bigquery(id)

        if result:
            return jsonify(result), 200
        else:
            return jsonify({"error": "Registro no encontrado"}), 404

    except Exception as e:
        logger.error(f"Error al obtener el registro: {e}")
        return jsonify({"error": "Error al obtener el registro"}), 500