# Documentation du Web Crawler SST

## Présentation

Ce web crawler automatisé est conçu pour surveiller, extraire et indexer intelligemment le contenu des sources en santé et sécurité du travail (SST). Il organise les informations de manière sémantique, cite les sources et produit des résultats au format JSON.

## Fonctionnalités principales

- **Crawling intelligent** : Exploration jusqu'à 3 niveaux de profondeur des sites SST
- **Traitement sémantique** : Catégorisation automatique du contenu et extraction de mots-clés
- **Extraction de contenu** : Récupération des titres, textes et documents PDF
- **Organisation structurée** : Classification par source, catégorie et pertinence
- **Export JSON** : Résultats structurés avec métadonnées
- **Notifications** : Alertes pour les nouveaux contenus découverts
- **Exécution planifiée** : Fonctionnement hebdomadaire automatisé

## Architecture du projet

```
sst_crawler/
├── src/
│   ├── config/         # Configuration du crawler
│   ├── models/         # Modèles de données
│   ├── processors/     # Traitement sémantique et PDF
│   ├── spiders/        # Spiders Scrapy pour chaque source
│   ├── utils/          # Utilitaires (export JSON, notifications)
│   └── main.py         # Script principal
├── tests/              # Tests unitaires et fonctionnels
└── output/             # Répertoire des résultats
    ├── pdf/            # PDFs téléchargés
    └── json/           # Données extraites au format JSON
```

## Prérequis

- Python 3.8+
- Bibliothèques Python : scrapy, spacy, beautifulsoup4, pdfminer.six, nltk, schedule
- Modèle linguistique spaCy français (fr_core_news_md)

## Installation

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/votre-organisation/sst-crawler.git
   cd sst-crawler
   ```

2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   python -m spacy download fr_core_news_md
   ```

3. Créez les répertoires nécessaires :
   ```bash
   mkdir -p output/pdf
   ```

## Configuration

Le fichier `src/config/settings.py` contient toutes les configurations du crawler :

- **Sources à crawler** : URLs de départ et domaines autorisés
- **Profondeur de crawl** : Nombre maximum de niveaux à explorer (par défaut : 3)
- **Catégories sémantiques** : Liste des catégories pour la classification
- **Configuration des notifications** : Activation et paramètres
- **Intégration MCP** : URL du serveur MCP

Vous pouvez modifier ce fichier pour ajouter de nouvelles sources ou ajuster les paramètres selon vos besoins.

## Utilisation

### Exécution manuelle

Pour lancer le crawler manuellement :

```bash
python src/main.py
```

### Exécution planifiée

Pour configurer le crawler en mode planifié (exécution hebdomadaire) :

```bash
python src/main.py --schedule
```

Par défaut, le crawler s'exécutera tous les lundis à 2h du matin.

### Résultats

Les résultats sont stockés dans le répertoire `output` :

- `output/sst_data.json` : Données extraites au format JSON
- `output/pdf/` : Documents PDF téléchargés, organisés par source
- `output/notification_*.txt` : Historique des notifications

## Déploiement sur serveur MCP

Pour déployer le crawler sur un serveur MCP agentique :

1. Assurez-vous que Python 3.8+ est installé sur le serveur

2. Transférez le code du crawler sur le serveur :
   ```bash
   scp -r sst_crawler/ user@mcp-server:/path/to/deployment/
   ```

3. Installez les dépendances sur le serveur :
   ```bash
   ssh user@mcp-server
   cd /path/to/deployment/sst_crawler
   pip install -r requirements.txt
   python -m spacy download fr_core_news_md
   ```

4. Configurez l'intégration MCP dans `src/config/settings.py` :
   ```python
   MCP_INTEGRATION = True
   MCP_SERVER_URL = 'http://localhost:8000'  # Ajustez selon votre configuration
   ```

5. Configurez l'exécution planifiée via cron :
   ```bash
   crontab -e
   ```
   
   Ajoutez la ligne suivante pour une exécution hebdomadaire (tous les lundis à 2h) :
   ```
   0 2 * * 1 cd /path/to/deployment/sst_crawler && python src/main.py > /path/to/deployment/sst_crawler/output/crawler.log 2>&1
   ```

## Limitations et solutions

### Blocage par les sites (403 Forbidden)

Certains sites peuvent bloquer les crawlers automatisés. Pour contourner ce problème :

1. Modifiez le User-Agent dans `src/config/settings.py` pour simuler un navigateur :
   ```python
   USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
   ```

2. Augmentez le délai entre les requêtes :
   ```python
   DOWNLOAD_DELAY = 3.0  # Délai en secondes
   ```

3. Ajoutez des headers supplémentaires pour simuler un navigateur :
   ```python
   DEFAULT_REQUEST_HEADERS = {
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
       'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
   }
   ```

### Gestion des PDFs protégés

Certains PDFs peuvent être protégés ou nécessiter une authentification. Dans ce cas :

1. Téléchargez manuellement les PDFs importants
2. Placez-les dans le répertoire `output/pdf/[source_name]/`
3. Ajoutez leurs métadonnées dans le fichier JSON de sortie

## Maintenance et extension

### Ajout de nouvelles sources

Pour ajouter une nouvelle source à crawler :

1. Modifiez `src/config/settings.py` et ajoutez la source dans le dictionnaire `SOURCES` :
   ```python
   'nouvelle_source': {
       'start_urls': ['https://www.nouvelle-source.com/sst'],
       'allowed_domains': ['nouvelle-source.com'],
       'priority': 2,
   }
   ```

2. Si nécessaire, créez un spider spécifique dans `src/spiders/specific_spiders.py`

### Personnalisation des notifications

Pour personnaliser les notifications :

1. Modifiez `src/utils/notification.py` pour adapter le format des notifications
2. Pour configurer l'envoi par email, complétez les paramètres SMTP dans la méthode `_send_email_notification`

## Dépannage

### Le crawler ne récupère aucun contenu

- Vérifiez que les URLs de départ sont accessibles
- Assurez-vous que le User-Agent est approprié
- Augmentez le délai entre les requêtes
- Vérifiez les logs dans `output/crawler.log`

### Erreurs lors de l'extraction de texte des PDFs

- Vérifiez que le PDF n'est pas protégé ou corrompu
- Assurez-vous que pdfminer.six est correctement installé
- Essayez d'extraire le texte manuellement avec `pdftotext`

### Problèmes de classification sémantique

- Vérifiez que le modèle spaCy français est correctement installé
- Ajustez les catégories et mots-clés dans `src/processors/semantic_processor.py`
- Augmentez la taille du texte analysé si nécessaire

## Support

Pour toute question ou assistance, veuillez contacter :
- Email : support@example.com
- Documentation en ligne : https://example.com/sst-crawler-docs
