# HTTP API

La aplicación está diseñada para escuchar los mensajes de la suscripción del tópico de Pub/Sub, e insertarlos en la base de datos de BigQuery. Para ejecutarla se recomienda hacerlo con Docker, pero puede hacerse mediante Python directamente.

## Prerequisitos 
1. Instalar Python3
2. Instalar virtualenv
3. Docker (opcional)
4. Copiar el archivo de credenciales `gcp-cred.json` usado en `/terraform` al directorio `shared/config`.
5. Modificar los valores de `gcp_vars_example.json` en `shared/config` con los valores reales del proyecto de GCP y renombrar a `gcp_vars.json`.

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

5. Ejecutar la aplicación
```sh
python run.py
```

## Ejecutar la aplicación con Docker

1. Buildear la imágen desde la raiz del proyecto
```sh
docker build -f dockerfiles/Dockerfile.pubsub -t tu-latam-challenge-pubsub .
```

2. Correr la aplicación

```sh
docker run -p 5000:5000  tu-latam-challenge-pubsub
```