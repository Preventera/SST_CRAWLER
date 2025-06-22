#!/usr/bin/env python3
"""
Crawler SST de production - Version complète pour données réelles
Intègre Firecrawl + Scrapy + traitement sémantique + vectorisation
Lit les sources depuis sources_quebec.json
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
import schedule
import time

# Imports pour le crawling
try:
    from firecrawl import FirecrawlApp
    import scrapy
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    print(f"⚠️  Installez les dépendances: pip install firecrawl-py scrapy requests beautifulsoup4")
    exit(1)

# Imports pour le traitement sémantique
try:
    import spacy
    from sentence_transformers import SentenceTransformer
    import chromadb
    from langchain.text_splitter import RecursiveCharacterTextSplitter
except ImportError as e:
    print(f"⚠️  Installez les dépendances NLP: pip install spacy sentence-transformers chromadb langchain")

@dataclass
class CrawlResult:
    """Structure des résultats de crawl"""
    url: str
    title: str
    content: str
    content_type: str  # webpage, pdf, document
    source: str  # cnesst, irsst, asp, etc.
    categories: List[str]
    keywords: List[str]
    summary: str
    language: str
    crawl_date: str
    semantic_score: float
    metadata: Dict

class RealSSTCrawler:
    """Crawler SST de production avec capacités avancées"""
    
    def __init__(self, config_path: str = None):
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.config = self.load_config(config_path)
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialisation des composants
        self.firecrawl_app = None
        self.nlp_processor = None
        self.vectorizer = None
        self.chroma_client = None
        
        self.initialize_components()
        
    def setup_logging(self):
        """Configure le système de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            handlers=[
                logging.FileHandler("output/production_crawler.log", encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def load_config(self, config_path: str = None) -> Dict:
        """Charge la configuration du crawler avec sources externes"""
        
        # Charger sources québécoises depuis fichier externe
        sources_quebec_path = "sources_quebec.json"
        quebec_sources = {}
        
        if os.path.exists(sources_quebec_path):
            with open(sources_quebec_path, 'r', encoding='utf-8') as f:
                quebec_config = json.load(f)
                quebec_sources = quebec_config.get("sources", {})
                self.logger.info(f"✅ {len(quebec_sources)} sources québécoises chargées")
        else:
            self.logger.warning("⚠️ Fichier sources_quebec.json non trouvé")
        
        # Configuration par défaut avec sources québécoises
        default_config = {
            "sources": quebec_sources,
            "processing": {
                "semantic_categories": [
                    "accidents_travail", "prevention_risques", "formation_securite",
                    "equipements_protection", "reglementation_sst", "ergonomie",
                    "risques_chimiques", "risques_physiques", "construction",
                    "industrie_manufacturiere", "secteur_municipal", "sante_travail"
                ],
                "min_content_length": 100,
                "max_content_length": 50000,
                "language_filter": ["fr", "en"],
                "quality_threshold": 0.7
            },
            "vectorization": {
                "model_name": "sentence-transformers/all-MiniLM-L6-v2",
                "chunk_size": 1000,
                "chunk_overlap": 200,
                "collection_name": "sst_corpus_production"
            },
            "schedule": {
                "enabled": True,
                "frequency": "weekly",
                "day": "monday",
                "time": "02:00"
            }
        }
        
        # Fusion avec config utilisateur si fournie
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def initialize_components(self):
        """Initialise tous les composants du crawler"""
        try:
            # Firecrawl
            firecrawl_key = os.getenv('FIRECRAWL_API_KEY')
            if firecrawl_key:
                self.firecrawl_app = FirecrawlApp(api_key=firecrawl_key)
                self.logger.info("✅ Firecrawl initialisé")
            else:
                self.logger.warning("⚠️  FIRECRAWL_API_KEY manquant - fonctionnalités limitées")
            
            # Traitement NLP
            try:
                self.nlp_processor = spacy.load("fr_core_news_md")
                self.logger.info("✅ Processeur NLP français chargé")
            except OSError:
                self.logger.warning("⚠️  Modèle fr_core_news_md manquant - installez avec: python -m spacy download fr_core_news_md")
            
            # Vectoriseur
            try:
                self.vectorizer = SentenceTransformer(self.config["vectorization"]["model_name"])
                self.logger.info("✅ Vectoriseur initialisé")
            except Exception as e:
                self.logger.warning(f"⚠️  Erreur vectoriseur: {e}")
            
            # Base vectorielle Chroma
            try:
                self.chroma_client = chromadb.PersistentClient(path="output/chroma_db")
                self.logger.info("✅ Base vectorielle Chroma initialisée")
            except Exception as e:
                self.logger.warning(f"⚠️  Erreur Chroma: {e}")
                
        except Exception as e:
            self.logger.error(f"❌ Erreur initialisation: {e}")
    
    async def crawl_with_firecrawl(self, source_config: Dict) -> List[CrawlResult]:
        """Crawling avec Firecrawl pour les sources complexes"""
        if not self.firecrawl_app:
            self.logger.error("Firecrawl non disponible")
            return []
        
        results = []
        source_name = source_config["name"]
        
        self.logger.info(f"🕷️  Crawling Firecrawl pour {source_name}")
        
        for start_url in source_config["start_urls"]:
            try:
                # Crawl avec extraction intelligente
                crawl_result = self.firecrawl_app.crawl_url(
                    start_url,
                    params={
                        'crawlerOptions': {
                            'includes': ['pdf', 'guide', 'formation', 'prevention'],
                            'excludes': ['contact', 'login', 'recherche'],
                            'maxDepth': 2,
                            'limit': source_config.get('max_pages', 50)
                        },
                        'pageOptions': {
                            'formats': ['markdown', 'html'],
                            'onlyMainContent': True
                        }
                    }
                )
                
                if crawl_result.get('success'):
                    for page in crawl_result.get('data', []):
                        result = await self.process_page_content(
                            page, source_name, "firecrawl"
                        )
                        if result:
                            results.append(result)
                
                # Pause respectueuse
                await asyncio.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Erreur crawl Firecrawl {start_url}: {e}")
        
        self.logger.info(f"✅ Firecrawl {source_name}: {len(results)} pages traitées")
        return results
    
    async def crawl_with_requests(self, source_config: Dict) -> List[CrawlResult]:
        """Crawling avec requests + BeautifulSoup pour les sources simples"""
        results = []
        source_name = source_config["name"]
        
        self.logger.info(f"🌐 Crawling requests pour {source_name}")
        
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'SST Research Bot (+https://exemple.com)'
        })
        
        for start_url in source_config["start_urls"]:
            try:
                response = session.get(start_url, timeout=30)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extraction du contenu principal
                    content = self.extract_main_content(soup)
                    title = soup.find('title').get_text() if soup.find('title') else ""
                    
                    # Traitement du contenu
                    result = await self.process_content(
                        url=start_url,
                        title=title,
                        content=content,
                        source=source_name,
                        content_type="webpage"
                    )
                    
                    if result:
                        results.append(result)
                    
                    # Trouver les liens vers les PDFs et autres ressources
                    pdf_links = self.find_pdf_links(soup, start_url)
                    for pdf_url in pdf_links[:10]:  # Limiter à 10 PDFs par page
                        pdf_result = await self.process_pdf(pdf_url, source_name)
                        if pdf_result:
                            results.append(pdf_result)
                
                await asyncio.sleep(1)  # Pause respectueuse
                
            except Exception as e:
                self.logger.error(f"Erreur crawl requests {start_url}: {e}")
        
        self.logger.info(f"✅ Requests {source_name}: {len(results)} pages traitées")
        return results
    
    def extract_main_content(self, soup) -> str:
        """Extrait le contenu principal d'une page"""
        # Supprimer les éléments non pertinents
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            element.decompose()
        
        # Chercher le contenu principal
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=['content', 'main'])
        
        if main_content:
            return main_content.get_text(strip=True, separator=' ')
        else:
            return soup.get_text(strip=True, separator=' ')
    
    def find_pdf_links(self, soup, base_url: str) -> List[str]:
        """Trouve tous les liens PDF sur une page"""
        pdf_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.endswith('.pdf'):
                if href.startswith('http'):
                    pdf_links.append(href)
                else:
                    # Lien relatif - construire l'URL complète
                    from urllib.parse import urljoin
                    pdf_links.append(urljoin(base_url, href))
        return pdf_links
    
    async def process_content(self, url: str, title: str, content: str, 
                            source: str, content_type: str) -> Optional[CrawlResult]:
        """Traite et analyse le contenu d'une page"""
        if len(content) < self.config["processing"]["min_content_length"]:
            return None
        
        # Limite la taille du contenu
        max_length = self.config["processing"]["max_content_length"]
        if len(content) > max_length:
            content = content[:max_length] + "..."
        
        try:
            # Traitement sémantique
            categories = self.classify_content(content)
            keywords = self.extract_keywords(content)
            summary = self.generate_summary(content)
            semantic_score = self.calculate_semantic_score(content, categories)
            
            # Filtrage qualité
            if semantic_score < self.config["processing"]["quality_threshold"]:
                return None
            
            return CrawlResult(
                url=url,
                title=title.strip(),
                content=content,
                content_type=content_type,
                source=source,
                categories=categories,
                keywords=keywords,
                summary=summary,
                language="fr",  # Détection de langue à améliorer
                crawl_date=datetime.now().isoformat(),
                semantic_score=semantic_score,
                metadata={
                    "content_length": len(content),
                    "processing_date": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            self.logger.error(f"Erreur traitement contenu {url}: {e}")
            return None
    
    async def process_page_content(self, page_data: Dict, source_name: str, 
                                 crawl_type: str) -> Optional[CrawlResult]:
        """Traite le contenu d'une page depuis Firecrawl"""
        try:
            url = page_data.get('url', '')
            title = page_data.get('title', '')
            content = page_data.get('markdown', '') or page_data.get('content', '')
            
            return await self.process_content(
                url=url,
                title=title,
                content=content,
                source=source_name,
                content_type="webpage"
            )
        except Exception as e:
            self.logger.error(f"Erreur process_page_content: {e}")
            return None
    
    def classify_content(self, content: str) -> List[str]:
        """Classifie le contenu par catégories SST"""
        categories = []
        content_lower = content.lower()
        
        category_keywords = {
            "accidents_travail": ["accident", "blessure", "incident", "traumatisme"],
            "prevention_risques": ["prévention", "prévenir", "risque", "sécurité"],
            "formation_securite": ["formation", "cours", "apprentissage", "certification"],
            "equipements_protection": ["epi", "équipement", "protection", "casque", "gants"],
            "construction": ["chantier", "construction", "bâtiment", "travaux"],
            "ergonomie": ["ergonomie", "posture", "tms", "troubles musculo"],
            "risques_chimiques": ["chimique", "toxique", "exposition", "substance"],
            "reglementation_sst": ["règlement", "loi", "norme", "obligation"]
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                categories.append(category)
        
        return categories[:3]  # Limiter à 3 catégories principales
    
    def extract_keywords(self, content: str) -> List[str]:
        """Extrait les mots-clés importants"""
        if not self.nlp_processor:
            # Extraction simple si spaCy n'est pas disponible
            return self.simple_keyword_extraction(content)
        
        doc = self.nlp_processor(content[:5000])  # Limiter pour la performance
        keywords = []
        
        for token in doc:
            if (token.pos_ in ['NOUN', 'ADJ'] and 
                len(token.text) > 3 and 
                not token.is_stop and 
                token.is_alpha):
                keywords.append(token.lemma_.lower())
        
        # Retourner les mots-clés les plus fréquents
        from collections import Counter
        return [word for word, count in Counter(keywords).most_common(10)]
    
    def simple_keyword_extraction(self, content: str) -> List[str]:
        """Extraction simple de mots-clés sans NLP"""
        import re
        words = re.findall(r'\b[a-zA-ZÀ-ÿ]{4,}\b', content.lower())
        
        # Mots vides français
        stop_words = {'dans', 'avec', 'pour', 'être', 'avoir', 'cette', 'celui', 'tout', 'plus'}
        keywords = [w for w in words if w not in stop_words]
        
        from collections import Counter
        return [word for word, count in Counter(keywords).most_common(10)]
    
    def generate_summary(self, content: str, max_length: int = 200) -> str:
        """Génère un résumé du contenu"""
        # Résumé simple : prendre les premières phrases significatives
        sentences = content.split('.')
        summary_parts = []
        current_length = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and current_length + len(sentence) < max_length:
                summary_parts.append(sentence)
                current_length += len(sentence)
            elif current_length > 50:
                break
        
        return '. '.join(summary_parts) + '.' if summary_parts else content[:max_length]
    
    def calculate_semantic_score(self, content: str, categories: List[str]) -> float:
        """Calcule un score de pertinence sémantique"""
        score = 0.5  # Score de base
        
        # Bonus pour les catégories SST identifiées
        score += len(categories) * 0.1
        
        # Bonus pour la longueur appropriée
        if 500 <= len(content) <= 5000:
            score += 0.2
        
        # Bonus pour les mots-clés SST
        sst_keywords = ['sécurité', 'prévention', 'risque', 'formation', 'accident', 'santé']
        content_lower = content.lower()
        keyword_count = sum(1 for keyword in sst_keywords if keyword in content_lower)
        score += keyword_count * 0.05
        
        return min(score, 1.0)
    
    async def process_pdf(self, pdf_url: str, source: str) -> Optional[CrawlResult]:
        """Traite un document PDF"""
        try:
            response = requests.get(pdf_url, timeout=60)
            if response.status_code == 200:
                # Sauvegarder le PDF temporairement
                pdf_path = f"output/temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                with open(pdf_path, 'wb') as f:
                    f.write(response.content)
                
                # Extraire le texte (nécessite pdfminer ou autre)
                content = self.extract_pdf_text(pdf_path)
                
                # Nettoyer le fichier temporaire
                os.remove(pdf_path)
                
                if content:
                    title = pdf_url.split('/')[-1].replace('.pdf', '').replace('-', ' ').title()
                    return await self.process_content(
                        url=pdf_url,
                        title=title,
                        content=content,
                        source=source,
                        content_type="pdf"
                    )
        
        except Exception as e:
            self.logger.error(f"Erreur traitement PDF {pdf_url}: {e}")
        
        return None
    
    def extract_pdf_text(self, pdf_path: str) -> str:
        """Extrait le texte d'un PDF"""
        try:
            from pdfminer.high_level import extract_text
            return extract_text(pdf_path)
        except ImportError:
            self.logger.warning("pdfminer.six non installé - extraction PDF désactivée")
            return ""
        except Exception as e:
            self.logger.error(f"Erreur extraction PDF: {e}")
            return ""
    
    async def vectorize_and_store(self, results: List[CrawlResult]):
        """Vectorise et stocke les résultats dans Chroma"""
        if not self.vectorizer or not self.chroma_client:
            self.logger.warning("Vectorisation non disponible")
            return
        
        try:
            # Créer ou récupérer la collection
            collection_name = self.config["vectorization"]["collection_name"]
            
            try:
                collection = self.chroma_client.get_collection(collection_name)
            except:
                collection = self.chroma_client.create_collection(collection_name)
            
            # Diviser les textes longs en chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.config["vectorization"]["chunk_size"],
                chunk_overlap=self.config["vectorization"]["chunk_overlap"]
            )
            
            documents = []
            metadatas = []
            ids = []
            
            for i, result in enumerate(results):
                chunks = text_splitter.split_text(result.content)
                
                for j, chunk in enumerate(chunks):
                    documents.append(chunk)
                    metadatas.append({
                        "source": result.source,
                        "url": result.url,
                        "title": result.title,
                        "categories": ",".join(result.categories),
                        "keywords": ",".join(result.keywords),
                        "content_type": result.content_type,
                        "crawl_date": result.crawl_date,
                        "semantic_score": result.semantic_score,
                        "chunk_index": j
                    })
                    ids.append(f"{result.source}_{i}_{j}")
            
            # Vectoriser et stocker par batches
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i:i+batch_size]
                batch_metas = metadatas[i:i+batch_size]
                batch_ids = ids[i:i+batch_size]
                
                collection.add(
                    documents=batch_docs,
                    metadatas=batch_metas,
                    ids=batch_ids
                )
            
            self.logger.info(f"✅ {len(documents)} chunks vectorisés et stockés")
            
        except Exception as e:
            self.logger.error(f"Erreur vectorisation: {e}")
    
    async def run_full_crawl(self) -> Dict:
        """Exécute un crawl complet de toutes les sources"""
        start_time = datetime.now()
        all_results = []
        
        self.logger.info("🚀 Démarrage du crawl complet SST")
        
        for source_name, source_config in self.config["sources"].items():
            try:
                method = source_config.get("crawl_method", "scrapy")
                
                if method == "firecrawl" and self.firecrawl_app:
                    results = await self.crawl_with_firecrawl(source_config)
                elif method in ["scrapy", "requests", "hybrid"]:
                    results = await self.crawl_with_requests(source_config)
                else:
                    self.logger.warning(f"Méthode inconnue pour {source_name}: {method}")
                    continue
                
                all_results.extend(results)
                self.logger.info(f"✅ {source_name}: {len(results)} résultats")
                
            except Exception as e:
                self.logger.error(f"❌ Erreur source {source_name}: {e}")
        
        # Vectorisation et stockage
        if all_results:
            await self.vectorize_and_store(all_results)
        
        # Sauvegarde JSON
        self.save_results(all_results)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        summary = {
            "execution_id": f"prod_{start_time.strftime('%Y%m%d_%H%M%S')}",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "total_results": len(all_results),
            "sources_processed": len(self.config["sources"]),
            "success_rate": len(all_results) / max(1, len(self.config["sources"]) * 10),
            "results_by_source": {
                source: len([r for r in all_results if r.source == source])
                for source in set(r.source for r in all_results)
            }
        }
        
        self.logger.info(f"🎯 Crawl terminé: {len(all_results)} résultats en {duration:.1f}s")
        return summary
    
    def save_results(self, results: List[CrawlResult]):
        """Sauvegarde les résultats au format JSON"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Conversion en dictionnaire pour JSON
        json_results = {
            "metadata": {
                "execution_id": f"prod_{timestamp}",
                "execution_date": datetime.now().isoformat(),
                "total_results": len(results),
                "crawler_version": "production_1.0_sources_externes"
            },
            "results": [
                {
                    "url": r.url,
                    "title": r.title,
                    "content": r.content,
                    "content_type": r.content_type,
                    "source": r.source,
                    "categories": r.categories,
                    "keywords": r.keywords,
                    "summary": r.summary,
                    "language": r.language,
                    "crawl_date": r.crawl_date,
                    "semantic_score": r.semantic_score,
                    "metadata": r.metadata
                }
                for r in results
            ]
        }
        
        # Sauvegarde avec timestamp
        filename = f"output/sst_production_results_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(json_results, f, indent=2, ensure_ascii=False)
        
        # Sauvegarde comme dernier résultat
        with open("output/latest_production_results.json", 'w', encoding='utf-8') as f:
            json.dump(json_results, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"📄 Résultats sauvegardés: {filename}")
    
    def setup_scheduler(self):
        """Configure l'exécution planifiée"""
        if not self.config["schedule"]["enabled"]:
            return
        
        frequency = self.config["schedule"]["frequency"]
        day = self.config["schedule"]["day"]
        time_str = self.config["schedule"]["time"]
        
        if frequency == "weekly":
            getattr(schedule.every(), day).at(time_str).do(
                lambda: asyncio.run(self.run_full_crawl())
            )
            self.logger.info(f"📅 Planification configurée: {day} à {time_str}")
        
    def run_scheduler(self):
        """Lance le scheduler en mode continu"""
        self.setup_scheduler()
        self.logger.info("🔄 Scheduler démarré - En attente...")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Vérifier chaque minute

# Interface en ligne de commande
async def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Crawler SST de production")
    parser.add_argument("--config", help="Fichier de configuration")
    parser.add_argument("--schedule", action="store_true", help="Mode planifié")
    parser.add_argument("--test", action="store_true", help="Mode test")
    
    args = parser.parse_args()
    
    crawler = RealSSTCrawler(args.config)
    
    if args.schedule:
        print("🔄 Mode planifié activé")
        crawler.run_scheduler()
    elif args.test:
        print("🧪 Mode test - crawl limité")
        # Limiter le nombre de pages pour les tests
        for source in crawler.config["sources"].values():
            source["max_pages"] = 5
        summary = await crawler.run_full_crawl()
        print(f"✅ Test terminé: {summary}")
    else:
        print("🚀 Mode production - crawl complet")
        summary = await crawler.run_full_crawl()
        print(f"✅ Crawl terminé: {summary}")

if __name__ == "__main__":
    asyncio.run(main())