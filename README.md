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

1. Para la **ingesta de datos** se utiliza el servicio **Pub/Sub** de GCP. Este recibe los datos de diversas fuentes, para luego distribuirse hacia el servicio de almacenamiento y análisis. Pub/Sub permite manejar flujos de datos en tiempo real y de manera asincrónica y escalable, siendo ideal en estos escenarios en los que es necesario desacoplar la ingesta de datos del procesamiento.

2. El **almacenamiento y análisis de datos** se realiza mediante **BigQuery**. Este almacenará los datos ingeridos y proporcionará capacidad de análisis que podrá ser aprovechada por otras aplicaciones a través de consultas SQL. BigQuery almacena y analiza grandes volúmenes de datos sin necesidad de gestionar la infraestructura subyacente, lo que simplifica su manejo, pero sin dejar de lado el análsis avanzado de datos que se requiere. Se utiliza unicamente un `dataset` con una única tabla para simplificar la posterior consulta con la API HTTP. Las columnas de la tabla son: un ID único, nombre, apellido y país. Siendo todos campos de tipo `string` y obligatorios.

3. Para **exponer los datos almacenados** mediante una API HTTP, se utiliza el servicio de **Cloud Run**. Este aloja la API que sirve los datos desde BigQuery, proporcionando un endpoint al que pueden consumir terceros. Al igual que BigQuery, Cloud Run es un servicio *serverless*, es decir que el *cloud provider*, en este caso GCP, se encargará de la gestíon del servidor, escalando automáticamente según la demanda y permitiendo que la API esté disponible y responda eficientemente las solicitudes sin gastar recursos innecesarios. Se utiliza el servicio de **Container Registry** de GCP para almacenar la imágen de Docker de la API. De esta forma, el servicio de Cloud Run podrá utilizarla y crear el contenedor con la aplicación simplemente referenciando el repositorio y el nombre de la imágen.

### 2. Despliegue de infraestructura

Para el despliegue automático de estos servicios en GCP, se utiliza el software de *infrastructure as code* (IaC) **Terraform**.

El código se encuentra en el directorio `/terraform`, que contiene los servicios anteriormente mencionados, y la configuración básica para poder desplegarlos.

Para crear los recursos en un **entorno GCP ya existente**, primero es necesario autenticarse a la consola de Google Cloud. Para esto se utiliza el **archivo de credenciales** de una *service account*. Este método es seguro y fácil de implementar. Para ello se crea una *service account* manualmente en GCP, con los permisos necesarios para correr todos los servicios correspondientes. Luego se crea una JSON *key* dentro de esta cuenta, la cual se coloca en el directorio `/shared/config` con el nombre `gcp-cred.json`, y de esta forma Terraform conectará la cuenta de GCP correctamente.

Este archivo JSON no es incluido en el control de versiones, por los riesgos de seguridad que conlleva tener datos sensibles que permitan el acceso a la cuenta de Google Cloud.

Por el mismo motivo, no se cuenta con el archivo `terraform.tfvars` que indica a Terraform el valor de las variables que debe utilizar. Para facilitar la ejecución, se creó el archivo `terraforn.tfvars.example` dentro del directorio `/terraform`, que indica que variables hay que *setear*, y un valor de ejemplo para cada una de ellas. Para ejecutar el código, simplemente se deben cambiar los valores del archivo de ejemplo y renombrarlo a `terraform.tfvars`.

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

### 2. Despliegue de la API HTTP

Para desplegar la aplicación en la nube, esepcificamente en el servicio de Google Cloud Run, se utiliza un workflow de **GitHub Actions** . Para facilitar esta tarea, se utilizan dos acciones que permiten la construcción y publicación de la imagen de Docker a un registro, para su posterior despliegue en GCP. Estas acciones son `push-to-gcr-github-action` y `deploy-cloudrun`. La utilización de estas acciones, en lugar de por ejemplo utilizar el paso `run`, permite abstraer la lógica de los pasos que realiza y así mejorar la comprensión y el mantenimiento del *workflow*.

