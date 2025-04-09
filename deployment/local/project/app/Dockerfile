FROM python:3.12-slim-bullseye

WORKDIR /app/

RUN set -eux && \
    apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    apt-transport-https \
    gcc \
    python3-dev \
    libpq-dev \
    libkrb5-dev \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/etc/poetry python3 -
ENV PATH="/etc/poetry/bin:$PATH"
ENV PYTHONPATH=/app

COPY ./app/pyproject.toml ./app/poetry.lock /app/
COPY ./app /app
RUN poetry install --no-root

COPY ./deployment/local/project/app/docker-entrypoint.sh ./docker-entrypoint.sh
RUN chmod +x ./docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["/bin/bash"]
