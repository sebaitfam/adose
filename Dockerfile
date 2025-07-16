# Imagen base de Python
FROM python:3.11-slim

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias de Python
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código backend
COPY backend/ ./

# Copiar la carpeta build del frontend ya construida
COPY frontend/build ./static/

# Exponer el puerto (ajústalo según tu app, por ejemplo Flask)
EXPOSE 8000

# Comando de inicio
CMD ["python", "app.py"]