En *workflow* tambíen se realiza la creación de archivos con datos sensibles, que luego serán necesarios en la API. Se trata por ejemplo de los archivos `gcp_cred.json` y `gcp_vars.json`, que contiene la información para autenticarse a GCP y los nombres y valores de los servicios de GCP respectivamente. Para esto se utilizan los **GitHub Secrets** para *GitHub Actions*. Estos son variables que se crean a nivel repositorio, que contienen información sensible, y que luego pueden ser referenciados en el *workflow* para que al momento de ejecutarse, sea reemplazado por el valor seteado.

La publicación de la imágen se realiza a un repositorio de **Google Container Registry**, la cual es luego utilizada por el servicio de Cloud Run y que de esta forma pueda crear el contenedor y ejecutar la API. El repositorio es creado una vez se sube la primera imágen con el *workflow* de Actions, indicando el nombre de este en la [acción](https://github.com/TomasAMolinari/tu-latam-challenge/blob/88d32c2f39e8f61dd37219cef34a8b5cc5799f94/.github/workflows/deploy.yml#L36). La imágen que de Cloud Run utiliza, se indica en el [código](https://github.com/TomasAMolinari/tu-latam-challenge/blob/88d32c2f39e8f61dd37219cef34a8b5cc5799f94/terraform/modules/cloudrun/main.tf#L9) de Terraform, junto con el resto de configuración de este servicio.

Con este código de Terraform, se desplegó en CloudRun, el cual a su vez corre la imágen de Docker publicada y desplegada por el *workflow*. La **URL de Cloud Run** es `https://data-api-service-vgf42mneka-uc.a.run.app`. Por lo tanto se puede probar la API, por ejemplo con la siguiente consulta: 
`https://data-api-service-vgf42mneka-uc.a.run.app/records/12345`

Obteniendo como respuesta el siguiente JSON:
```
{
  "apellido": "Perez",
  "id": "12345",
  "nombre": "Juan",
  "pais": "Argentina"
}
```

### 3. Ingesta de datos mediante Pub/Sub

Para la **ingesta de datos** se utiliza una aplicación en Python, la cual escucha continuamente al tema de Google Pub/Sub, esperando a recibir un mensaje. Una vez recibido este mensaje, se ejecuta un [callback](https://github.com/TomasAMolinari/tu-latam-challenge/blob/f847594e3ea7b51e6d769e30af7764e27e677af0/pubsub_app/gcp_handler/pubsub_handler.py#L24-L45) para insertar el contenido en la base de datos de BigQuery.

La aplicación se ejecuta de forma local, siguiendo los pasos de este [README.md](https://github.com/TomasAMolinari/tu-latam-challenge/blob/development/pubsub_app/README.md).

Internamente, la función realiza la validación para insertar aquellos registros que contengan todos los campos necesarios. Si la información del mensaje no es correcta u ocurre algún error en el procesamiento, entonces se vuelve a intentar hasta llegar al número de intentos máximos dado en el [código](https://github.com/TomasAMolinari/tu-latam-challenge/blob/f847594e3ea7b51e6d769e30af7764e27e677af0/terraform/modules/pubsub/main.tf#L20) de Terraform. Si llega a la cantidad de intentos máximas, entonces se enviará el mensaje a otro tema de Pub/Sub, utilizando la política de *deadman letter*.

### 4. Diagrama de Arquitectura

El siguiente **diagrama de arquitectura** es una representación a alto nivel de todas las interacciones del sistema, partiendo desde el momento en donde se publica la imágen de la API en Container Registry mediante el workflow de *GitHub Actions*, para luego ser utilizada por el servicio de Cloud Run, la cual recibe solicitudes de un usuario y le responde con los datos de BigQuery. A su vez el usuario publica mensajes en formato JSON al tema de Pub/Sub, al cual se suscribe la aplicación de PubSub que es ejecutada por el usuario, y que al recibir los mensajes de este servicio, inserta la información en BigQuery.

![diagrama](./img/diagrama.png)

## Parte 3: Pruebas de Integración y Puntos Críticos de Calidad

### 1. Test de integración

Para verificar que la API esté exponiendo correctamente los datos de BigQuery, se utiliza un **test de integración** mediante `integration_test.py`. Este código realiza requests a los dos métodos GET de la API para asegurarse que respondan correctamente. 

Este código de prueba se puede probar localmente, pero está pensado para ejecutarse mediante GitHub Actions. Especificamente por medio de dos *workflows*: uno que ejecuta pruebas localmente en el *runner* de Actions, `local_test.yml`, y otro que las ejecuta directamente en el servicio de Cloud Run.

El primer *workflow* se ejecuta en ambas ramas `main` y `development`. Para esto se construye la imágen de Docker de la API y se crea su contenedor, para luego ejecutar el código de pruebas forma local. Sí las pruebas son satisfactorias y el *workflow* termina su ejecución correctamente, entonces pasa a la ejecución del *workflow* mencionado en la sección anterior, `build_and_deploy.yml`. A diferencia del anterior, este *workflow* solo se ejecuta cuando se hace un *push* o un *pull request* a la rama `main`.

Al ejecutarse correctamente el *workflow* de despliegue, este da lugar al último flujo de CI/CD, es decir la prueba de integración remota. Esta es mas sencilla que la local, ya que solo debe realizar las solicitudes en el servicio de Cloud Run recién actualizado.

Para ambos *workflows* de pruebas, se utiliza el mismo código `integration_test.py`. Esto es posible con el uso de la [variable de entorno](https://github.com/TomasAMolinari/tu-latam-challenge/blob/a6f69adda78a4144cb38c2bad16e6778a5a884ad/api/test/api_test/integration_test.py#L4) para indicar que URL base utilizar, si la local, o la de Cloud Run. Esta variable será seteada en una [acción](https://github.com/TomasAMolinari/tu-latam-challenge/blob/a6f69adda78a4144cb38c2bad16e6778a5a884ad/.github/workflows/integration_test.yml#L26-L27) al momento de ejecutar cualquiera de los dos *workflows*.

### 2. Otras pruebas de integración

Las anteriores pruebas se centraron en la API HTTP y en su correcto funcionamiento tanto remoto como local. Sin embargo para probar la fucionalidad del sistema en su totalidad, se pueden implementar más testeos integradores en otras partes de este:

#### Prueba de manejo de errores para la API

Se valida que ante una solicitud GET incorrecta, la API responde correctamente al error.

Implementación:

1. Crear un *test* que envié una solicitud errónea a la API. Por ejemplo:
```
https://data-api-service-vgf42mneka-uc.a.run.app/records/estesinolovasaencontrar
```
2. Validar que la respuesta recibida es del error definido para esta situación en la API. En este caso:
```
{
  "error": "Registro no encontrado"
}
```

#### Prueba de ingesta de datos en Pub/Sub

El objetivo de esta prueba es validar que el sistema es capaz de ingerir datos correctamente a través de Pub/Sub y que estos datos se almacenan en BigQuery.

Implementación:

1. Crear un *test* que publique un mensaje en el tema de Pub/Sub. Por ejemplo siguiendo la lógica del comando:
```
gcloud pubsub topics publish data-ingest-topic --message="{'ID': '123', 'nombre': 'Juan', 'apellido': 'Pérez', 'pais': 'Argentina'}"
```
2. En el mismo código, realizar una consulta a la API para comprobar que los datos coinciden con el mensaje enviado.

#### Manejo de errores y cola *deadman letter en Pub/Sub*

Se verifica que los mensajes incorrectos son manejados adecuadamente y enviados a la cola de *dead man letter*. 

Implementación:

1. Crear un *test* que publique un mensaje inválido en el tema de Pub/Sub. Por ejemplo que le falte el campo `id`:
```
gcloud pubsub topics publish data-ingest-topic --message="{'nombre': 'Juan', 'apellido': 'Pérez', 'pais': 'Argentina'}"
```
2. En el mismo, verificar que el mensaje se encuentra en el tema de *deadman letter*.

### 3. Puntos críticos del sistema

#### Limitaciones de escalabilidad en Cloud Run

Si el tráfico hacia la API aumenta repentinamente, Cloud Run necesitará escalar para manejar la demanda. Si el escalado automático no ocurre lo suficientemente rápido, se podrían perder solicitudes o experimentar tiempos de respuesta elevados.

Pruebas:

- Prueba de escalabilidad: Realizar una prueba de carga con `locust`, para evaluar como responde Cloud Run, y si escala adecuadamente. Medir el tiempo de escalado y verificar que la API mantenga un rendimiento aceptable durante la prueba.

- Simular alta demanda: Introducir una carga de tráfico superior con `locust` a la capacidad máxima de escalado configurada en Cloud Run para evaluar cómo maneja el sistema las situaciones en las que se alcanzan estos límites.

#### Cuello de botella en Pub/Sub

Si el tema de Pub/Sub recibe un alto volumen de mensajes en un período corto, existe la posibilidad de que los mensajes no sean procesados a tiempo por el suscriptor `pubsub_app`, lo que podría causar una acumulación de mensajes en la cola.

Pruebas:

- Prueba de sobrecarga: Publicar una cantidad alta de de mensajes en el tema de Pub/Sub para observar cómo responde el sistema. Medir el tiempo de latencia desde que se publica un mensaje hasta que es procesado por completo por `pubsub_app`.

- Prueba de resiliencia: Introducir fallos en la aplicación de Pub/Sub para observar cómo se maneja la acumulación de mensajes y cómo se recupera el sistema después de restablecer el servicio.

#### Dependencia en la conectividad con BigQuery

Si hay problemas de conectividad o latencia en BigQuery, la API podría volverse lenta o no funcionar, ya que esta depende de BigQuery para consultar y almacenar datos.

Pruebas:

- Prueba de Latencia: Introducir artificialmente latencia en las consultas a BigQuery para observar cómo afecta a los tiempos de respuesta y al manejo de errores de la API.

- Prueba de conectividad: Desactivar el acceso a BigQuery para verificar cómo maneja la API la falta de conectividad, si devuelve un error manejado o si se cae la aplicación.

### 4. Robustecer el sistema

#### Optimizar el escalado automático de Cloud Run

Punto crítico: Limitaciones de escalabilidad en Cloud Run

Solución:

- *Warmup* del servicio: Configurar un número mínimo de instancias en Cloud Run para que siempre haya instancias listas para manejar solicitudes. El número mínimo se podrá encotnrar al realizar las pruebas de escalabilidad y de alta demanda.

- Configuración avanzada del escalado: Ajustar las configuraciones de escalado automático para que responda más rápidamente a cambios en la carga. Por ejemplo configurar límites mínimos y máximos de instancias. Es recomendable seguir la [documentación](https://cloud.google.com/run/docs/about-instance-autoscaling?hl=es-419) de GCP para esta cuestión.


#### Mejorar la capacidad de manejo de carga en Pub/Sub

Punto crítico: Cuello de botella en Pub/Sub

Solución:

- Aumentar el número de subscriptores: Configurar múltiples instancias de suscriptores en paralelo para procesar los mensajes más rápidamente. Esto puede lograrse desplegando la aplicación `pubsub_app` en Cloud Run para escalar automáticamente según la demanda.

#### Mejorar la disponibilidad de BigQuery

Punto crítico: Dependencia en la conectividad con BigQuery

Solución:

- Cachear resultados: Implementar un sistema de caché para almacenar los resultados de consultas frecuentes en una memoria de acceso rápido como Redis o Memorystore de Google, reduciendo la dependencia de BigQuery para las consultas repetitivas.

- Política de *disaster recovery*: Configurar la replicación de los datos en diferentes regiones para que, en caso de que una de las regiones donde se encuentra la base de datos de BigQuery experimente problemas, se pueda acceder a los datos desde una región alternativa.

## Parte 4: Métricas y Monitoreo

### 1. Métricas críticas

#### 1. Latencia de respuesta de la API

Mide el tiempo que le toma a la API en responder a las solicitudes, desde que se recibe la petición hasta que se envía la respuesta.

Es importante medir la latencia para evaluar no solo la experiencia del usuario, si no que la eficiencia del sistema. Un aumento o una latencia muy alta indica problemas de rendimiento de la API, la base de datos o alguna infraestructura relacionada, en este caso el servicio de Cloud Run.

Ante esta situación será importante diagnosticar que parte del sistema afecta a la latencia para poder introducir mejoras. Por ejemplo, refactorizando el código de la API para volverlo mas eficiente o aumentar la escalabilidad de Cloud Run.

#### 2. Tasa de Errores de la API

Mide el porcentaje de solicitudes a la API que resultan en códigos de error (4xx y 5xx).

Esta métrica es clave para identificar problemas en la lógica o eficiencia de la API, como también en la infraestructura subyacente. Al igual que el punto anterior, es importante diagnosticar en donde se originan los errores, pero la diferencia es que los arreglos deben ser críticos, ya que una alta tasa de errores afecta en gran medida el funcionamiento y a la disponibilidad del sistema.

#### 3. Tasa de ACKs y NACKs en Pub/Sub

Mide la proporción de mensajes que son reconocidos (*acknowledgement*) correctamente frente a los mensajes que no lo son (*negative acknowledgement*) en el sistema Pub/Sub.

Una tasa alta de NACKs indica problemas en el procesamiento de los mensajes, es decir en la aplicación `pubsub_app` que inserta los mensajes en BigQuery. Se puede utilizar métricas ya provistas por Cloud Monitoring, como `subscription/ack_message_count` y `subscription/nack_message_count`.


### 2. Herramienta de visualización

Para visualizar el estado del sistema se utilizaría Grafana. Es una herramienta apliamente utilizada para monitorear y analizar métricas en tiempo real. Se puede integrar con fuentes de datos como la de Google Cloud Monitoring, que permite monitorear tanto la infraestructura de GCP como la API, sin necesidad de desplegar otras fuentes como Prometheus.

#### Métricas a mostrar

Además de las tres métricas críticas del punto anterior (Latencia de la API, tasa de errores de la API y Tasa de ACKs y NACKs) se podrán incluir las siguientes en los *dashboards* de Grafana:

1. **Tasa de reintentos de la API**: Gráfico de barras que muestre el número de reintentos que realiza la API para completar una solicitud con éxito. 
Permite identificar problemas de disponibilidad. Un alto número de reintentos indica posibles problemas en la red, en el código de la API o en la infraestructura.

2. **Número de instancias de Cloud Run**: Gráfico de líneas que muestre el número de instancias de Cloud Run activas a lo largo del tiempo, junto con una métrica que indique el autoescalado, por ejemplo la tasa de solicitudes por segundo de la API. 
Permite saber si el servicio de Cloud Run está escalando adecuadamente con el tráfico, o si haría falta ajustar la configuración de autoescalado.

3. **Tiempo de inicio de instancia**: Gráfico de líneas que indique el tiempo promedio que tarda en arrancar una nueva instancia de Cloud Run. 
Permite preparase ante un aumento del tráfico inesperado. Un tiempo de inicio elevado podría afectar la experiencia de usuario al no poder responder las solicitudes en un tiempo adecuado.

4. **Duración de consultas de BigQuery**: Un gráfico de barras que muestre la duración promedio, mínima y máxima de las consultas de la API sobre BigQuery. 
Permite identificar consultas que afecten al rendimiento de la aplicación. Las consultas lentas pueden ser optimizadas para mejorar el timpo de respuesta.

5. **Tasa de errores en BigQuery**: Un gráfico de líneas que muestre la cantidad de errores en las consultas de BigQuery. 
Un aumento en los errores de las consultas indicaría problemas en la integridad de los datos, la configuración de las cosultas o con la capacidad de la base de datos de manejar la carga.

6. **Tasa de mensajes publicados**: Un gráfico de líneas que muestre el número de mensajes publicados por segundo en un tópico.
Permite entender la carga que está manejando Pub/Sub. Un aumento en la tasa de publicación indica un aumento en la actividad del sistema.

7. **Tasa de mensajes enviados al tema *deadman letter***: Un gráfico de líneas que muestre el número de mensajes publicados por segundo en el tópico de *deadman letter*
Permite entender la cantidad de mensajes que no están pudiendo ser confirmados reiteradas veces, por un error en su formación, en el sistema o en la red. Una tasa alta de estos mensajes indicaría que hay problemas en el sistema, pero una tasa nula indicaría que la política *deadman letter* no está funcionando.

8. **Tamaño promedio de los mensajes**: Un gráfico de líneas que muestre el tamaño de los mensajes publicados en un tópico.
Permite ajustar la configuración de Pub/Sub, para así mejorar el rendimiento y latencia si es que los tamaños son muy grandes, o reducir y ahorrar recursos si es que son pequeños.


### 3. Implementación de la herramienta de visualización

Siguiendo la linea del uso de infraestructura *serverless* y gestionada por Google del proyecto, se podría implementar la plataforma de Grafana mediante el ***marketplace*** de GCP. Esto facilita el despliegue y la implementación, al tener menor complejidad en la configuración y mantenimiento de la plataforma.

Para deplegar Grafana en GCP, simplemente hay que seleccionar el plan deseado en el [producto](https://console.cloud.google.com/marketplace/product/grafana-public/grafana-cloud-subscription) de esta en el *marketplace* de GCP. Al suscribirse a este, Google se encargará de configurar los recursos y servicios subyacentes, como maquinas virtuales, almacenamiento y redes.

El siguiente paso sería **integrarlo con Cloud Monitoring**, para podes monitorear de forma nativa los servicios de GCP, como Cloud Run y BigQuery. Para esto es necesario configurarla como fuente de datos, y de esta forma Grafana accederá a todas las métricas recoletadas por este servicio. Esto también implica que recolectará las métricas de la API en Cloud Run, por lo que no será necesario implementar otra fuente de datos, como Prometheus, para la aplicación.

Una vez configurada la integración, será posible crear *dashboards* en Grafana con las métricas mencionadas en el punto anterior para así monitorear la salud del sistema de forma completa.

### 4. Visualización con escalamiento

Ante un aumento de 50 sistemas similares al que tenemos, será necesario cambiar la visualización de Grafana. La gran cantidad de datos de estos sistemas podría dificultar el análisis de las métricas y la posterior toma de decisiones.

Para abordar este problema se pueden implementar varias soluciones:

- **Organización de *dashboards***: En lugar de un único *dasboard para todo el sistema, se podría dividir en grupos. Cada grupo de dasboards correspondería a uno de los sistemas específicos, permitiendo navegar de forma más sencilla.
También se podría tener un dashboard central en el cual se agrupen las métricas comunes a los 50 sistemas.

- **Uso de variables**: Se podría utilizar variables para filtrar y cambiar dinámicamente el contenido de un dashboard, de manera de poder seleccionar un sistema o un grupo de sistemas para visualizar solo las métricas correspondientes a estos.

- ***Heatmaps***: El uso de heatmaps sería útil para identificar patrones en grandes conjuntos de datos. Se podrían visualizar la distribución de métricas como la latencia, tasa de error o uso de recursos a lo largo de varios sistemas.

- **Paneles de estado**: Este tipo de paneles permiten visualizar rápidamente el estado de cada sistema con un código de color (verde, amarillo, rojo). De esta forma es más sencillo administrar muchos sistemas a la vez.
Este panel por ejemplo puede estar en el *dashboard* global mencionado en la primera solución.

- **Alertas agregadas y basadas en tendencias**: En lugar de recibir una alerta por cada sistema, se pueden configurar alertas para que se activen si múltiples sistemas experimentan problemas al mismo tiempo. También se pueden implementar alertas basadas en tendencias que identifiquen los patrones de rendimiento de los 50 sistemas, para así alertar cuando la tendencia baje/suba a determinado nivel.

### 5. Problemas en observabilidad por escalamiento

Si no se aborda correctamente el problma de la escalabilidad del sistema, podrían surgir problemas a nivel observabilidad como por ejemplo:

- **Exceso de métricas**: A medida que aumentan la cantidad de sistemas,  la cantidad de datos generados por logs, métricas y trazas aumenta exponencialmente. Si no se prepara la arquitectura adecuadamente, la sobrecarga podría llevar a la perdida de información importante o incluso el colapso de le herramienta de visualizacíon.
Gracias a la implementación mencionada anteriormente en la nube, este es un problema que tendría baja probabilidad de ocurrencia en este proyecto, ya que se utiliza un sistema de visualización en donde los recursos son manejados por Google y ante un escalamiento masivo, el sistema respondería automaticamente a este.

- **Falta de visibilidad**: Sin una estrategia de escalabilidad en Grafana, es probable que los datos de los 50 sistemas se fragmenten y se pierdan. Esto llevaría a la incapacidad de relacionar métricas entre las del sistema, además de generar lagunas de información que harían imposible analizar y tomar decisiones en esos intervalos de tiempo.

- **Alertas ineficaces**: Un sistema mal escalado, podría generar un volúmen enorme de alertas, muchas irrelevantes o duplicadas, que puede llevar a que el personal encargado de revisar estas alertas ignore tanto alertas irrelevantes como críticas, ante la gran cantidad de estas.

## Parte 5: Alertas y SRE

### 1. Reglas y umbrales para las métricas

1. **Tasa de reintentos de la API**

  - Advertencia: 5 reintentos por minuto
  - Crítico: 10 reintentos por minuto

Superar el umbral crítico indicaría que la API está fallando constantemente, por problemas de red, inestablidad de la aplicación o de la infraestructura.

2. **Número de instancias de Cloud Run**: 

  - Advertencia: 70% del límite máximo
  - Crítico: 90% del límite máximo

Si el número de instancias se acerca al nivel crítico, entonces la capacidad del sistema estaría llegando a su máximo, por lo que sería necesario un ajuste en la configuración de autoescalado.

3. **Tiempo de inicio de instancia**: 

  - Advertencia: Tiempo promedio superior a 10 segundos
  - Crítico: Tiempo promedio superior a 20 segundos

Un tiempo de inicio muy grande podría causar latencia en la respuesta a nuevas solicitudes. Un umbral crítico de 20 segundos promedio permitiría intervenir antes que el usuario experimente tiempos de respuestas intolerables.

4. **Duración de consultas de BigQuery**:

  - Advertencia: Duración promedio superior a 3 segundos
  - Crítico: Tiempo promedio superior a 5 segundos
  
  Una duración promedio de 3 segundos es aceptable teniendo en cuenta que la conexión y la posterior consulta de la API con BigQuery puede llevar un tiempo considerable. Un tiempo de espera mayor a 10 segundos para una consulta GET, podría tornarse inaceptable para el usuario.

5. **Tasa de errores en BigQuery**: 

  - Advertencia: 1% de errores en las consultas
  - Crítico: 5% de errores en las consultas

  Superar el umbral crítico afectaría en gran medida al acceso de los datos y a la funcionalidad de la API. Un 5% de errores son 5 errores cada 100 respuestas. Tomando un promedio de 1 petición por segundo, entonces habrá 3 errores por minuto, es decir 3 usuarios que no podrán recibir correctamente los datos, lo cual es excesivo para el tipo de consulta.

6. **Tasa de mensajes publicados**: 

  - Advertencia: Incremento del 50% en la tasa de mensajes publicados en comparación con el promedio
  - Crítico: Incremento del 100% en la tasa de mensajes publicados.

  Un incremento repentino del doble de mensajes publicados es provocado por un aumento inesperado de la carga o de un ataque de denegación de servicio. Para cualquiera de las dos situaciones se deberá tomar decisiones inmediatas para evitar mayores problemas.

7. **Tasa de mensajes enviados al tema *deadman letter***: 

  - Advertencia: 1% de mensajes enviados al tema
  - Crítico: 5% de mensajes enviados al tema

  Al igual que la alerta para la tasa de errores de BigQuery, superar el nivel crítico para este umbral indicaría que una cantidad mucho mayor a la deseada no está siendo confirmada por el tema de Pub/Sub. Por lo tanto tampoco estarían siendo insertados en BigQuery, perdiendose esta información por completo.

8. **Tamaño promedio de los mensajes**: 

  - Advertencia: Tamaño promedio superior a 256 KB
  - Crítico: Tamaño promedio superior a 512 KB

  Un tamaño promedio muy grande de archivo, superior a medio mega, podría relentizar el procesamiento de los mensajes y afectar la eficiencia del servicio de Pub/Sub. Controlar esto no solo que mejoraría los tiempos de respuesta, si no que evitaría costos de almacenamiento y procesamiento tanto en Pub/Sub como en BigQuery.

### 2. SLIs y SLOs

1. **SLI: Disponibilidad de la API**

Mide el porcentaje de tiempo en el que la API está disponible y responde correctamente solicitudes.

- SLO: 99,99% de la disponibilidad mensual.

Un SLO menor al propuesto, por ejemplo 99,9%, implicaría que la aplicación podría estar inactiva mas de 43 minutos por mes. Esto es mucho tiempo para la parte más crítica e importante del sistema. Un SLO de 99,99% implicaría 4,32 minutos permitidos de inactivdad por mes, lo cual es accesible y aceptable.

2. **SLI: Latencia de respuesta de la API**

Mide el tiempo que toma la API para responde una soilcitud desde que se recibe hasta que se envía la respuesta.

- SLO: 95% de las respuesta deben ser enviadas en menos de 2 segundos

La latencia afecta directamente al usuario. Mientras mayor sea el tiempo de respuesta, peor será la experiencia de este. Mantener el 95% de las respuestas en 2 segundos permite cierta flexibilidad para picos de tráfico ocasionales.

3. **SLI: Tasa de Errores de la API**
   
Mide el porcentaje de solicitudes a la API que resultan en un código de error (4xx o 5xx).

- SLO: Menos del 0,001% de las solicitudes deben resultar en un error por mes

Una tasa de error baja es aún mas importante que la latencia para la experiencia del usuario.  Es crucial mantener la cantidad de errores lo más baja posible. Un SLO de 0,001% implicaría que por ejemplo, para 1.000.000 de peticiones por mes, solo se tengan 1000 errores. Esto es aceptable para una API que su principal tarea es exponer la información de una base de datos.

4. **SLI: Tasa de Mensajes No Procesados en Pub/Sub (*Deadman letter rate*)**

Mide el porcentaje de mensajes que no pudieron ser procesados después de varios intentos y fueron enviados al tópico de *deadman letter*.

- SLO: Menos del 0.00001% de los mensajes deben ser enviados al tópico de *deadman letter* por mes

El componente más crítico del sistema es la inserción de los mensajes a la base de datos en BigQuery. Para un usuario o sistema es aceptable tener que volver a realizar una consulta que devuelva información por que esta falló. Sin embargo no es aceptable que la consulta falle si lo que quería era ingresar información a un sistema y gracias a este fallo ahora no pueda continuar. Una tasa de 0,00001% de errores implicaría que para 1.000.000 de consultas por mes, solo 10 fallarían, un número mucho más bajo en comparación al SLO de la API.

Métricas como la CPU, RAM o almacenamiento **no se incluyeron** en los SLIs ya que no son importantes para monitorear el sistema. Estos no siempre reflejan directamente la experiencia del usuario ni la salud del sistema. 
Los SLIs/SLOs deben incluir métricas que sean fundamentales para el funcionamiento del sistema y que si no se cumplen con el objetivo, corra peligro la operación de las aplicaciones e infraestructura. Es por esto que tampoco se incluyeron métricas de latencia de Pub/Sub ni de BigQuery, ya que no son críticas para el funcionamiento de las aplicaciones. Tampoco son críticas las métricas de mensajes publicados en Pub/Sub, el tamaño promedio de los mensajes o el número y tiempo de inicio de las instancias de Cloud Run. 
