FROM python:3.11-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos de dependencia e instala las librerías
# Esto se hace primero para aprovechar el cacheo de capas de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de los archivos de tu proyecto, incluido el modelo
# 'catboost_best_model.cbm' y el código 'app.py'
COPY . /app

# 'app.main:app' es el punto de entrada: archivo 'main.py', objeto 'app'.
# Si tu archivo se llama 'app.py', cámbialo a 'app:app'.
# --host 0.0.0.0 es necesario para que el contenedor escuche peticiones externas
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]

# Expone el puerto por el que correrá tu API
EXPOSE 80