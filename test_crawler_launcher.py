#!/usr/bin/env python3
"""
test_crawler_launcher.py - Version simplifiée pour tests étape par étape
Placez ce fichier à la racine de votre dossier SST_CRAWLER
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path

def etape_1_creation_dossiers():
    """ÉTAPE 1: Créer les dossiers nécessaires"""
    print("🔧 ÉTAPE 1: Création des dossiers...")
    
    dossiers = ["output", "output/pdf", "output/json", "output/logs"]
    
    for dossier in dossiers:
        Path(dossier).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Dossier créé: {dossier}")
    
    print("✅ ÉTAPE 1 TERMINÉE - Dossiers créés")
    input("   ⏸️  Appuyez sur ENTRÉE pour continuer vers l'étape 2...")

def etape_2_configuration_logging():
    """ÉTAPE 2: Configuration du système de logs"""
    print("\n🔧 ÉTAPE 2: Configuration des logs...")
    
    # Configuration basique du logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler("output/logs/test.log"),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Système de logging configuré")
    
    print("   ✅ Logs configurés dans output/logs/test.log")
    print("✅ ÉTAPE 2 TERMINÉE - Logging configuré")
    input("   ⏸️  Appuyez sur ENTRÉE pour continuer vers l'étape 3...")
    
    return logger

def etape_3_creation_config():
    """ÉTAPE 3: Création de la configuration de test"""
    print("\n🔧 ÉTAPE 3: Création du fichier de configuration...")
    
    config = {
        "metadata": {
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "description": "Configuration de test pour le crawler SST"
        },
        "sources_test": {
            "cnesst": {
                "name": "CNESST - Test",
                "url": "https://www.cnesst.gouv.qc.ca/fr/prevention-securite",
                "status": "ready"
            },
            "irsst": {
                "name": "IRSST - Test", 
                "url": "https://www.irsst.qc.ca/publications-et-outils",
                "status": "ready"
            }
        },
        "parametres": {
            "max_depth": 3,
            "delay": 1.0,
            "language": "fr"
        }
    }
    
    # Sauvegarder la configuration
    with open("output/test_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("   ✅ Fichier créé: output/test_config.json")
    print(f"   📄 Contenu: {len(config)} sections configurées")
    print("✅ ÉTAPE 3 TERMINÉE - Configuration créée")
    input("   ⏸️  Appuyez sur ENTRÉE pour continuer vers l'étape 4...")

def etape_4_simulation_resultats():
    """ÉTAPE 4: Création des résultats de test simulés"""
    print("\n🔧 ÉTAPE 4: Génération des résultats de test...")
    
    resultats = {
        "metadata": {
            "execution_id": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "start_time": datetime.now().isoformat(),
            "status": "simulation_completed",
            "total_pages": 12,
            "total_pdfs": 5
        },
        "sources_testees": {
            "cnesst": {
                "pages_trouvees": 8,
                "pdfs_trouves": 3,
                "status": "success"
            },
            "irsst": {
                "pages_trouvees": 4,
                "pdfs_trouves": 2,
                "status": "success"
            }
        },
        "contenu_exemple": [
            {
                "id": "test_001",
                "titre": "Prévention des chutes sur les chantiers",
                "source": "cnesst",
                "type": "guide",
                "categories": ["construction", "prevention", "chutes"],
                "langue": "fr",
                "date_test": datetime.now().isoformat()
            },
            {
                "id": "test_002", 
                "titre": "Recherche IRSST - Équipements de protection",
                "source": "irsst",
                "type": "recherche",
                "categories": ["recherche", "EPI", "protection"],
                "langue": "fr",
                "date_test": datetime.now().isoformat()
            }
        ],
        "metriques_qualite": {
            "score_global": 0.85,
            "couverture_sources": 1.0,
            "diversite_contenu": 0.78
        }
    }
    
    # Sauvegarder les résultats
    with open("output/test_result.json", "w", encoding="utf-8") as f:
        json.dump(resultats, f, indent=2, ensure_ascii=False)
    
    print("   ✅ Fichier créé: output/test_result.json")
    print(f"   📊 {resultats['metadata']['total_pages']} pages simulées")
    print(f"   📄 {resultats['metadata']['total_pdfs']} PDFs simulés")
    print("✅ ÉTAPE 4 TERMINÉE - Résultats générés")
    input("   ⏸️  Appuyez sur ENTRÉE pour continuer vers l'étape 5...")

def etape_5_verification_finale():
    """ÉTAPE 5: Vérification des fichiers créés"""
    print("\n🔧 ÉTAPE 5: Vérification finale...")
    
    fichiers_attendus = [
        "output/test_config.json",
        "output/test_result.json", 
        "output/logs/test.log"
    ]
    
    tous_presents = True
    for fichier in fichiers_attendus:
        if os.path.exists(fichier):
            taille = os.path.getsize(fichier)
            print(f"   ✅ {fichier} - {taille} bytes")
        else:
            print(f"   ❌ {fichier} - MANQUANT")
            tous_presents = False
    
    if tous_presents:
        print("\n🎉 SUCCÈS! Tous les fichiers ont été créés")
        print("📁 Vérifiez le dossier 'output' pour voir les résultats")
    else:
        print("\n⚠️  Certains fichiers sont manquants")
    
    print("✅ ÉTAPE 5 TERMINÉE - Vérification complète")

def main():
    """Fonction principale - Exécute toutes les étapes"""
    print("=" * 60)
    print("🚀 TEST CRAWLER SST - EXÉCUTION ÉTAPE PAR ÉTAPE")
    print("=" * 60)
    print("📍 Fichier exécuté depuis:", os.getcwd())
    print()
    
    try:
        # Exécution séquentielle avec points d'arrêt
        etape_1_creation_dossiers()
        logger = etape_2_configuration_logging() 
        etape_3_creation_config()
        etape_4_simulation_resultats()
        etape_5_verification_finale()
        
        print("\n" + "=" * 60)
        print("🎯 TOUTES LES ÉTAPES TERMINÉES!")
        print("=" * 60)
        print("📄 Votre fichier test_result.json est maintenant disponible")
        print("📂 Emplacement: output/test_result.json")
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        print("🔧 Vérifiez vos permissions de fichier")

if __name__ == "__main__":
    main()
    