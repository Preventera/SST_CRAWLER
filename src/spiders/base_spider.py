"""
Spider de base pour le crawler SST.
"""

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from datetime import datetime
from urllib.parse import urlparse

from ..models.item import SSTDocument
from ..processors.semantic_processor import SemanticProcessor
from ..processors.pdf_processor import PDFProcessor
from ..config.settings import MAX_DEPTH


class SSTBaseSpider(CrawlSpider):
    """Spider de base pour crawler les sites de santé et sécurité au travail."""
    
    name = 'sst_base'
    
    def __init__(self, source_name, start_urls, allowed_domains, *args, **kwargs):
        self.source_name = source_name
        self.start_urls = start_urls
        self.allowed_domains = allowed_domains
        self.semantic_processor = SemanticProcessor()
        self.pdf_processor = PDFProcessor()
        
        # Définition des règles de crawl
        self.rules = (
            # Règle pour suivre les liens et les traiter
            Rule(
                LinkExtractor(allow=(), deny=()),
                callback='parse_item',
                follow=True,
                process_request='process_request'
            ),
        )
        
        super().__init__(*args, **kwargs)
    
    def process_request(self, request, spider):
        """Traite les requêtes pour respecter la profondeur maximale."""
        depth = request.meta.get('depth', 0)
        if depth > MAX_DEPTH:
            return None
        return request
    
    def parse_item(self, response):
        """Traite chaque page pour en extraire les informations."""
        # Vérifier si c'est un PDF
        if response.headers.get('Content-Type', b'').startswith(b'application/pdf'):
            return self.parse_pdf(response)
        
        # Traiter une page web normale
        return self.parse_webpage(response)
    
    def parse_webpage(self, response):
        """Traite une page web pour en extraire les informations."""
        # Extraction du titre
        title = response.css('title::text').get() or ''
        title = title.strip()
        
        # Extraction du contenu principal
        content = ' '.join([
            text.strip() for text in response.css('p::text, h1::text, h2::text, h3::text, h4::text, li::text').getall()
            if text.strip()
        ])
        
        # Traitement sémantique (mise à jour pour inclure les secteurs)
        categories, keywords, summary, sectors = self.semantic_processor.process_text(content)
        
        # Création de l'item
        item = SSTDocument(
            url=response.url,
            title=title,
            source=self.source_name,
            content=content,
            summary=summary,
            categories=categories,
            keywords=keywords,
            sectors=sectors,  # Ajout des secteurs
            doc_type='webpage',
            depth=response.meta.get('depth', 0)
        )
        
        # Extraction de la date de publication si disponible
        date_text = response.css('time::text, .date::text, .published::text').get()
        if date_text:
            try:
                item.publication_date = datetime.strptime(date_text.strip(), '%Y-%m-%d')
            except ValueError:
                pass  # Ignorer si le format de date n'est pas reconnu
        
        return item
    
    def parse_pdf(self, response):
        """Traite un document PDF pour en extraire les informations."""
        # Extraction du nom de fichier à partir de l'URL
        url_path = urlparse(response.url).path
        filename = url_path.split('/')[-1]
        
        # Sauvegarde du PDF localement
        pdf_path = f'output/pdf/{self.source_name}/{filename}'
        with open(pdf_path, 'wb') as f:
            f.write(response.body)
        
        # Extraction du texte et des métadonnées du PDF
        text, metadata = self.pdf_processor.extract_text_and_metadata(pdf_path)
        
        # Traitement sémantique (mise à jour pour inclure les secteurs)
        categories, keywords, summary, sectors = self.semantic_processor.process_text(text)
        
        # Création de l'item
        item = SSTDocument(
            url=response.url,
            title=metadata.get('title', filename),
            source=self.source_name,
            content=text[:5000],  # Limiter la taille du contenu
            summary=summary,
            categories=categories,
            keywords=keywords,
            sectors=sectors,  # Ajout des secteurs
            doc_type='pdf',
            pdf_path=pdf_path,
            depth=response.meta.get('depth', 0)
        )
        
        # Extraction de la date de publication si disponible dans les métadonnées
        if 'creation_date' in metadata:
            item.publication_date = metadata['creation_date']
        
        # Extraction de l'auteur si disponible dans les métadonnées
        if 'author' in metadata:
            item.author = metadata['author']
        
        return item