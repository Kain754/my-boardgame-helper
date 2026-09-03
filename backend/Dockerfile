FROM python:3.11-slim

WORKDIR /app

# Копируем requirements.txt
COPY backend/requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код из папки backend
COPY backend/ .

# Создаем папку для базы данных
RUN mkdir -p /app/data

# Команда запуска
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
