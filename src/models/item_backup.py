"""
Définition des modèles de données pour le crawler SST.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class SSTDocument:
    """Représente un document extrait par le crawler."""
    
    # Métadonnées de base
    url: str
    title: str
    source: str
    crawl_date: datetime = field(default_factory=datetime.now)
    
    # Contenu
    content: str = ""
    summary: str = ""
    
    # Classification sémantique
    categories: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    
    # Métadonnées supplémentaires
    publication_date: Optional[datetime] = None
    author: str = ""
    language: str = "fr"
    
    # Informations sur le document
    doc_type: str = "webpage"  # webpage, pdf, etc.
    pdf_path: Optional[str] = None
    
    # Relations avec d'autres documents
    related_docs: List[str] = field(default_factory=list)
    
    # Métadonnées techniques
    depth: int = 0
    last_updated: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'objet en dictionnaire pour l'export JSON."""
        result = {
            "url": self.url,
            "title": self.title,
            "source": self.source,
            "crawl_date": self.crawl_date.isoformat(),
            "content": self.content,
            "summary": self.summary,
            "categories": self.categories,
            "keywords": self.keywords,
            "language": self.language,
            "doc_type": self.doc_type,
            "depth": self.depth,
        }
        
        # Ajout des champs optionnels s'ils sont définis
        if self.publication_date:
            result["publication_date"] = self.publication_date.isoformat()
        if self.author:
            result["author"] = self.author
        if self.pdf_path:
            result["pdf_path"] = self.pdf_path
        if self.related_docs:
            result["related_docs"] = self.related_docs
        if self.last_updated:
            result["last_updated"] = self.last_updated.isoformat()
            
        return result
