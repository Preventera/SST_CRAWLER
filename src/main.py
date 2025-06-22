"""
Script principal pour l'exécution du crawler SST.
"""

import os
import sys
import time
import schedule
import logging
from datetime import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Ajouter le répertoire parent au chemin d'importation
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.settings import SOURCES, OUTPUT_DIRECTORY, JSON_FILENAME, ENABLE_NOTIFICATIONS, NOTIFICATION_EMAIL
from src.spiders.base_spider import SSTBaseSpider
from src.utils.notification import NotificationManager
from src.utils.json_exporter import JSONExporter


# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(f"{OUTPUT_DIRECTORY}/crawler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_crawler():
    """Exécute le crawler pour toutes les sources configurées."""
    logger.info("Démarrage du crawler SST")
    
    # Créer le répertoire de sortie s'il n'existe pas
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
    
    # Timestamp pour les fichiers de sortie
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Paramètres Scrapy
    settings = get_project_settings()
    settings.update({
        'BOT_NAME': 'sst_crawler',
        'USER_AGENT': 'SST Crawler (+https://example.com)',
        'ROBOTSTXT_OBEY': True,
        'CONCURRENT_REQUESTS': 8,
        'DOWNLOAD_DELAY': 1.0,
        'LOG_LEVEL': 'INFO',
        'FEED_FORMAT': 'json',
        'FEED_URI': f'{OUTPUT_DIRECTORY}/raw_items_{timestamp}.json',
        'FEED_EXPORT_ENCODING': 'utf-8',
    })
    
    # Initialiser le processus Scrapy
    process = CrawlerProcess(settings)
    
    # Ajouter chaque spider au processus
    for source_name, config in SOURCES.items():
        logger.info(f"Configuration du spider pour {source_name}")
        process.crawl(
            SSTBaseSpider,
            source_name=source_name,
            start_urls=config['start_urls'],
            allowed_domains=config['allowed_domains']
        )
    
    # Exécuter le processus
    logger.info("Lancement du processus de crawl")
    process.start()  # Bloquant jusqu'à la fin du crawl
    
    # Traitement post-crawl
    logger.info("Crawl terminé, traitement des résultats")
    
    # Charger les items extraits
    raw_items_file = f'{OUTPUT_DIRECTORY}/raw_items_{timestamp}.json'
    items = []
    if os.path.exists(raw_items_file):
        import json
        with open(raw_items_file, 'r', encoding='utf-8') as f:
            items = json.load(f)
    
    # Exporter les résultats au format JSON
    exporter = JSONExporter(OUTPUT_DIRECTORY)
    json_file = exporter.export_items(items, JSON_FILENAME)
    logger.info(f"Données exportées dans {json_file}")
    
    # Envoyer des notifications si activé
    if ENABLE_NOTIFICATIONS:
        logger.info("Vérification des nouveaux contenus pour notification")
        notification_manager = NotificationManager(NOTIFICATION_EMAIL)
        new_items = notification_manager.check_new_content(items)
        
        if new_items:
            logger.info(f"{len(new_items)} nouveaux contenus découverts, envoi de notification")
            notification_manager.send_notification(new_items)
        else:
            logger.info("Aucun nouveau contenu découvert")
    
    logger.info("Traitement terminé avec succès")
    return True


def schedule_crawler():
    """Configure l'exécution hebdomadaire du crawler."""
    logger.info("Configuration de l'exécution hebdomadaire du crawler")
    
    # Exécuter le crawler tous les lundis à 2h du matin
    schedule.every().monday.at("02:00").do(run_crawler)
    
    logger.info("Crawler programmé pour s'exécuter tous les lundis à 2h du matin")
    logger.info("Appuyez sur Ctrl+C pour arrêter")
    
    try:
        # Exécuter une première fois immédiatement
        run_crawler()
        
        # Boucle principale pour l'exécution planifiée
        while True:
            schedule.run_pending()
            time.sleep(60)  # Vérifier toutes les minutes
    except KeyboardInterrupt:
        logger.info("Arrêt du programme")
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution planifiée: {e}")


if __name__ == "__main__":
    # Créer le répertoire de sortie s'il n'existe pas
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
    
    # Vérifier les arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--schedule":
        schedule_crawler()
    else:
        run_crawler()
