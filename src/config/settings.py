"""
Configuration du crawler SST.
"""

# Configuration générale
BOT_NAME = 'sst_crawler'
USER_AGENT = 'SST Crawler (+https://example.com)'
ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS = 8
DOWNLOAD_DELAY = 1.0  # Délai entre les requêtes pour être respectueux des sites
LOG_LEVEL = 'INFO'

# Profondeur maximale de crawl (selon les exigences de l'utilisateur)
MAX_DEPTH = 3

# Configuration des sources principales
SOURCES = {
    'cnesst': {
        'start_urls': [
            'https://www.cnesst.gouv.qc.ca/fr/prevention-securite/organiser-prevention/mesures-chantiers-construction',
            'https://www.cnesst.gouv.qc.ca/fr/prevention-securite/organiser-prevention/mesures-chantiers-construction/programme-prevention-chantier-construction',
            'https://www.centredoc.cnesst.gouv.qc.ca/explorer-par-sujet',
        ],
        'allowed_domains': ['cnesst.gouv.qc.ca', 'centredoc.cnesst.gouv.qc.ca'],
        'priority': 1,
    },
    'asp_construction': {
        'start_urls': [
            'https://www.asp-construction.org/ressources-sst/centre-de-documentation/veille',
            'https://asp-construction.org/formations/cours-de-30h',
        ],
        'allowed_domains': ['asp-construction.org'],
        'priority': 1,
    },
    'prevention_btp': {
        'start_urls': [
            'https://www.preventionbtp.fr/',
            'https://www.preventionbtp.fr/tous-les-metiers/la-prevention-pour-les-macons',
            'https://www.preventionbtp.fr/outils-en-ligne',
        ],
        'allowed_domains': ['preventionbtp.fr'],
        'priority': 2,
    },
    'apsam': {
        'start_urls': [
            'https://www.apsam.com/actualites/mecanismes-de-prevention-et-de-participation-en-chantier-de-construction-pour-le-secteur-municipal-precision-importante',
        ],
        'allowed_domains': ['apsam.com'],
        'priority': 2,
    },
    'ilo_org': {
        'start_urls': [
            'https://www.ilo.org/sites/default/files/wcmsp5/groups/public/@ed_dialogue/@sector/documents/normativeinstrument/wcms_861586.pdf',
        ],
        'allowed_domains': ['ilo.org'],
        'priority': 3,
    },
    'legisquebec': {
        'start_urls': [
            'https://www.legisquebec.gouv.qc.ca/fr/document/lc/s-2.1',
            'https://www.legisquebec.gouv.qc.ca/fr/ShowDoc/cr/S-2.1,%20r.%2010%20/',
        ],
        'allowed_domains': ['legisquebec.gouv.qc.ca'],
        'priority': 2,
    },
    'carsat': {
        'start_urls': [
            'https://www.carsat-aquitaine.fr/files/live/sites/carsat-aquitaine/files/documents/entreprises/prevention/Guide_MSSTweb.pdf',
        ],
        'allowed_domains': ['carsat-aquitaine.fr'],
        'priority': 3,
    },
    'umontreal': {
        'start_urls': [
            'https://fas.umontreal.ca/public/FAS/fas/Documents/communiques/Programme_de_prévention_UDM___Pavillon_Lionel_Groulx.pdf',
        ],
        'allowed_domains': ['fas.umontreal.ca'],
        'priority': 3,
    },
}

# Configuration des catégories sémantiques
SEMANTIC_CATEGORIES = [
    'Prévention',
    'Réglementation',
    'Formation',
    'Équipements de protection',
    'Risques spécifiques',
    'Bonnes pratiques',
    'Normes et standards',
    'Études et statistiques',
]

# Configuration de l'export
OUTPUT_DIRECTORY = 'output'
JSON_FILENAME = 'sst_data.json'

# Configuration des notifications
ENABLE_NOTIFICATIONS = True
NOTIFICATION_EMAIL = 'user@example.com'  # À remplacer par l'email de l'utilisateur

# Configuration MCP
MCP_INTEGRATION = True
MCP_SERVER_URL = 'http://localhost:8000'  # À remplacer par l'URL du serveur MCP
