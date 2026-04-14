FROM python:3.12-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no root
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY app ./app
COPY config.py .
COPY proyecto.py .

# Permisos
RUN chown -R appuser:appuser /app

# Usuario no root
USER appuser

EXPOSE 5000

# Comando de inicio
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "proyecto:app"]