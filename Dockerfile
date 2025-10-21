# Use an official Python runtime as a parent image
FROM python:3.13-slim

WORKDIR /app

# Install build dependencies for asyncpg and other packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy the scoring_algorithms package first
COPY scoring_algorithms /app/scoring_algorithms

# Copy uv configuration files
COPY pyproject.toml uv.lock ./

# Install dependencies with uv
RUN uv sync --frozen

# Install the scoring_algorithms package in the uv virtual environment
RUN uv pip install -e ./scoring_algorithms

# Copy the rest of the application
COPY . /app

EXPOSE 8000

# Use uv run to execute uvicorn within the virtual environment
CMD ["uv", "run", "uvicorn", "run_apps:app", "--host", "0.0.0.0", "--port", "8000"]