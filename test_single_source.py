"""
Script de test pour crawler une seule source SST.
Placé à la racine du projet pour éviter les problèmes d'importation.
"""

import os
import sys
import logging
from datetime import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("output/test_single_source.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Importation des settings
import settings

# Source de test unique
TEST_SOURCE = 'cnesst'

def run_single_source_test():
    """Exécute le crawler sur une seule source avec profondeur limitée."""
    logger.info(f"Démarrage du test avec la source: {TEST_SOURCE}")
    
    # Sauvegarder les paramètres originaux
    original_sources = settings.SOURCES.copy() if hasattr(settings, 'SOURCES') else {}
    original_max_depth = settings.MAX_DEPTH if hasattr(settings, 'MAX_DEPTH') else 3
    
    try:
        # Limiter aux paramètres de test
        test_sources = {TEST_SOURCE: original_sources[TEST_SOURCE]}
        settings.SOURCES = test_sources
        settings.MAX_DEPTH = 1  # Limiter la profondeur
        
        # Créer le répertoire de sortie s'il n'existe pas
        os.makedirs("output", exist_ok=True)
        os.makedirs("output/pdf", exist_ok=True)
        
        # Timestamp pour les fichiers de sortie
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Paramètres Scrapy
        scrapy_settings = get_project_settings()
        scrapy_settings.update({
            'BOT_NAME': 'sst_crawler_test',
            'USER_AGENT': 'SST Crawler Test (+https://example.com)',
            'ROBOTSTXT_OBEY': True,
            'CONCURRENT_REQUESTS': 4,  # Limiter le nombre de requêtes simultanées
            'DOWNLOAD_DELAY': 2.0,     # Délai plus long entre les requêtes
            'LOG_LEVEL': 'INFO',
            'FEED_FORMAT': 'json',
            'FEED_URI': f'output/test_crawl_{timestamp}.json',
            'FEED_EXPORT_ENCODING': 'utf-8',
            'DEPTH_LIMIT': 1,          # Limiter la profondeur explicitement
            'HTTPERROR_ALLOW_ALL': True,  # Permettre tous les codes d'erreur HTTP pour le test
        })
        
        # Initialiser le processus Scrapy
        process = CrawlerProcess(scrapy_settings)
        
        # Importer le spider de base
        from Dowload_Codes.base_spider import SSTBaseSpider
        
        # Ajouter la source de test au processus
        source_config = settings.SOURCES[TEST_SOURCE]
        logger.info(f"Configuration du spider pour {TEST_SOURCE}")
        logger.info(f"URLs de départ: {source_config['start_urls']}")
        logger.info(f"Domaines autorisés: {source_config['allowed_domains']}")
        
        process.crawl(
            SSTBaseSpider,
            source_name=TEST_SOURCE,
            start_urls=source_config['start_urls'],
            allowed_domains=source_config['allowed_domains']
        )
        
        # Exécuter le processus
        logger.info("Lancement du processus de crawl")
        process.start()  # Bloquant jusqu'à la fin du crawl
        
        # Vérifier les résultats
        output_file = f'output/test_crawl_{timestamp}.json'
        if os.path.exists(output_file):
            import json
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Crawl terminé avec succès. {len(data)} items extraits.")
            
            # Afficher un aperçu des premiers items
            for i, item in enumerate(data[:3]):
                logger.info(f"Item {i+1}:")
                logger.info(f"  URL: {item.get('url', 'N/A')}")
                logger.info(f"  Titre: {item.get('title', 'N/A')[:50]}...")
                logger.info(f"  Source: {item.get('source', 'N/A')}")
                if 'categories' in item:
                    logger.info(f"  Catégories: {item.get('categories', [])}")
        else:
            logger.warning(f"Aucun fichier de résultat trouvé: {output_file}")
        
        logger.info("Test terminé")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors du test: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
        
    finally:
        # Restaurer les paramètres originaux
        settings.SOURCES = original_sources
        settings.MAX_DEPTH = original_max_depth


if __name__ == "__main__":
    run_single_source_test()