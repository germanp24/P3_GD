# P3_GD

Repository for the practice 3.

## Instalación

### Paso 1: Instalar Python

1. Descarga el instalador de Python desde [python.org](https://www.python.org/downloads/).
2. Ejecuta el instalador y asegúrate de seleccionar las 2 casillas inferiores.
3. Sigue las instrucciones del instalador para completar la instalación.
4. Verifica la instalación de Python abriendo una terminal y ejecutando:
    ```sh
    python --version
    ```

### Paso 2: Instalar dependencias

1. Abre una terminal y navega al directorio del proyecto.
2. Instala las dependencias necesarias:
    ```sh
    pip install requests pymongo python-dotenv
    ```

### Paso 3: Instalar y configurar MongoDB

1. Descarga e instala MongoDB desde [aquí](https://www.mongodb.com/try/download/community).
2. Asegúrate de que MongoDB esté ejecutándose en tu máquina.

### Paso 4: Configurar variables de entorno

1. Crea un archivo [.env](http://_vscodecontentref_/1) en el mismo directorio que [client.py](http://_vscodecontentref_/2).
2. Agrega tu token de GitHub al archivo [.env](http://_vscodecontentref_/3):
    ```
    GITHUB_TOKEN=tu_token_de_github
    ```

## Ejecución

1. Asegúrate de que MongoDB esté ejecutándose.
2. Ejecuta el script `client.py`:
    ```sh
    python [client.py](http://_vscodecontentref_/4)
    ```

Esto comenzará a extraer commits del repositorio especificado y los almacenará en la base de datos MongoDB.
