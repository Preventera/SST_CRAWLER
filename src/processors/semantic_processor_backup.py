"""
Processeur sémantique amélioré pour analyser et catégoriser le contenu SST.
"""

import spacy
import re
from typing import List, Tuple, Dict
from collections import Counter

class SemanticProcessor:
    """Classe pour le traitement sémantique des textes SST avec des capacités améliorées."""
    
    def __init__(self):
        """Initialise le processeur sémantique avec le modèle spaCy français."""
        self.nlp = spacy.load('fr_core_news_md')
        
        # Dictionnaire enrichi de catégories avec mots-clés associés
        self.categories = {
            'Prévention': ['prévention', 'préventif', 'prévenir', 'éviter', 'anticiper', 'mesure', 'protection', 'prévenir', 'sécuriser', 'précaution', 'sécuritaire'],
            
            'Réglementation': ['loi', 'règlement', 'norme', 'législation', 'code', 'obligation', 'légal', 'juridique', 'décret', 'arrêté', 'directive', 'conformité', 'réglementaire', 'CNESST', 'LSST'],
            
            'Formation': ['formation', 'cours', 'apprentissage', 'éducation', 'compétence', 'qualification', 'sensibilisation', 'instruction', 'atelier', 'certification', 'accréditation', 'habilitation'],
            
            'Équipements de protection': ['équipement', 'EPI', 'protection', 'casque', 'gant', 'harnais', 'masque', 'lunette', 'chaussure', 'protection individuelle', 'protection collective', 'respirateur', 'système d\'arrêt de chute'],
            
            'Risques spécifiques': ['risque', 'danger', 'chute', 'électrique', 'chimique', 'incendie', 'explosion', 'ergonomique', 'biologique', 'hauteur', 'confiné', 'excavation', 'rayonnement', 'bruit', 'vibration', 'psychosocial', 'amiante', 'silice'],
            
            'Risques chimiques': ['produit chimique', 'SIMDUT', 'FDS', 'étiquette', 'toxique', 'corrosif', 'inflammable', 'cancérogène', 'mutagène', 'reprotoxique', 'allergène', 'sensibilisant'],
            
            'Risques physiques': ['bruit', 'vibration', 'radiation', 'chaleur', 'froid', 'électricité', 'rayonnement', 'pression', 'ventilation', 'éclairage'],
            
            'Risques ergonomiques': ['ergonomie', 'posture', 'mouvement répétitif', 'manutention', 'charge', 'TMS', 'trouble musculosquelettique', 'biomécanique', 'poste de travail'],
            
            'Risques psychosociaux': ['stress', 'harcèlement', 'violence', 'santé mentale', 'épuisement', 'burnout', 'surcharge', 'RPS', 'organisation du travail'],
            
            'Bonnes pratiques': ['pratique', 'méthode', 'procédure', 'recommandation', 'guide', 'conseil', 'fiche technique', 'protocole', 'instruction', 'méthode de travail', 'permis de travail'],
            
            'Normes et standards': ['norme', 'standard', 'ISO', 'certification', 'référentiel', 'qualité', 'CSA', 'ANSI', 'EN', 'homologation', 'accréditation'],
            
            'Études et statistiques': ['étude', 'statistique', 'donnée', 'analyse', 'recherche', 'rapport', 'enquête', 'indicateur', 'fréquence', 'gravité', 'incidence', 'prévalence'],
            
            'Gestion SST': ['système de gestion', 'politique', 'planification', 'audit', 'revue', 'amélioration continue', 'SGSST', 'comité', 'représentant', 'responsable', 'programme'],
            
            'Accidents et incidents': ['accident', 'incident', 'quasi-accident', 'lésion', 'blessure', 'enquête', 'analyse', 'arbre des causes', 'déclaration', 'signalement', 'premiers secours']
        }
        
        # Définition des secteurs industriels
        self.sectors = {
            'Construction': ['construction', 'bâtiment', 'chantier', 'BTP', 'génie civil', 'entrepreneur', 'gros œuvre'],
            'Manufacturier': ['usine', 'fabrication', 'manufacture', 'production', 'industriel', 'assemblage'],
            'Minier': ['mine', 'extraction', 'forage', 'minerai', 'gisement', 'carrière'],
            'Forestier': ['forêt', 'forestier', 'sylviculture', 'bois', 'abattage', 'scierie'],
            'Transport': ['transport', 'logistique', 'routier', 'ferroviaire', 'maritime', 'aérien', 'manutention'],
            'Santé': ['santé', 'hôpital', 'clinique', 'soins', 'médical', 'infirmier', 'CHSLD'],
            'Agriculture': ['agriculture', 'agricole', 'ferme', 'culture', 'élevage', 'agroalimentaire'],
            'Énergie': ['énergie', 'électricité', 'hydro', 'nucléaire', 'pétrole', 'gaz', 'renouvelable'],
            'Services': ['service', 'commerce', 'bureau', 'détail', 'restauration', 'hôtellerie']
        }
        
        # Liste de termes SST importants à privilégier
        self.sst_terms = [
            'prévention', 'sécurité', 'risque', 'danger', 'protection', 'formation',
            'accident', 'incident', 'travailleur', 'employeur', 'équipement', 'EPI',
            'CNESST', 'chantier', 'construction', 'ergonomie', 'exposition', 'chimique',
            'biologique', 'physique', 'psychosocial', 'règlement', 'norme', 'standard',
            'programme', 'comité', 'inspection', 'audit', 'enquête'
        ]
    
    def process_text(self, text: str) -> Tuple[List[str], List[str], str, List[str]]:
        """
        Traite un texte pour en extraire les catégories, mots-clés, résumé et secteurs.
        
        Args:
            text: Le texte à analyser
                
        Returns:
            Tuple contenant:
            - Liste des catégories identifiées
            - Liste des mots-clés extraits
            - Résumé du texte
            - Liste des secteurs industriels détectés
        """
        # Nettoyage du texte
        text = self._clean_text(text)
        
        # Analyse avec spaCy (limiter la taille pour éviter les problèmes de mémoire)
        doc = self.nlp(text[:100000])
        
        # Extraction des catégories
        categories = self._extract_categories(doc)
        
        # Extraction des mots-clés
        keywords = self._extract_keywords(doc)
        
        # Génération du résumé
        summary = self._generate_summary(doc)
        
        # Détection des secteurs
        sectors = self._detect_sectors(doc)
        
        return categories, keywords, summary, sectors
    
    def _clean_text(self, text: str) -> str:
        """Nettoie le texte en supprimant les caractères spéciaux et les espaces multiples."""
        # Remplacer les sauts de ligne par des espaces
        text = re.sub(r'\n+', ' ', text)
        
        # Supprimer les caractères spéciaux tout en gardant la ponctuation importante
        text = re.sub(r'[^\w\s.,;:!?«»\'\-]', ' ', text)
        
        # Supprimer les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _extract_categories(self, doc) -> List[str]:
        """Extrait les catégories pertinentes du texte avec une méthode améliorée."""
        text_lower = doc.text.lower()
        
        # Calculer un score pour chaque catégorie
        category_scores = {}
        for category, keywords in self.categories.items():
            # Score basé sur le nombre de mots-clés trouvés
            keyword_count = sum(1 for keyword in keywords if keyword.lower() in text_lower)
            
            # Score basé sur la fréquence (nombre d'occurrences des mots-clés)
            frequency_score = 0
            for keyword in keywords:
                keyword_lower = keyword.lower()
                # Compter les occurrences du mot-clé
                frequency_score += text_lower.count(keyword_lower)
            
            # Score final (combinaison de présence et fréquence)
            if keyword_count > 0:
                category_scores[category] = (keyword_count * 2) + (frequency_score * 0.5)
        
        # Sélectionner les catégories avec un score > 0, triées par score décroissant
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Limiter à 5 catégories principales pour éviter le bruit
        return [category for category, score in sorted_categories[:5]]
    
    def _extract_keywords(self, doc) -> List[str]:
        """Extrait les mots-clés pertinents du texte avec une méthode améliorée."""
        # Extraire les noms, adjectifs et verbes significatifs
        potential_keywords = []
        
        # Extraire les entités nommées pertinentes (organisations, lois, etc.)
        entities = [ent.text.lower() for ent in doc.ents if ent.label_ in ('ORG', 'LAW', 'PRODUCT')]
        potential_keywords.extend(entities)
        
        # Extraire les termes individuels
        for token in doc:
            if (token.pos_ in ('NOUN', 'ADJ', 'VERB') 
                and not token.is_stop 
                and len(token.text) > 3):
                potential_keywords.append(token.lemma_.lower())
        
        # Extraire les expressions nominales (syntagmes nominaux)
        for chunk in doc.noun_chunks:
            if len(chunk.text) > 3 and not all(token.is_stop for token in chunk):
                potential_keywords.append(chunk.text.lower())
        
        # Compter les occurrences
        keyword_counter = Counter(potential_keywords)
        
        # Donner un bonus aux termes SST spécifiques
        for term in self.sst_terms:
            for keyword in list(keyword_counter.keys()):
                if term in keyword:
                    keyword_counter[keyword] *= 1.5  # Bonus de 50%
        
        # Sélectionner jusqu'à 20 mots-clés les plus pertinents
        top_keywords = [keyword for keyword, _ in keyword_counter.most_common(20)]
        
        # Éliminer les doublons ou sous-chaînes (si un terme est inclus dans un autre)
        filtered_keywords = []
        for kw in top_keywords:
            if not any(kw in other_kw and kw != other_kw for other_kw in top_keywords):
                filtered_keywords.append(kw)
        
        return filtered_keywords[:15]  # Limiter à 15 mots-clés
    
    def _generate_summary(self, doc) -> str:
        """Génère un résumé du texte avec une méthode améliorée."""
        # Extraire les phrases
        sentences = list(doc.sents)
        
        # Si le texte est court, le retourner tel quel
        if len(sentences) <= 3:
            return doc.text
        
        # Calculer un score pour chaque phrase
        sentence_scores = {}
        
        # Mots-clés SST importants à rechercher dans les phrases
        important_terms = [
            'sécurité', 'santé', 'travail', 'prévention', 'risque', 'danger',
            'protection', 'mesure', 'obligation', 'employeur', 'travailleur',
            'règlement', 'norme', 'accident', 'formation', 'équipement'
        ]
        
        for i, sent in enumerate(sentences):
            # Score initial basé sur la position (les phrases au début et à la fin sont souvent plus importantes)
            position_score = 1.0
            if i == 0:  # Première phrase
                position_score = 3.0
            elif i == len(sentences) - 1:  # Dernière phrase
                position_score = 1.5
            elif i < 3:  # Parmi les 3 premières phrases
                position_score = 2.0
            
            # Score basé sur la présence de termes importants
            term_score = sum(1 for term in important_terms if term.lower() in sent.text.lower())
            
            # Score basé sur la longueur (éviter les phrases trop courtes ou trop longues)
            length = len(sent.text.split())
            length_score = 1.0
            if 10 <= length <= 30:  # Longueur idéale
                length_score = 1.5
            elif length < 5 or length > 50:  # Trop court ou trop long
                length_score = 0.5
            
            # Score final
            sentence_scores[sent] = position_score + term_score + length_score
        
        # Sélectionner les 3-5 meilleures phrases (selon la longueur du texte)
        summary_size = min(5, max(3, len(sentences) // 10))
        top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:summary_size]
        
        # Trier les phrases par ordre d'apparition dans le texte
        top_sentences = sorted(top_sentences, key=lambda x: sentences.index(x[0]))
        
        # Générer le résumé
        summary = ' '.join(sent.text for sent, _ in top_sentences)
        
        return summary
    
    def _detect_sectors(self, doc) -> List[str]:
        """Détecte les secteurs industriels mentionnés dans le texte."""
        text_lower = doc.text.lower()
        detected_sectors = []
        
        for sector, keywords in self.sectors.items():
            if any(keyword.lower() in text_lower for keyword in keywords):
                detected_sectors.append(sector)
        
        return detected_sectors