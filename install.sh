#!/usr/bin/env bash
# Installation sur Linux ou macOS.
set -e

echo "== Installation du bot (Linux/macOS) =="

PYTHON_BIN="python3"
if ! command -v $PYTHON_BIN &> /dev/null; then
    echo "Python 3 n'est pas installé. Installe-le d'abord (ex: 'brew install python3' sur macOS)."
    exit 1
fi

$PYTHON_BIN -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f .env ]; then
    cp .env.example .env
    echo "Fichier .env créé à partir de .env.example — remplis-le avant de lancer le bot."
fi

echo ""
echo "Installation terminée."
echo "Pour lancer le bot :"
echo "  source venv/bin/activate"
echo "  python main.py"
