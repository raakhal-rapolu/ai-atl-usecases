# Base image with Python 3.12
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
        cmake \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry and add it to the PATH
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    mv /root/.local/bin/poetry /usr/local/bin/poetry

# Copy project files
COPY . .

# Install dependencies using Poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Expose the port
EXPOSE 8000

# Run the application
CMD ["poetry", "run", "python", "app.py"]
