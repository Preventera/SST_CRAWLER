#!/bin/bash

# Script d'installation du crawler SST

echo "Installation du crawler SST..."

# Vérification de Python
python3 --version
if [ $? -ne 0 ]; then
    echo "Erreur: Python 3 n'est pas installé. Veuillez installer Python 3.8 ou supérieur."
    exit 1
fi

# Création de l'environnement virtuel
echo "Création de l'environnement virtuel..."
python3 -m venv venv
source venv/bin/activate

# Installation des dépendances
echo "Installation des dépendances..."
pip install -r requirements.txt

# Installation du modèle spaCy français
echo "Installation du modèle spaCy français..."
python -m spacy download fr_core_news_md

# Création des répertoires nécessaires
echo "Création des répertoires de sortie..."
mkdir -p output/pdf

echo "Installation terminée avec succès!"
echo "Pour lancer le crawler, exécutez: python src/main.py"
echo "Pour configurer l'exécution planifiée: python src/main.py --schedule"
