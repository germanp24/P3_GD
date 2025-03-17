# Práctica 3 - Gestión de Datos

Este repositorio contiene la tercera práctica de la asignatura, centrada en la gestión de datos utilizando Python y MongoDB.

## Integrantes del Equipo

- Germán Pajarero
- Zineb El Ouaazizi
- Victor Pérez
- Oussama Bolbaroud

## Descripción de la Práctica

Esta práctica consiste en la ingesta de commits desde un repositorio de GitHub en una base de datos MongoDB, aplicando los conceptos de bases de datos orientadas a documentos y utilizando la API REST de GitHub para la extracción de datos.

Los objetivos incluyen:
1. Extraer commits del repositorio https://github.com/microsoft/vscode.
2. Filtrar los commits desde el 1 de enero de 2018 hasta la actualidad.
3. Gestionar eficientemente el rate limit de GitHub.
4. Almacenar la información extendida de cada commit, incluyendo ficheros modificados y estadísticas de cambios.

## Instalación y Configuración

Para utilizar este proyecto correctamente, sigue los siguientes pasos:

### 1. Instalación de Python

1. Descarga la última versión de Python desde [python.org](https://www.python.org/downloads/).
2. Durante la instalación, asegúrate de seleccionar la opción **"Add Python to PATH"**.
3. Verifica que la instalación fue exitosa ejecutando en la terminal:
   ```sh
   python --version
   ```

### 2. Instalación de Dependencias

1. Ejecuta el siguiente comando para instalar las dependencias necesarias:
   ```sh
   pip install python-dotenv
   ```

### 3. Instalación y Configuración de MongoDB

1. Descarga e instala MongoDB desde [aquí](https://www.mongodb.com/try/download/community).
2. Asegúrate de que MongoDB esté en ejecución antes de continuar.
3. Opcionalmente, puedes instalar herramientas como Compass o Robo3T para facilitar la gestión de la base de datos.

### 4. Configuración de Variables de Entorno

1. Crea un archivo `.env` en el mismo directorio donde se encuentra `client.py`.
2. Agrega la siguiente información al archivo `.env`:
   ```sh
   GITHUB_TOKEN=tu_token_de_github
   ```

## Ejecución del Proyecto

1. Asegúrate de que MongoDB esté ejecutándose.
2. Ejecuta el script `client.py` para comenzar a extraer y almacenar datos:
   ```sh
   python client.py
   ```

Este script se encargará de extraer los commits del repositorio especificado y almacenarlos en la base de datos MongoDB.

## Recursos Adicionales

- [Documentación de MongoDB](https://docs.mongodb.com/manual/)
- [API REST de GitHub](https://docs.github.com/en/rest/commits/commits#get-a-commit)
- [MongoDB Compass](https://www.mongodb.com/try/download/compass)
