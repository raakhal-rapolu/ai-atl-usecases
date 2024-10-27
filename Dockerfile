# Base image with Python 3.12
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Expose necessary ports
EXPOSE 8080
EXPOSE 8050

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
        cmake \
        libgl1-mesa-glx \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry and add it to the PATH
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    mv /root/.local/bin/poetry /usr/local/bin/poetry

# Copy project files
COPY . .

# Install dependencies using Poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Set up Taskipy for running multiple tasks
RUN poetry run pip install taskipy

# Run both Flask and Streamlit apps concurrently using Taskipy
CMD ["poetry", "run", "task", "run-all"]
