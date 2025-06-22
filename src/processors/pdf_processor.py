"""
Processeur PDF pour extraire le texte et les métadonnées des documents PDF.
"""

import os
from typing import Dict, Tuple, Any
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from datetime import datetime


class PDFProcessor:
    """Classe pour le traitement des documents PDF."""
    
    def __init__(self):
        """Initialise le processeur PDF."""
        # Créer le répertoire de sortie pour les PDF s'il n'existe pas
        os.makedirs('output/pdf', exist_ok=True)
    
    def extract_text_and_metadata(self, pdf_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Extrait le texte et les métadonnées d'un document PDF.
        
        Args:
            pdf_path: Chemin vers le fichier PDF
            
        Returns:
            Tuple contenant:
            - Le texte extrait du PDF
            - Un dictionnaire des métadonnées
        """
        # Vérifier que le fichier existe
        if not os.path.exists(pdf_path):
            return "", {}
        
        # Extraire le texte
        try:
            text = extract_text(pdf_path)
        except Exception as e:
            print(f"Erreur lors de l'extraction du texte du PDF {pdf_path}: {e}")
            text = ""
        
        # Extraire les métadonnées
        metadata = self._extract_metadata(pdf_path)
        
        return text, metadata
    
    def _extract_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extrait les métadonnées d'un document PDF.
        
        Args:
            pdf_path: Chemin vers le fichier PDF
            
        Returns:
            Dictionnaire des métadonnées
        """
        metadata = {}
        
        try:
            with open(pdf_path, 'rb') as file:
                parser = PDFParser(file)
                doc = PDFDocument(parser)
                
                if doc.info:
                    info = doc.info[0]
                    
                    # Extraire le titre
                    if 'Title' in info:
                        title = info['Title']
                        if isinstance(title, bytes):
                            title = title.decode('utf-8', errors='ignore')
                        metadata['title'] = title
                    
                    # Extraire l'auteur
                    if 'Author' in info:
                        author = info['Author']
                        if isinstance(author, bytes):
                            author = author.decode('utf-8', errors='ignore')
                        metadata['author'] = author
                    
                    # Extraire la date de création
                    if 'CreationDate' in info:
                        date_str = info['CreationDate']
                        if isinstance(date_str, bytes):
                            date_str = date_str.decode('utf-8', errors='ignore')
                        
                        # Essayer de parser la date (format typique: D:YYYYMMDDHHmmSS)
                        try:
                            if date_str.startswith('D:'):
                                date_str = date_str[2:]
                                date = datetime.strptime(date_str[:14], '%Y%m%d%H%M%S')
                                metadata['creation_date'] = date
                        except ValueError:
                            pass
        
        except Exception as e:
            print(f"Erreur lors de l'extraction des métadonnées du PDF {pdf_path}: {e}")
        
        return metadata
    
    def save_pdf(self, content: bytes, source_name: str, filename: str) -> str:
        """
        Sauvegarde un contenu PDF dans un fichier.
        
        Args:
            content: Contenu binaire du PDF
            source_name: Nom de la source (pour organiser les fichiers)
            filename: Nom du fichier
            
        Returns:
            Chemin vers le fichier sauvegardé
        """
        # Créer le répertoire pour la source si nécessaire
        source_dir = f'output/pdf/{source_name}'
        os.makedirs(source_dir, exist_ok=True)
        
        # Chemin complet du fichier
        file_path = f'{source_dir}/{filename}'
        
        # Sauvegarder le fichier
        with open(file_path, 'wb') as f:
            f.write(content)
        
        return file_path
