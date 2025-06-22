"""
Processeur sémantique pour analyser et catégoriser le contenu SST.
"""

import spacy
import re
from typing import List, Tuple
from collections import Counter

class SemanticProcessor:
    """Classe pour le traitement sémantique des textes SST."""
    
    def __init__(self):
        """Initialise le processeur sémantique avec le modèle spaCy français."""
        self.nlp = spacy.load('fr_core_news_md')
        
        # Dictionnaire de catégories avec mots-clés associés
        self.categories = {
            'Prévention': ['prévention', 'préventif', 'prévenir', 'éviter', 'anticiper', 'mesure', 'protection'],
            'Réglementation': ['loi', 'règlement', 'norme', 'législation', 'code', 'obligation', 'légal', 'juridique'],
            'Formation': ['formation', 'cours', 'apprentissage', 'éducation', 'compétence', 'qualification'],
            'Équipements de protection': ['équipement', 'EPI', 'protection', 'casque', 'gant', 'harnais', 'masque'],
            'Risques spécifiques': ['risque', 'danger', 'chute', 'électrique', 'chimique', 'incendie', 'explosion'],
            'Bonnes pratiques': ['pratique', 'méthode', 'procédure', 'recommandation', 'guide', 'conseil'],
            'Normes et standards': ['norme', 'standard', 'ISO', 'certification', 'référentiel', 'qualité'],
            'Études et statistiques': ['étude', 'statistique', 'donnée', 'analyse', 'recherche', 'rapport', 'enquête']
        }
    
    def process_text(self, text: str) -> Tuple[List[str], List[str], str]:
        """
        Traite un texte pour en extraire les catégories, mots-clés et résumé.
        
        Args:
            text: Le texte à analyser
            
        Returns:
            Tuple contenant:
            - Liste des catégories identifiées
            - Liste des mots-clés extraits
            - Résumé du texte
        """
        # Nettoyage du texte
        text = self._clean_text(text)
        
        # Analyse avec spaCy
        doc = self.nlp(text[:100000])  # Limiter la taille pour éviter les problèmes de mémoire
        
        # Extraction des catégories
        categories = self._extract_categories(doc)
        
        # Extraction des mots-clés
        keywords = self._extract_keywords(doc)
        
        # Génération du résumé
        summary = self._generate_summary(doc)
        
        return categories, keywords, summary
    
    def _clean_text(self, text: str) -> str:
        """Nettoie le texte en supprimant les caractères spéciaux et les espaces multiples."""
        # Remplacer les sauts de ligne par des espaces
        text = re.sub(r'\n+', ' ', text)
        
        # Supprimer les caractères spéciaux
        text = re.sub(r'[^\w\s.,;:!?«»\'\-]', ' ', text)
        
        # Supprimer les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _extract_categories(self, doc) -> List[str]:
        """Extrait les catégories pertinentes du texte."""
        text_lower = doc.text.lower()
        
        # Calculer un score pour chaque catégorie
        category_scores = {}
        for category, keywords in self.categories.items():
            score = sum(1 for keyword in keywords if keyword.lower() in text_lower)
            if score > 0:
                category_scores[category] = score
        
        # Sélectionner les catégories avec un score > 0, triées par score décroissant
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        return [category for category, score in sorted_categories]
    
    def _extract_keywords(self, doc) -> List[str]:
        """Extrait les mots-clés pertinents du texte."""
        # Extraire les noms, adjectifs et verbes significatifs
        potential_keywords = [token.lemma_ for token in doc 
                             if token.pos_ in ('NOUN', 'ADJ', 'VERB') 
                             and not token.is_stop 
                             and len(token.text) > 3]
        
        # Compter les occurrences
        keyword_counter = Counter(potential_keywords)
        
        # Sélectionner les 15 mots-clés les plus fréquents
        top_keywords = [keyword for keyword, _ in keyword_counter.most_common(15)]
        
        return top_keywords
    
    def _generate_summary(self, doc) -> str:
        """Génère un résumé du texte."""
        # Extraire les phrases
        sentences = [sent.text for sent in doc.sents]
        
        # Si le texte est court, le retourner tel quel
        if len(sentences) <= 3:
            return doc.text
        
        # Sinon, prendre les 3 premières phrases comme résumé
        return ' '.join(sentences[:3])
