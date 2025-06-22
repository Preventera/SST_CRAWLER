"""
Spiders spécifiques pour les différentes sources SST.
"""

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule

from .base_spider import SSTBaseSpider
from ..config.settings import SOURCES


class CNESSTSpider(SSTBaseSpider):
    """Spider spécifique pour le site de la CNESST."""
    
    name = 'cnesst'
    
    def __init__(self, *args, **kwargs):
        source_config = SOURCES['cnesst']
        super().__init__(
            source_name='cnesst',
            start_urls=source_config['start_urls'],
            allowed_domains=source_config['allowed_domains'],
            *args, **kwargs
        )
        
        # Règles spécifiques pour la CNESST
        self.rules = (
            Rule(
                LinkExtractor(
                    allow=(
                        r'/fr/prevention-securite/',
                        r'/explorer-par-sujet/',
                        r'/sites/default/files/documents/',
                    ),
                    deny=(
                        r'/recherche',
                        r'/login',
                        r'/user',
                    )
                ),
                callback='parse_item',
                follow=True,
                process_request='process_request'
            ),
        )


class ASPConstructionSpider(SSTBaseSpider):
    """Spider spécifique pour le site de l'ASP Construction."""
    
    name = 'asp_construction'
    
    def __init__(self, *args, **kwargs):
        source_config = SOURCES['asp_construction']
        super().__init__(
            source_name='asp_construction',
            start_urls=source_config['start_urls'],
            allowed_domains=source_config['allowed_domains'],
            *args, **kwargs
        )
        
        # Règles spécifiques pour l'ASP Construction
        self.rules = (
            Rule(
                LinkExtractor(
                    allow=(
                        r'/ressources-sst/',
                        r'/formations/',
                        r'/publications/',
                    ),
                    deny=(
                        r'/recherche',
                        r'/login',
                        r'/user',
                    )
                ),
                callback='parse_item',
                follow=True,
                process_request='process_request'
            ),
        )


class PreventionBTPSpider(SSTBaseSpider):
    """Spider spécifique pour le site Prevention BTP."""
    
    name = 'prevention_btp'
    
    def __init__(self, *args, **kwargs):
        source_config = SOURCES['prevention_btp']
        super().__init__(
            source_name='prevention_btp',
            start_urls=source_config['start_urls'],
            allowed_domains=source_config['allowed_domains'],
            *args, **kwargs
        )
        
        # Règles spécifiques pour Prevention BTP
        self.rules = (
            Rule(
                LinkExtractor(
                    allow=(
                        r'/tous-les-metiers/',
                        r'/outils-en-ligne/',
                        r'/actualites/',
                    ),
                    deny=(
                        r'/recherche',
                        r'/login',
                        r'/user',
                    )
                ),
                callback='parse_item',
                follow=True,
                process_request='process_request'
            ),
        )


# Créer des instances de spiders pour les autres sources
def create_spider_classes():
    """Crée dynamiquement des classes de spiders pour les sources restantes."""
    spiders = {}
    
    for source_name, config in SOURCES.items():
        # Ignorer les sources qui ont déjà des spiders spécifiques
        if source_name in ['cnesst', 'asp_construction', 'prevention_btp']:
            continue
        
        # Créer une classe de spider pour cette source
        class_name = f"{source_name.capitalize()}Spider"
        spider_class = type(
            class_name,
            (SSTBaseSpider,),
            {
                'name': source_name,
                '__init__': lambda self, *args, **kwargs, src=source_name, cfg=config: SSTBaseSpider.__init__(
                    self,
                    source_name=src,
                    start_urls=cfg['start_urls'],
                    allowed_domains=cfg['allowed_domains'],
                    *args, **kwargs
                )
            }
        )
        
        spiders[source_name] = spider_class
    
    return spiders


# Créer les spiders dynamiquement
dynamic_spiders = create_spider_classes()

# Ajouter les spiders au module
for name, spider_class in dynamic_spiders.items():
    globals()[f"{name.capitalize()}Spider"] = spider_class
