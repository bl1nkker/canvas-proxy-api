#!/bin/bash

set -eux

curl -sSL https://install.python-poetry.org | python - --version 2.1.1
export PATH="/root/.local/bin:$PATH"
poetry --version

python -m venv .venv
source .venv/bin/activate

pip install "typer[all]"
pip install poetry-core==1.4.0
pip install tomlkit==0.11.8
