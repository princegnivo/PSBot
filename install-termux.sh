#!/data/data/com.termux/files/usr/bin/bash
# Installation sur Termux (Android).
set -e

echo "== Installation du bot (Termux) =="

pkg update -y && pkg upgrade -y
pkg install -y python python-numpy clang make rust binutils

# Utilise la version de python fournie par 'pkg' (celle qui a python-numpy installé).
PYTHON_BIN=$(command -v python)
echo "Python détecté : $PYTHON_BIN ($($PYTHON_BIN --version))"

$PYTHON_BIN -m pip install --upgrade pip
$PYTHON_BIN -m pip install -r requirements.txt --break-system-packages

if [ ! -f .env ]; then
    cp .env.example .env
    echo "Fichier .env créé à partir de .env.example — remplis-le avant de lancer le bot."
fi

echo ""
echo "Installation terminée."
echo "Pour lancer le bot en continu sans que Termux ne le tue en arrière-plan :"
echo "  termux-wake-lock"
echo "  python main.py"
echo ""
echo "Astuce : installe 'tmux' (pkg install tmux) pour garder la session active"
echo "même si tu changes d'application."
