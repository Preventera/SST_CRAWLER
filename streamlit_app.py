import streamlit as st
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import os
import json
from datetime import datetime
import plotly.express as px

# Configuration de la page
st.set_page_config(
    page_title="GAIN - GenAISafety Agentic Intelligence Network", 
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styles personnalisés
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2563EB;
        margin-bottom: 1rem;
    }
    .highlight {
        background-color: #DBEAFE;
        padding: 0.2rem;
        border-radius: 0.2rem;
    }
    .source-tag {
        background-color: #EFF6FF;
        color: #1E40AF;
        padding: 0.2rem 0.5rem;
        border-radius: 0.5rem;
        font-size: 0.8rem;
        font-weight: 500;
        margin-right: 0.5rem;
    }
    .result-card {
        background-color: white;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid #E5E7EB;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .score-badge {
        background-color: #DBEAFE;
        color: #1E40AF;
        padding: 0.2rem 0.5rem;
        border-radius: 0.5rem;
        font-size: 0.8rem;
        font-weight: 500;
    }
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: 600;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
    }
    .footer {
        margin-top: 3rem;
        text-align: center;
        color: #6B7280;
        font-size: 0.8rem;
    }
    .metrics-container {
        display: flex;
        justify-content: space-between;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        flex: 1;
        margin: 0 0.5rem;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1E3A8A;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #4B5563;
    }
</style>
""", unsafe_allow_html=True)

# Chemin vers le dossier de données
DATA_DIR = "data"
EMBEDDINGS_PATH = os.path.join(DATA_DIR, "embeddings.npy")
METADATA_PATH = os.path.join(DATA_DIR, "metadata.json")
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"  # Modèle multilingue pour supporter français et anglais

# Fonctions utilitaires
@st.cache_resource
def load_model():
    """Charge le modèle de sentence embeddings"""
    return SentenceTransformer(MODEL_NAME)

@st.cache_data
def load_data():
    """Charge les données et prépare l'index FAISS"""
    # Si les fichiers d'embeddings et de métadonnées existent, les charger
    if os.path.exists(EMBEDDINGS_PATH) and os.path.exists(METADATA_PATH):
        embeddings = np.load(EMBEDDINGS_PATH)
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            metadata = json.load(f)
    else:
        # Sinon, utiliser des données factices pour la démonstration
        st.warning("⚠️ Données de démonstration chargées. Veuillez configurer le chemin vers vos données réelles.")
        embeddings, metadata = create_demo_data()
        
    # Créer l'index FAISS
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)  # Utiliser le produit scalaire (cosine similarity)
    index.add(embeddings.astype(np.float32))
    
    # Extraire les sources uniques pour les filtres
    sources = sorted(list(set([item["source"] for item in metadata])))
    
    # Extraire les secteurs uniques pour les filtres (si disponibles)
    sectors = []
    if "sector" in metadata[0]:
        sectors = sorted(list(set([item["sector"] for item in metadata if "sector" in item])))
    
    return embeddings, metadata, index, sources, sectors

def create_demo_data():
    """Crée des données de démonstration pour le développement"""
    # Textes d'exemple
    texts = [
        "La CNESST recommande l'utilisation d'équipements de protection individuelle pour les travaux en hauteur.",
        "L'ASP Construction a publié un guide sur la prévention des chutes sur les chantiers.",
        "L'IRSST a mené une étude sur l'exposition aux poussières dans le secteur de la construction.",
        "Le programme de prévention de la CNESST inclut des mesures de contrôle des risques chimiques.",
        "Guide des bonnes pratiques en ergonomie pour le secteur manufacturier par l'IRSST.",
        "L'ASP Construction recommande des procédures de travail sécuritaires pour les travaux d'excavation.",
        "La CNESST a mis à jour ses directives concernant la prévention des troubles musculo-squelettiques.",
        "Étude de l'IRSST sur la prévention des risques psychosociaux dans le secteur de la santé.",
        "L'ASP Construction propose des fiches techniques sur l'utilisation sécuritaire des échafaudages.",
        "La CNESST exige une formation adéquate pour les travailleurs manipulant des produits dangereux."
    ]
    
    # Sources d'exemple
    sources = ["CNESST", "ASP Construction", "IRSST", "CNESST", "IRSST", 
               "ASP Construction", "CNESST", "IRSST", "ASP Construction", "CNESST"]
    
    # Secteurs d'exemple
    sectors = ["Construction", "Construction", "Construction", "Général", "Manufacturier",
               "Construction", "Général", "Santé", "Construction", "Général"]
    
    # URLs fictives
    urls = [f"https://exemple.com/document_{i}" for i in range(1, 11)]
    
    # Créer des embeddings aléatoires (dimension 384 pour paraphrase-multilingual-MiniLM-L12-v2)
    embeddings = np.random.rand(len(texts), 384).astype(np.float32)
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)  # Normaliser
    
    # Créer les métadonnées
    metadata = []
    for i in range(len(texts)):
        metadata.append({
            "id": i,
            "text": texts[i],
            "source": sources[i],
            "sector": sectors[i],
            "url": urls[i],
            "date_added": datetime.now().strftime("%Y-%m-%d")
        })
    
    return embeddings, metadata

