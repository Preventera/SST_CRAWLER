"""
Module de notification pour alerter des nouveaux contenus découverts.
"""

import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Any

class NotificationManager:
    """Gestionnaire de notifications pour le crawler SST."""
    
    def __init__(self, email_recipient=None):
        """
        Initialise le gestionnaire de notifications.
        
        Args:
            email_recipient: Adresse email du destinataire des notifications
        """
        self.email_recipient = email_recipient
        self.history_file = 'output/notification_history.json'
        self.last_notification = self._load_history()
        
        # Créer le répertoire de sortie s'il n'existe pas
        os.makedirs('output', exist_ok=True)
    
    def _load_history(self) -> Dict[str, Any]:
        """Charge l'historique des notifications."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erreur lors du chargement de l'historique des notifications: {e}")
        
        # Historique par défaut si le fichier n'existe pas ou est invalide
        return {
            'last_run': None,
            'notified_urls': []
        }
    
    def _save_history(self) -> None:
        """Sauvegarde l'historique des notifications."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.last_notification, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de l'historique des notifications: {e}")
    
    def check_new_content(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Vérifie si de nouveaux contenus ont été découverts.
        
        Args:
            items: Liste des items extraits par le crawler
            
        Returns:
            Liste des nouveaux items
        """
        # Récupérer les URLs déjà notifiées
        notified_urls = set(self.last_notification.get('notified_urls', []))
        
        # Filtrer les nouveaux items
        new_items = [item for item in items if item['url'] not in notified_urls]
        
        # Mettre à jour l'historique
        if new_items:
            self.last_notification['last_run'] = datetime.now().isoformat()
            self.last_notification['notified_urls'] = list(notified_urls.union(item['url'] for item in new_items))
            self._save_history()
        
        return new_items
    
    def send_notification(self, new_items: List[Dict[str, Any]]) -> bool:
        """
        Envoie une notification pour les nouveaux contenus.
        
        Args:
            new_items: Liste des nouveaux items
            
        Returns:
            True si la notification a été envoyée avec succès, False sinon
        """
        if not new_items:
            return True  # Pas de nouveaux contenus, pas besoin de notification
        
        # Générer le contenu de la notification
        notification_content = self._generate_notification_content(new_items)
        
        # Enregistrer la notification dans un fichier
        self._save_notification_to_file(notification_content)
        
        # Envoyer la notification par email si configuré
        if self.email_recipient:
            return self._send_email_notification(notification_content, new_items)
        
        return True
    
    def _generate_notification_content(self, new_items: List[Dict[str, Any]]) -> str:
        """Génère le contenu de la notification."""
        content = f"Nouveaux contenus SST découverts le {datetime.now().strftime('%d/%m/%Y à %H:%M')}\n\n"
        
        # Regrouper les items par source
        items_by_source = {}
        for item in new_items:
            source = item.get('source', 'Inconnu')
            if source not in items_by_source:
                items_by_source[source] = []
            items_by_source[source].append(item)
        
        # Générer le contenu pour chaque source
        for source, items in items_by_source.items():
            content += f"=== {source} ({len(items)} nouveaux contenus) ===\n"
            for item in items:
                content += f"- {item.get('title', 'Sans titre')}\n"
                content += f"  URL: {item.get('url', '')}\n"
                if item.get('categories'):
                    content += f"  Catégories: {', '.join(item.get('categories', []))}\n"
                content += "\n"
        
        return content
    
    def _save_notification_to_file(self, content: str) -> None:
        """Sauvegarde la notification dans un fichier."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'output/notification_{timestamp}.txt'
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la notification: {e}")
    
    def _send_email_notification(self, content: str, new_items: List[Dict[str, Any]]) -> bool:
        """
        Envoie une notification par email.
        
        Note: Cette fonction est un exemple et nécessite une configuration SMTP.
        Dans un environnement de production, il faudrait adapter cette fonction
        au système de notification disponible sur le serveur MCP.
        """
        try:
            # Configuration de l'email
            msg = MIMEMultipart()
            msg['Subject'] = f"SST Crawler - {len(new_items)} nouveaux contenus découverts"
            msg['From'] = "sst-crawler@example.com"
            msg['To'] = self.email_recipient
            
            # Corps de l'email
            msg.attach(MIMEText(content, 'plain'))
            
            # Connexion au serveur SMTP et envoi
            # Note: Dans un environnement réel, il faudrait configurer les paramètres SMTP
            # server = smtplib.SMTP('smtp.example.com', 587)
            # server.starttls()
            # server.login('username', 'password')
            # server.send_message(msg)
            # server.quit()
            
            # Pour l'instant, on simule l'envoi
            print(f"Simulation d'envoi d'email à {self.email_recipient}")
            print(f"Sujet: {msg['Subject']}")
            print(f"Contenu: {content[:100]}...")
            
            return True
        
        except Exception as e:
            print(f"Erreur lors de l'envoi de la notification par email: {e}")
            return False
