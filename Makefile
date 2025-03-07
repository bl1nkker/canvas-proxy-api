w:
	cd app && poetry run celery -A celery_app worker --loglevel=info

b:
	cd app && poetry run celery -A celery_app beat --loglevel=info

start:
	cd app/web && poetry run python api.py

dbinit:
	cd app && poetry run cli dbinit

up:
	cd deployment/local && ./up.sh

down:
	cd deployment/local && ./down.sh 

build:
	docker build --tag blinkker/canvas-proxy-api:0.0.5 --tag blinkker/canvas-proxy-api:latest --file ./deployment/local/project/app/Dockerfile .

push:
	docker push blinkker/canvas-proxy-api:0.0.5
	docker push blinkker/canvas-proxy-api:latest

linter:
	ruff check .

enable-git-hooks:
	git config core.hooksPath .githooks
