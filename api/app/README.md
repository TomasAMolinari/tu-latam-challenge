# HTTP API

La aplicación está diseñada para buscar información de BigQuery y exponerla via REST API. Para ejecutarla se recomienda hacerlo con Docker, pero puede hacerse mediante Python directamente.

## Prerequisitos 
1. Instalar Python3
2. Instalar virtualenv
3. Docker (opcional)
4. Copiar el archivo de credenciales `gcp-terraform-creds.json` usado en `/terraform` al directorio `api/config`.
5. Modificar los valores de `gcp_vars_example.json` en `api/config` con los valores reales del proyecto de GCP y renombrar a `gcp_vars.json`.

## Ejecutar la aplicación localmente (en Linux)
1. Crear el *virtual enviroment*
```sh
python -m venv </path/to/new/virtual/environment>
```

2. Activar el `venv`
```sh
source </path/to/new/virtual/environment>/Scripts/activate 
```

3. Intallar los requerimientos:
```sh
pip install -r requirements.txt
```

4. Setear la variable de entorno `FLASK_SECRET_KEY` para Flask.
```sh
FLASK_SECRET_KEY=<flask_secret_key>
```

5. Ejecutar la aplicación
```sh
python run.py
```

## Ejecutar la aplicación con Docker

1. Buildear la imágen

```sh
docker build -t tu-latam-challenge-api .
```

2. Correr la aplicación

```sh
docker run -p 8080:8080 -e FLASK_SECRET_KEY=<flask_secret_key> tu-latam-challenge-api
```