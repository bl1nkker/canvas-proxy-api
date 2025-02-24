# Canvas Proxy with Face Recog

## Usage:

### Up docker services:
```
cd deployment/local && ./up.sh
```

### Down docker services:
```
cd deployment/local && ./down.sh
```

### Init DB:
```
cd app && poetry run cli dbinit
```

### Install poetry deps:
```
poetry install --no-root
```

### Start API:
```
cd app/web && poetry run python api.py
```

### Create Alembic Migration:
```
alembic revision --autogenerate -m "<message>"
```

## TODOS:

1. Add vectorized database (pgvector or milvus)


6. write tests for all of the above shit
7. write ci/cd for github actions (tests, flake + publish_project (maybe for public sources like pypi, discuss with Timur))
8. write Dockerfile
9. [Optional] write git precommit
