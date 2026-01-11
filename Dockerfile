FROM python:3.9-slim

WORKDIR /app

# Установка зависимостей
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установка Python пакетов
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Создание кастомной модели Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh && \
    ollama pull mistral && \
    ollama create mistral-sparql -f ./Modelfile || true

EXPOSE 5000

CMD ["python3", "sparql_generator.py"]