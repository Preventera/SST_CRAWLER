"""
Module d'export JSON pour le crawler SST.
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any


class JSONExporter:
    """Classe pour l'export des données au format JSON."""
    
    def __init__(self, output_dir='output'):
        """
        Initialise l'exporteur JSON.
        
        Args:
            output_dir: Répertoire de sortie pour les fichiers JSON
        """
        self.output_dir = output_dir
        
        # Créer le répertoire de sortie s'il n'existe pas
        os.makedirs(output_dir, exist_ok=True)
    
    def export_items(self, items: List[Dict[str, Any]], filename: str = None) -> str:
        """
        Exporte une liste d'items au format JSON.
        
        Args:
            items: Liste des items à exporter
            filename: Nom du fichier de sortie (optionnel)
            
        Returns:
            Chemin vers le fichier JSON généré
        """
        if not filename:
            # Générer un nom de fichier basé sur la date et l'heure
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'sst_data_{timestamp}.json'
        
        # Chemin complet du fichier
        file_path = os.path.join(self.output_dir, filename)
        
        # Préparer les données pour l'export
        export_data = {
            'metadata': {
                'export_date': datetime.now().isoformat(),
                'item_count': len(items),
                'sources': list(set(item.get('source', 'unknown') for item in items))
            },
            'items': items
        }
        
        # Exporter au format JSON
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            return file_path
        except Exception as e:
            print(f"Erreur lors de l'export JSON: {e}")
            return None
    
    def merge_json_files(self, file_paths: List[str], output_filename: str) -> str:
        """
        Fusionne plusieurs fichiers JSON en un seul.
        
        Args:
            file_paths: Liste des chemins vers les fichiers JSON à fusionner
            output_filename: Nom du fichier de sortie
            
        Returns:
            Chemin vers le fichier JSON fusionné
        """
        all_items = []
        sources = set()
        
        # Charger tous les items des fichiers
        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'items' in data:
                        all_items.extend(data['items'])
                    if 'metadata' in data and 'sources' in data['metadata']:
                        sources.update(data['metadata']['sources'])
            except Exception as e:
                print(f"Erreur lors de la lecture du fichier {file_path}: {e}")
        
        # Préparer les données pour l'export
        export_data = {
            'metadata': {
                'export_date': datetime.now().isoformat(),
                'item_count': len(all_items),
                'sources': list(sources),
                'merged_from': file_paths
            },
            'items': all_items
        }
        
        # Chemin complet du fichier
        output_path = os.path.join(self.output_dir, output_filename)
        
        # Exporter au format JSON
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            return output_path
        except Exception as e:
            print(f"Erreur lors de l'export JSON fusionné: {e}")
            return None
