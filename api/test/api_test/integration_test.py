import os
import requests

BASE_URL = os.getenv("BASE_URL")

def test_get_all_records():
    """
    Verifica que el endpoint GET /records devuelve una lista de registros.
    """
    response = requests.get(f"{BASE_URL}/records")
    assert response.status_code == 200, f"Se esperaba un código de estado 200, pero se recibió {response.status_code}"
    
    data = response.json()
    assert isinstance(data, list), "Se esperaba que la respuesta fuera una lista"
    assert len(data) > 0, "Se esperaba al menos un registro en la respuesta"

    # verificar que cada registro contiene las claves necesarias
    claves_requeridas = {"id", "nombre", "apellido", "pais"}
    for record in data:
        assert claves_requeridas.issubset(record.keys()), f"Faltan claves en el registro: {record}"

def test_get_record_by_id():
    """
    Verifica que el endpoint GET /records/<id> devuelve el registro correcto.
    """
    record_id = "12345"
    response = requests.get(f"{BASE_URL}/records/{record_id}")
    assert response.status_code == 200, f"Se esperaba el código de estado 200, pero se obtuvo {response.status_code}"
    
    data = response.json()
    assert isinstance(data, dict), "Se esperaba que la respuesta fuera un diccionario"
    
    # Verificar que los datos del registro coinciden con lo esperado
    assert data["id"] == record_id, f"Se esperaba el ID del registro {record_id}, pero se obtuvo {data['id']}"
    assert data["nombre"] == "Juan", f"Se esperaba 'Juan' como nombre, pero se obtuvo {data['nombre']}"
    assert data["apellido"] == "Perez", f"Se esperaba 'Perez' como apellido, pero se obtuvo {data['apellido']}"
    assert data["pais"] == "Argentina", f"Se esperaba 'Argentina' como país, pero se obtuvo {data['pais']}"