#!/usr/bin/env python3
"""
Testeur de recherche sémantique pour la base Chroma SST
Teste les requêtes sur vos vraies données SST québécoises
"""

import chromadb
from sentence_transformers import SentenceTransformer
import json
from typing import List, Dict
from datetime import datetime

class SSTSemanticSearchTester:
    """Testeur de recherche sémantique pour les données SST"""
    
    def __init__(self, chroma_path: str = "output/chroma_db"):
        """Initialise le testeur avec la base Chroma existante"""
        print("🔍 Initialisation du testeur de recherche sémantique SST...")
        
        try:
            # Connexion à la base Chroma existante
            self.chroma_client = chromadb.PersistentClient(path=chroma_path)
            print(f"✅ Connecté à la base Chroma: {chroma_path}")
            
            # Récupération de la collection SST
            self.collection = self.chroma_client.get_collection("sst_corpus_production")
            print(f"✅ Collection SST trouvée: {self.collection.count()} chunks disponibles")
            
            # Initialisation du vectoriseur (même modèle que le crawler)
            self.vectorizer = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            print("✅ Vectoriseur initialisé")
            
        except Exception as e:
            print(f"❌ Erreur d'initialisation: {e}")
            raise
    
    def search_semantic(self, query: str, n_results: int = 5) -> Dict:
        """Effectue une recherche sémantique"""
        try:
            print(f"\n🔎 Recherche: '{query}'")
            print("-" * 50)
            
            # Recherche sémantique dans Chroma
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            # Formatage des résultats
            formatted_results = []
            for i in range(len(results["documents"][0])):
                result = {
                    "rank": i + 1,
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "similarity_score": 1 / (1 + results["distances"][0][i]),
                    "source": results["metadatas"][0][i].get("source", "Unknown"),
                    "url": results["metadatas"][0][i].get("url", ""),
                    "title": results["metadatas"][0][i].get("title", ""),
                    "categories": results["metadatas"][0][i].get("categories", "").split(",")
                }
                formatted_results.append(result)
            
            # Affichage des résultats
            self.display_results(query, formatted_results)
            
            return {
                "query": query,
                "results": formatted_results,
                "search_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Erreur de recherche: {e}")
            return {}
    
    def display_results(self, query: str, results: List[Dict]):
        """Affiche les résultats de recherche de manière lisible"""
        
        if not results:
            print("❌ Aucun résultat trouvé")
            return
        
        print(f"📊 {len(results)} résultats trouvés pour: '{query}'\n")
        
        for result in results:
            similarity_pct = result["similarity_score"] * 100
            
            print(f"🎯 Résultat #{result['rank']} - Pertinence: {similarity_pct:.1f}%")
            print(f"📄 Source: {result['source']}")
            print(f"📝 Titre: {result['title'][:80]}...")
            print(f"🏷️  Catégories: {', '.join(result['categories'])}")
            print(f"📖 Contenu: {result['content'][:200]}...")
            print(f"🔗 URL: {result['url']}")
            print("-" * 50)
    
    def test_sst_queries(self):
        """Teste une série de requêtes SST typiques"""
        
        test_queries = [
            # Sujets généraux SST
            "prévention des chutes sur chantier",
            "équipements de protection individuelle",
            "formation en sécurité au travail",
            "risques chimiques et exposition",
            "cadenassage et consignation",
            
            # Sujets spécifiques construction
            "travaux en hauteur et échafaudage",
            "amiante et désamiantage",
            "tranchées et excavation",
            "signalisation de chantier",
            
            # Sujets techniques/scientifiques
            "recherche IRSST ergonomie",
            "méthodes de laboratoire analyse",
            "guide technique prévention",
            
            # Requêtes réglementaires
            "obligations employeur CNESST",
            "programme de prévention",
            "ASP formation obligatoire"
        ]
        
        print("🧪 SÉRIE DE TESTS AUTOMATIQUES")
        print("=" * 60)
        
        all_results = []
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🔬 Test {i}/{len(test_queries)}")
            result = self.search_semantic(query, n_results=3)
            all_results.append(result)
            
            # Pause entre les requêtes pour la lisibilité
            input("\n⏸️  Appuyez sur ENTRÉE pour le test suivant...")
        
        return all_results
    
    def interactive_search(self):
        """Mode de recherche interactive"""
        print("\n🔍 MODE RECHERCHE INTERACTIVE")
        print("=" * 50)
        print("Tapez vos requêtes SST ou 'quit' pour quitter")
        
        while True:
            query = input("\n🔎 Votre recherche SST: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Au revoir!")
                break
            
            if query:
                self.search_semantic(query, n_results=5)
            else:
                print("⚠️  Veuillez entrer une requête")
    
    def analyze_collection(self):
        """Analyse la collection Chroma"""
        print("\n📊 ANALYSE DE LA COLLECTION SST")
        print("=" * 50)
        
        try:
            # Statistiques générales
            count = self.collection.count()
            print(f"📈 Total chunks: {count}")
            
            # Récupération d'un échantillon pour analyse
            sample = self.collection.get(limit=10, include=["metadatas"])
            
            # Analyse des sources
            sources = {}
            categories = {}
            
            for metadata in sample["metadatas"]:
                source = metadata.get("source", "Unknown")
                sources[source] = sources.get(source, 0) + 1
                
                cats = metadata.get("categories", "").split(",")
                for cat in cats:
                    if cat.strip():
                        categories[cat.strip()] = categories.get(cat.strip(), 0) + 1
            
            print(f"\n📚 Sources représentées (échantillon):")
            for source, count in sources.items():
                print(f"   - {source}: {count} chunks")
            
            print(f"\n🏷️  Catégories détectées (échantillon):")
            for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                print(f"   - {category}: {count} mentions")
                
        except Exception as e:
            print(f"❌ Erreur d'analyse: {e}")
    
    def benchmark_search_speed(self):
        """Test de performance de recherche"""
        print("\n⚡ TEST DE PERFORMANCE")
        print("=" * 50)
        
        test_query = "prévention des risques au travail"
        
        import time
        
        # Test de vitesse
        start_time = time.time()
        for i in range(5):
            self.collection.query(
                query_texts=[test_query],
                n_results=10
            )
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 5
        print(f"⚡ Temps moyen de recherche: {avg_time:.3f} secondes")
        print(f"📊 Vitesse: {10/avg_time:.1f} résultats/seconde")

