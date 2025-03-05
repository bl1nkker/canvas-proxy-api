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

### Init/Drop DB:

```
cd app && poetry run cli dbinit
cd app && poetry run cli dbdrop
```

### Init/Drop DB (Test):

```
cd app && PYTHON_ENV=test poetry run cli dbinit
cd app && PYTHON_ENV=test poetry run cli dbdrop
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
2. update face recognition service
   1.2 Add hnsw index (by default?)

3. investigate how to fetch students on Canvas
4. investigate how to mark students on Canvas

- Improve user existence in Canvas
- Add tests for working canvas (wait-for-it)

# Workers

1. add students worker
2. add student attendance worker

3. write tests for all of the above shit
4. write ci/cd for github actions (tests, flake + publish_project (maybe for public sources like pypi, discuss with Timur))
5. write Dockerfile
6. [Optional] write git precommit
