#!/usr/bin/env python3
"""
GAIN (GenAISafety Agentic Intelligence Network)
Script d'automatisation du crawling SST pour la production
Compatible avec l'architecture existante du projet
"""

import os
import sys
import json
import logging
import argparse
import time
import schedule
from datetime import datetime
from pathlib import Path
import threading
import subprocess
from typing import List, Dict, Optional

# Configuration du logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / f"crawling_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("GAIN-SST-Crawler")

# Répertoires de travail
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
CHROMA_DIR = DATA_DIR / "chroma_db"
CHROMA_DIR.mkdir(exist_ok=True)

# Sources SST à crawler
SOURCES = {
    "cnesst": {
        "name": "CNESST",
        "base_url": "https://www.cnesst.gouv.qc.ca/fr/prevention-securite",
        "spider": "cnesst_spider",
        "max_pages": 100,
        "enabled": True,
        "priority": 1
    },
    "irsst": {
        "name": "IRSST",
        "base_url": "https://www.irsst.qc.ca/publications-et-outils",
        "spider": "irsst_spider",
        "max_pages": 100,
        "enabled": True,
        "priority": 2
    },
    "asp_construction": {
        "name": "ASP Construction",
        "base_url": "https://www.asp-construction.org/ressources-sst/centre-de-documentation",
        "spider": "asp_construction_spider",
        "max_pages": 100,
        "enabled": True,
        "priority": 3
    },
    "apssap": {
        "name": "APSSAP",
        "base_url": "https://apssap.qc.ca/ressources/",
        "spider": "apssap_spider",
        "max_pages": 50,
        "enabled": True,
        "priority": 4
    },
    "multiprevention": {
        "name": "MultiPrévention",
        "base_url": "https://multiprevention.org/publications/",
        "spider": "multiprevention_spider",
        "max_pages": 50,
        "enabled": True,
        "priority": 5
    },
    "apsam": {
        "name": "APSAM",
        "base_url": "https://www.apsam.com/theme",
        "spider": "apsam_spider",
        "max_pages": 50,
        "enabled": True,
        "priority": 6
    },
    "asstsas": {
        "name": "ASSTSAS",
        "base_url": "https://asstsas.qc.ca/dossiers-thematiques",
        "spider": "asstsas_spider",
        "max_pages": 50,
        "enabled": True,
        "priority": 7
    },
    "asfetm": {
        "name": "ASFETM",
        "base_url": "https://www.asfetm.com/publications/",
        "spider": "asfetm_spider",
        "max_pages": 30,
        "enabled": True,
        "priority": 8
    },
    "asphme": {
        "name": "ASPHME",
        "base_url": "https://asphme.org/outils-de-prevention/",
        "spider": "asphme_spider",
        "max_pages": 30,
        "enabled": True,
        "priority": 9
    },
    "autoprévention": {
        "name": "AutoPrévention",
        "base_url": "https://autoprevention.org/documentation/",
        "spider": "autoprevention_spider",
        "max_pages": 30,
        "enabled": True,
        "priority": 10
    },
    "via_prévention": {
        "name": "Via Prévention",
        "base_url": "https://www.viaprevention.com/documentation/",
        "spider": "viaprevention_spider",
        "max_pages": 30,
        "enabled": True,
        "priority": 11
    },
    "préventex": {
        "name": "Préventex",
        "base_url": "https://www.preventex.qc.ca/fr/documentation/",
        "spider": "preventex_spider",
        "max_pages": 30,
        "enabled": True,
        "priority": 12
    },
    "santéquébec": {
        "name": "Santé Québec",
        "base_url": "https://www.quebec.ca/sante/conseils-et-prevention/sante-et-environnement/sante-au-travail",
        "spider": "sante_quebec_spider",
        "max_pages": 30,
        "enabled": True,
        "priority": 13
    }
}

