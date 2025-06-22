"""
Script pour tester le crawler sur une seule page spécifique.
"""
import os
import sys
import logging
import json
from datetime import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Ajouter le répertoire du projet au chemin d'importation
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Créer le répertoire de sortie
os.makedirs("output", exist_ok=True)

# URL spécifique à tester (choisir une page qui semble intéressante)
TEST_URL = "https://www.cnesst.gouv.qc.ca/fr/prevention-securite/organiser-prevention/mesures-chantiers-construction/programme-prevention-chantier-construction"
TEST_DOMAIN = "cnesst.gouv.qc.ca"

try:
    # Importer le spider
    from src.spiders.base_spider import SSTBaseSpider
    
    # Paramètres Scrapy simplifiés
    settings = get_project_settings()
    settings.update({
        'BOT_NAME': 'quick_test',
        'USER_AGENT': 'SST Crawler Quick Test',
        'ROBOTSTXT_OBEY': True,
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 0,
        'LOG_LEVEL': 'INFO',
        'DEPTH_LIMIT': 0,  # Ne crawler que l'URL spécifiée
        'HTTPERROR_ALLOW_ALL': True,
        'FEED_FORMAT': 'json',
        'FEED_URI': 'output/single_page_test.json',
        'FEED_EXPORT_ENCODING': 'utf-8',
    })
    
    # Initialiser le processus
    process = CrawlerProcess(settings)
    
    # Ajouter le spider
    process.crawl(
        SSTBaseSpider,
        source_name="test",
        start_urls=[TEST_URL],
        allowed_domains=[TEST_DOMAIN]
    )
    
    logger.info(f"Lancement du crawl pour: {TEST_URL}")
    process.start()
    
    # Afficher un résumé des résultats
    if os.path.exists('output/single_page_test.json'):
        with open('output/single_page_test.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if data:
            logger.info(f"Page extraite avec succès: {data[0].get('title', 'Sans titre')}")
            
            # Afficher un aperçu des métadonnées
            categories = data[0].get('categories', [])
            keywords = data[0].get('keywords', [])
            logger.info(f"Catégories: {categories}")
            logger.info(f"Mots-clés: {keywords}")
        else:
            logger.warning("Aucune donnée extraite")
    
except Exception as e:
    logger.error(f"Erreur: {e}")
    import traceback
    logger.error(traceback.format_exc())