# LATAM Challenge DevSecOps/SRE

## Contexto
Se requiere un sistema para ingestar y almacenar datos en una DB con la finalidad de hacer
analítica avanzada. Posteriormente, los datos almacenados deben ser expuestos mediante
una API HTTP para que puedan ser consumidos por terceros.

## Objetivo
Desarrollar un sistema en la nube para ingestar, almacenar y exponer datos mediante el uso
de IaC y despliegue con flujos CI/CD. Hacer pruebas de calidad, monitoreo y alertas para
asegurar y monitorear la salud del sistema.

## Parte 1: Infraestructura e IaC

### 1. Servicios a utilizar
La infraestructura de la solución consta de tres partes: la ingesta de datos, el almacenamiento y la exposición de estos. Esta infraestructura utiliza los servicios de **Google Cloud Platform** (GCP).

a. Para la **ingesta de datos** se utiliza el servicio **Pub/Sub** de GCP. Este recibe los datos de diversas fuentes, para luego distribuirse hacia el servicio de almacenamiento y análisis. Pub/Sub permite manejar flujos de datos en tiempo real y de manera asincrónica y escalable, siendo ideal en estos escenarios en los que es necesario desacoplar la ingesta de datos del procesamiento.

b. El **almacenamiento y análisis de datos** se realiza mediante **BigQuery**. Este almacenará los datos ingeridos y proporcionará capacidad de análisis que podrá ser aprovechada por otras aplicaciones a través de consultas SQL. BigQuery almacena y analiza grandes volúmenes de datos sin necesidad de gestionar la infraestructura subyacente, lo que simplifica su manejo, pero sin dejar de lado el análsis avanzado de datos que se requiere.

Se utilizará unicamente un `dataset` con una única tabla para simplificar la posterior consulta con la API HTTP. Las columnas de la tabla serán: un ID único, nombre, apellido y país. Siendo todos campos de tipo `string` y obligatorios.

c. Para **exponer los datos almacenados** mediante una API HTTP, se utiliza el servicio de **Cloud Run**. Este aloja la API que sirve los datos desde BigQuery, proporcionando un endpoint al que pueden consumir terceros. Al igual que BigQuery, Cloud Run es un servicio *serverless*, es decir que el *cloud provider*, en este caso GCP, se encargará de la gestíon del servidor, escalando automáticamente según la demanda y permitiendo que la API esté disponible y responda eficientemente las solicitudes sin gastar recursos innecesarios.

### 2. Despliegue de infraestructura

Para el despliegue automático de estos servicios en GCP, se utiliza el software de *infrastructure as code* (IaC) **Terraform**.

El código se encuentra en el directorio `/terraform`, que contiene los servicios anteriormente mencionados, y la configuración básica para poder desplegarlos.

Para crear los recursos en un **entorno GCP ya existente**, primero es necesario autenticarse a la consola de Google Cloud. Para esto se utiliza el **archivo de credenciales** de una *service account*. Este método es seguro y fácil de implementar. Para ello se crea una *service account* manualmente en GCP, con los permisos necesarios para correr todos los servicios correspondientes. Luego se crea una JSON *key* dentro de esta cuenta, la cual se coloca en el directorio `/terraform` con el nombre `gcp-terraform-creds.json`, y de esta forma Terraform conectará la cuenta de GCP correctamente.

Este archivo JSON no debe ser incluido en el control de versiones, por los riesgos de seguridad que conlleva tener datos sensibles que permitan el acceso a la cuenta de Google Cloud.

Por el mismo motivo, no se cuenta con el archivo `terraform.tfvars` que indica a Terraform el valor de las variables que debe utilizar. Para facilitar la ejecución, se creó el archivo `terraforn.tfvars.example` que indica que variables hay que *setear*, y un valor de ejemplo para cada una de ellas.

Una vez resuelto estas dos últimas cuestiones, se procede a inicializar el directorio de trabajo de Terraform, en el propio directorio `/terraform`:
```
terraform init
 ```
 
Luego se crea el plan de ejecución:
```
terraform plan
```

Y por último se aplican los cambios para alcanzar el estado deseado de la infraestructura:
```
terraform apply
```

## Parte 2: Aplicaciones y flujo CI/CD

### 1. Aplicación API HTTP

La **API HTTP** tiene como propósito exponer los datos almacenados en BigQuery a través de los endpoints de esta. Como se mencionó anteriormente, la API es desplegada en Google Cloud Run, permitiendo que escale según la demanda y optimizando el uso de recursos. También puede ser ejecutada de manera local, siguiendo los pasos de este [README.md](./api/app/README.app).

La **estructura de la aplicación** está organizada de manera que cada componente de la API esté claramente delimitado:

- `app/`: Contiene la aplicación principal, con submódulos organizados para manejar las rutas, la lógica de negocio, y la interacción con la base de datos.
    - `routes.py`: Define los endpoints de la API y maneja las solicitudes HTTP.
    - `bigquery_handler.py`: Contiene la lógica para interactuar con BigQuery, incluyendo funciones para ejecutar consultas SQL y manejar los datos devueltos.

- `config/`: Almacena la configuración de la API, incluyendo las credenciales necesarias para interactuar con los servicios de GCP y las variables de entorno.

- `test/test_data`: Contiene el script para poblar la base de datos de BigQuery.
    - `mock_data.py`: Script para poblar la base de datos en GCP y así probar los endpoints definidos anteriormente. Utiliza la bilbioteca `Faker` para crear datos ficticios realistas.

La aplicación cuenta con varios endpoints que permiten realizar lecturas en la base de datos, exponiendo los datos de esta al recibir una petición GET. Para esto se desarrollaron los siguientes endpoints:

- **GET /records**: Este endpoint permite obtener un conjunto de registros de la base de datos de BigQuery. Soporta paginación mediante los parámetros `limit` y `offset`, permitiendo controlar la cantidad de registros devueltos y la posición desde la cual se empiezan a contar los registros.

 - **GET /records/<id>**: Este endpoint permite obtener un único registro basado en el `ID` proporcionado en la URL.


La API se desarrolló utilizando el framework de **Flask** de Python, facilitando así la creación de la aplicación web necesaria para exponer los datos. Se emplearon *blueprints* para modularizar el código, separando la lógica de la API en distintas partes, lo que facilita el mantenimiento y permite ampliar los métodos fácilmente en un futuro.

Para leer datos desde BigQuery, se implementó el método `execute_query` en el módulo `bigquery_handler.py` que ejecuta consultas SQL utilizando el cliente oficial de Google Cloud para Python (`google-cloud-bigquery`). Los resultados de las consultas se transforman en listas de diccionarios para facilitar su serialización y posterior envío como respuesta a las solicitudes HTTP.