def parse_arguments():
    """Parse les arguments de ligne de commande"""
    parser = argparse.ArgumentParser(description="GAIN - Automatisation du crawling SST")
    parser.add_argument("--test", action="store_true", help="Mode test avec un nombre limité de pages")
    parser.add_argument("--schedule", action="store_true", help="Planifier l'exécution automatique (21h00 tous les jours)")
    parser.add_argument("--source", type=str, help="Source spécifique à crawler (cnesst, irsst, asp_construction, etc.)")
    parser.add_argument("--no-processing", action="store_true", help="Désactiver le traitement sémantique après le crawling")
    parser.add_argument("--no-vectorize", action="store_true", help="Désactiver la vectorisation après le crawling")
    parser.add_argument("--max-pages", type=int, default=0, help="Nombre maximum de pages à crawler par source")
    parser.add_argument("--output", type=str, help="Chemin de sortie personnalisé")
    return parser.parse_args()

def get_enabled_sources(args) -> List[Dict]:
    """Récupère la liste des sources activées pour le crawling"""
    sources_list = []
    
    # Si une source spécifique est demandée
    if args.source:
        if args.source in SOURCES:
            source = SOURCES[args.source]
            if source["enabled"]:
                source_copy = source.copy()
                # Limiter le nombre de pages en mode test
                if args.test:
                    source_copy["max_pages"] = min(5, source_copy["max_pages"])
                # Appliquer le nombre maximal de pages si spécifié
                if args.max_pages > 0:
                    source_copy["max_pages"] = args.max_pages
                sources_list.append(source_copy)
            else:
                logger.warning(f"La source {args.source} est désactivée dans la configuration.")
        else:
            logger.error(f"Source inconnue: {args.source}")
            available_sources = ", ".join(SOURCES.keys())
            logger.info(f"Sources disponibles: {available_sources}")
            sys.exit(1)
    else:
        # Sinon, utiliser toutes les sources activées
        for source_id, source in SOURCES.items():
            if source["enabled"]:
                source_copy = source.copy()
                # Limiter le nombre de pages en mode test
                if args.test:
                    source_copy["max_pages"] = min(5, source_copy["max_pages"])
                # Appliquer le nombre maximal de pages si spécifié
                if args.max_pages > 0:
                    source_copy["max_pages"] = args.max_pages
                sources_list.append(source_copy)
    
    # Trier par priorité
    sources_list.sort(key=lambda x: x["priority"])
    return sources_list

def run_spider(source: Dict) -> Path:
    """Exécute un spider Scrapy pour une source donnée"""
    source_id = next((k for k, v in SOURCES.items() if v["name"] == source["name"]), "unknown")
    spider_name = source["spider"]
    output_file = OUTPUT_DIR / f"crawl_{source_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    logger.info(f"Démarrage du crawling pour {source['name']} ({source_id}) avec max_pages={source['max_pages']}")
    
    # Construction de la commande Scrapy
    cmd = [
        "scrapy", "crawl", spider_name,
        "-a", f"max_pages={source['max_pages']}",
        "-a", f"base_url={source['base_url']}",
        "-o", str(output_file)
    ]
    
    try:
        # Exécution de la commande Scrapy
        logger.info(f"Exécution de la commande: {' '.join(cmd)}")
        subprocess.run(cmd, check=True, cwd=str(BASE_DIR / "src" / "spiders"))
        logger.info(f"Crawling terminé pour {source['name']}, résultats sauvegardés dans {output_file}")
        return output_file
    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur lors du crawling de {source['name']}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Erreur inattendue lors du crawling de {source['name']}: {str(e)}")
        return None

def process_crawl_results(output_files: List[Path], args) -> Path:
    """Traite les résultats de crawling pour créer un fichier JSON unique"""
    if not output_files:
        logger.warning("Aucun fichier de résultat à traiter.")
        return None
    
    all_results = []
    for file_path in output_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                results = json.load(f)
                if isinstance(results, list):
                    all_results.extend(results)
                else:
                    all_results.append(results)
            logger.info(f"Chargé {len(results) if isinstance(results, list) else 1} résultats depuis {file_path}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement de {file_path}: {str(e)}")
    
    # Créer le fichier JSON consolidé
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = OUTPUT_DIR / f"all_results_{timestamp}.json"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    # Créer un lien symbolique vers le dernier résultat
    latest_path = OUTPUT_DIR / "latest_results.json"
    if os.path.exists(latest_path):
        os.remove(latest_path)
    
    # En Windows, la création de liens symboliques nécessite des privilèges administrateur
    try:
        os.symlink(output_path, latest_path)
    except:
        # Fallback: copier le fichier
        import shutil
        shutil.copy2(output_path, latest_path)
    
    logger.info(f"Résultats consolidés sauvegardés dans {output_path}")
    return output_path