def search_documents(query, index, metadata, model, top_k=10, source_filter=None, sector_filter=None):
    """Recherche sémantique dans les documents"""
    # Encoder la requête
    query_embedding = model.encode([query])[0]
    query_embedding = query_embedding / np.linalg.norm(query_embedding)  # Normaliser
    
    # Effectuer la recherche
    k = min(top_k * 3, index.ntotal)  # Rechercher plus de résultats pour permettre le filtrage
    scores, indices = index.search(np.array([query_embedding]).astype(np.float32), k=k)
    
    # Filtrer et formater les résultats
    results = []
    for i, idx in enumerate(indices[0]):
        if idx == -1:  # Faiss retourne -1 si moins de k résultats sont trouvés
            continue
            
        item = metadata[idx]
        
        # Appliquer les filtres
        if source_filter and item["source"] not in source_filter:
            continue
            
        if sector_filter and ("sector" in item and item["sector"] not in sector_filter):
            continue
            
        # Ajouter le score de similarité
        result = item.copy()
        result["score"] = float(scores[0][i])
        results.append(result)
        
        # Arrêter une fois que nous avons assez de résultats après filtrage
        if len(results) >= top_k:
            break
    
    return results

def highlight_query_terms(text, query_terms, max_length=300):
    """Met en évidence les termes de la requête dans le texte et tronque si nécessaire"""
    query_terms = query_terms.lower().split()
    
    # Tronquer le texte si nécessaire
    if len(text) > max_length:
        # Trouver la première occurrence d'un terme de recherche
        first_pos = len(text)
        for term in query_terms:
            pos = text.lower().find(term)
            if pos != -1 and pos < first_pos:
                first_pos = pos
        
        # Déterminer les limites de la troncature
        start = max(0, first_pos - 100)
        end = min(len(text), start + max_length)
        
        # Ajuster pour ne pas couper un mot
        if start > 0:
            start = text.rfind(" ", 0, start) + 1
        
        if end < len(text):
            end = text.rfind(" ", end - 50, end)
            if end == -1:  # Si pas d'espace trouvé
                end = min(len(text), start + max_length)
        
        truncated_text = ("..." if start > 0 else "") + text[start:end] + ("..." if end < len(text) else "")
    else:
        truncated_text = text
    
    # Mettre en évidence les termes de recherche
    highlighted_text = truncated_text
    for term in query_terms:
        if len(term) > 2:  # Ignorer les termes trop courts
            pattern = term
            replacement = f"<span class='highlight'>{term}</span>"
            highlighted_text = highlighted_text.replace(pattern, replacement)
            # Aussi essayer avec la première lettre en majuscule
            pattern_cap = term.capitalize()
            replacement_cap = f"<span class='highlight'>{pattern_cap}</span>"
            highlighted_text = highlighted_text.replace(pattern_cap, replacement_cap)
    
    return highlighted_text

def format_results(results, query):
    """Formate les résultats pour l'affichage"""
    if not results:
        st.info("Aucun résultat trouvé pour cette requête. Essayez de modifier vos termes de recherche ou vos filtres.")
        return
    
    for result in results:
        with st.container():
            st.markdown(f"""
            <div class="result-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
                    <div>
                        <span class="source-tag">{result['source']}</span>
                        {f'<span class="source-tag">{result["sector"]}</span>' if 'sector' in result else ''}
                    </div>
                    <span class="score-badge">Score: {result['score']:.2f}</span>
                </div>
                <div style="margin-bottom: 0.5rem;">
                    {highlight_query_terms(result['text'], query)}
                </div>
                <div style="text-align: right;">
                    <a href="{result['url']}" target="_blank" style="color: #2563EB; text-decoration: none; font-size: 0.8rem;">
                        Voir la source originale →
                    </a>
                </div>
            </div>
            """, unsafe_allow_html=True)

