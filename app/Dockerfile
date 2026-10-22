
FROM python:3.12-slim

# Directorio de trabajo
WORKDIR /app

# Configuracion de Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependencias
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copiar aplicacion y script de inicializacion
COPY . .

# Crear usuario sin privilegios de root
RUN useradd --create-home appuser

USER appuser

# Puerto de la aplicacion
EXPOSE 8000

# Inicializar PostgreSQL en Blitz Cloud
# e iniciar Gunicorn
CMD ["sh", "-c", "if [ -n \"${DATABASE_URL:-}\" ]; then python init_db.py; fi; exec gunicorn --bind 0.0.0.0:8000 main:app"]