def run_semantic_processing(results_file: Path) -> Optional[Path]:
    """Exécute le traitement sémantique sur les résultats du crawling"""
    if not results_file or not os.path.exists(results_file):
        logger.warning("Aucun fichier de résultats à traiter pour le traitement sémantique.")
        return None
    
    logger.info(f"Démarrage du traitement sémantique pour {results_file}")
    
    try:
        # Exécuter le script de traitement sémantique
        cmd = [
            "python", str(BASE_DIR / "src" / "processors" / "semantic_processor.py"),
            "--input", str(results_file),
            "--output", str(OUTPUT_DIR / f"processed_{os.path.basename(results_file)}")
        ]
        
        logger.info(f"Exécution de la commande: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        
        processed_file = OUTPUT_DIR / f"processed_{os.path.basename(results_file)}"
        logger.info(f"Traitement sémantique terminé, résultats sauvegardés dans {processed_file}")
        return processed_file
    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur lors du traitement sémantique: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Erreur inattendue lors du traitement sémantique: {str(e)}")
        return None

def run_vectorization(processed_file: Path) -> bool:
    """Exécute la vectorisation des résultats traités"""
    if not processed_file or not os.path.exists(processed_file):
        logger.warning("Aucun fichier traité à vectoriser.")
        return False
    
    logger.info(f"Démarrage de la vectorisation pour {processed_file}")
    
    try:
        # Exécuter le script de vectorisation
        cmd = [
            "python", str(BASE_DIR / "src" / "processors" / "vectorize.py"),
            "--input", str(processed_file),
            "--output", str(CHROMA_DIR)
        ]
        
        logger.info(f"Exécution de la commande: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        
        logger.info(f"Vectorisation terminée, embeddings sauvegardés dans {CHROMA_DIR}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur lors de la vectorisation: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la vectorisation: {str(e)}")
        return False

def run_crawling_pipeline(args):
    """Exécute le pipeline complet de crawling"""
    logger.info(f"Démarrage du pipeline de crawling {'(mode test)' if args.test else ''}")
    start_time = time.time()
    
    # 1. Récupérer les sources activées
    sources = get_enabled_sources(args)
    if not sources:
        logger.warning("Aucune source activée pour le crawling.")
        return
    
    logger.info(f"Sources activées: {', '.join([s['name'] for s in sources])}")
    
    # 2. Exécuter les spiders pour chaque source
    output_files = []
    for source in sources:
        output_file = run_spider(source)
        if output_file:
            output_files.append(output_file)
    
    # 3. Traiter les résultats
    results_file = process_crawl_results(output_files, args)
    
    # 4. Traitement sémantique (sauf si désactivé)
    processed_file = None
    if not args.no_processing:
        processed_file = run_semantic_processing(results_file)
    else:
        logger.info("Traitement sémantique désactivé.")
        processed_file = results_file
    
    # 5. Vectorisation (sauf si désactivée)
    if not args.no_vectorize and processed_file:
        success = run_vectorization(processed_file)
        if success:
            logger.info("Vectorisation terminée avec succès.")
        else:
            logger.warning("Échec de la vectorisation.")
    else:
        logger.info("Vectorisation désactivée.")
    
    # Calcul du temps d'exécution
    elapsed_time = time.time() - start_time
    logger.info(f"Pipeline de crawling terminé en {elapsed_time:.2f} secondes.")

def scheduled_job():
    """Fonction exécutée à l'heure planifiée"""
    logger.info("Exécution planifiée du pipeline de crawling")
    args = parse_arguments()
    run_crawling_pipeline(args)

def main():
    """Fonction principale"""
    args = parse_arguments()
    
    # Vérifier si l'exécution est planifiée
    if args.schedule:
        logger.info("Configuration de l'exécution planifiée à 21h00 tous les jours.")
        schedule.every().day.at("21:00").do(scheduled_job)
        
        # Boucle principale pour l'exécution planifiée
        while True:
            schedule.run_pending()
            time.sleep(60)  # Vérifier toutes les minutes
    else:
        # Exécution immédiate
        run_crawling_pipeline(args)

if __name__ == "__main__":
    main()