def main():
    """Fonction principale de test"""
    print("🔍 TESTEUR DE RECHERCHE SÉMANTIQUE SST")
    print("=" * 60)
    print("Testez votre base vectorielle avec vos données SST québécoises\n")
    
    try:
        # Initialisation du testeur
        tester = SSTSemanticSearchTester()
        
        # Analyse de la collection
        tester.analyze_collection()
        
        print("\n" + "=" * 60)
        print("CHOISISSEZ UN MODE DE TEST:")
        print("1. Tests automatiques (série de requêtes prédéfinies)")
        print("2. Recherche interactive (vos propres requêtes)")
        print("3. Test de performance")
        print("4. Recherche unique rapide")
        
        choice = input("\nVotre choix (1-4): ").strip()
        
        if choice == "1":
            tester.test_sst_queries()
        elif choice == "2":
            tester.interactive_search()
        elif choice == "3":
            tester.benchmark_search_speed()
        elif choice == "4":
            query = input("🔎 Votre recherche: ")
            if query:
                tester.search_semantic(query, n_results=5)
        else:
            print("❌ Choix invalide")
            
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
        print("\n💡 Vérifiez que:")
        print("   - Le dossier output/chroma_db existe")
        print("   - La collection 'sst_corpus_production' a été créée")
        print("   - Le crawler a été exécuté avec succès")

if __name__ == "__main__":
    main()