def display_source_distribution(metadata, source_filter=None):
    """Affiche la distribution des sources dans les données"""
    # Compter les occurrences de chaque source
    source_counts = {}
    for item in metadata:
        source = item["source"]
        if source_filter and source not in source_filter:
            continue
        source_counts[source] = source_counts.get(source, 0) + 1
    
    # Créer un DataFrame pour Plotly
    df = pd.DataFrame({
        "Source": list(source_counts.keys()),
        "Nombre de documents": list(source_counts.values())
    })
    
    # Trier par nombre de documents
    df = df.sort_values("Nombre de documents", ascending=False)
    
    # Créer le graphique
    fig = px.bar(
        df, 
        x="Source", 
        y="Nombre de documents",
        color="Source",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        labels={"Source": "Source", "Nombre de documents": "Nombre de documents"}
    )
    
    # Personnaliser le graphique
    fig.update_layout(
        plot_bgcolor="white",
        xaxis_title="",
        yaxis_title="Nombre de documents",
        xaxis={'categoryorder':'total descending'}
    )
    
    return fig

def display_metrics(metadata, results=None):
    """Affiche les métriques principales"""
    st.markdown("""
    <div class="metrics-container">
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Documents</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Sources</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Secteurs</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Résultats</div>
        </div>
    </div>
    """.format(
        len(metadata),
        len(set(item["source"] for item in metadata)),
        len(set(item.get("sector", "Non spécifié") for item in metadata)),
        len(results) if results else 0
    ), unsafe_allow_html=True)

# Interface principale
def main():
    # Afficher le header
    st.markdown('<div class="main-header">🛡️ GAIN</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">GenAISafety Agentic Intelligence Network</div>', unsafe_allow_html=True)
    
    # Charger le modèle et les données
    model = load_model()
    embeddings, metadata, index, sources, sectors = load_data()
    
    # Barre latérale pour les filtres
    with st.sidebar:
        st.markdown('<div class="sidebar-header">Filtres de recherche</div>', unsafe_allow_html=True)
        
        # Filtre par source
        st.markdown("**Sources**")
        selected_sources = []
        for source in sources:
            if st.checkbox(source, value=True, key=f"source_{source}"):
                selected_sources.append(source)
        
        # Filtre par secteur (si disponible)
        if sectors:
            st.markdown("**Secteurs**")
            selected_sectors = []
            for sector in sectors:
                if st.checkbox(sector, value=True, key=f"sector_{sector}"):
                    selected_sectors.append(sector)
        else:
            selected_sectors = None
        
        # Nombre de résultats
        top_k = st.slider("Nombre de résultats", min_value=5, max_value=50, value=10, step=5)
        
        # Informations sur les données
        st.markdown("---")
        st.markdown('<div class="sidebar-header">Statistiques</div>', unsafe_allow_html=True)
        st.markdown(f"**Total documents:** {len(metadata)}")
        st.markdown(f"**Sources uniques:** {len(sources)}")
        if sectors:
            st.markdown(f"**Secteurs uniques:** {len(sectors)}")
        
        # Afficher un graphique de distribution des sources
        st.markdown("---")
        st.markdown('<div class="sidebar-header">Distribution des sources</div>', unsafe_allow_html=True)
        fig = display_source_distribution(metadata, selected_sources)
        st.plotly_chart(fig, use_container_width=True)
    
    # Barre de recherche
    query = st.text_input("Rechercher dans la base de connaissances SST...", placeholder="Ex: prévention des chutes, équipements de protection, risques chimiques...")
    
    # Afficher les résultats de recherche
    results = []
    if query:
        with st.spinner("Recherche en cours..."):
            results = search_documents(
                query=query,
                index=index,
                metadata=metadata,
                model=model,
                top_k=top_k,
                source_filter=selected_sources,
                sector_filter=selected_sectors if 'selected_sectors' in locals() else None
            )
        
        # Afficher les métriques
        display_metrics(metadata, results)
        
        # Afficher les résultats
        st.markdown('<div class="sub-header">Résultats</div>', unsafe_allow_html=True)
        format_results(results, query)
    else:
        # Afficher les métriques initiales
        display_metrics(metadata)
        
        # Afficher un message d'accueil
        st.info("👋 Bienvenue dans GAIN (GenAISafety Agentic Intelligence Network) pour la recherche SST Québec. "
                "Entrez votre requête dans la barre de recherche pour explorer la base de connaissances.")
        
        # Afficher quelques exemples de recherche
        st.markdown("### Exemples de recherche")
        example_queries = [
            "prévention des chutes",
            "équipements de protection individuelle",
            "risques chimiques",
            "ergonomie au travail",
            "formation sécurité"
        ]
        
        cols = st.columns(len(example_queries))
        for i, col in enumerate(cols):
            if col.button(example_queries[i]):
                st.experimental_rerun()  # Cette fonction est dépréciée mais encore fonctionnelle, à remplacer par st.rerun() dans les versions récentes de Streamlit
    
    # Footer
    st.markdown("""
    <div class="footer">
        GAIN (GenAISafety Agentic Intelligence Network) | Interface de recherche sémantique SST Québec | © 2025
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()