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

c. Para **exponer los datos almacenados** mediante una API HTTP, se utiliza el servicio de **Cloud Run**. Este aloja la API que sirve los datos desde BigQuery, proporcionando un endpoint al que pueden consumir terceros. Al igual que BigQuery, Cloud Run es un servicio *serverless*, es decir que el *cloud provider*, en este caso GCP, se encargará de la gestíon del servidor, escalando automáticamente según la demanda y permitiendo que la API esté disponible y responda eficientemente las solicitudes sin gastar recursos innecesarios.

### 2. Despliegue de infraestructura

Para el despliegue automático de estos servicios en GCP, se utilizará el software de *infrastructure as code* (IaC) **Terraform**. 