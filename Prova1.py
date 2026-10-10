import streamlit as st
import json
import os
from datetime import datetime

# Configurazione della pagina web
st.set_page_config(
    page_title="Gestione Progetti Complessi",
    page_icon="📊",
    layout="wide"
)

FILE_DATI = "progetto_dati.json"

def carica_dati():
    """Carica i dati del progetto dal file JSON o inizializza una struttura di base."""
    if os.path.exists(FILE_DATI):
        with open(FILE_DATI, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "nome_progetto": "Progetto Ingegneristico Avanzato",
        "fasi": [
            {"fase": "Fattibilità e Normativa", "scadenza": "2026-06-30", "documenti": [], "commenti": []},
            {"fase": "Progettazione Esecutiva", "scadenza": "2026-09-15", "documenti": [], "commenti": []}
        ]
    }

def salva_dati(dati):
    """Salva lo stato corrente sul disco."""
    with open(FILE_DATI, "w", encoding="utf-8") as f:
        json.dump(dati, f, indent=4, ensure_ascii=False)

if "dati" not in st.session_state:
    st.session_state.dati = carica_dati()

# --- INTERFACCIA WEB (FRONTEND) ---
st.title("🚀 Dashboard Gestione Progetti Complessi")
st.markdown("Piattaforma interna per il tracciamento delle fasi, archiviazione documenti e note tecniche.")

dati = st.session_state.dati

# Sidebar per la gestione globale o aggiunta nuove fasi
st.sidebar.header("⚙️ Pannello di Controllo")
nuova_fase_nome = st.sidebar.text_input("Nome Nuova Fase")
nuova_scadenza = st.sidebar.date_input("Data di Scadenza")

if st.sidebar.button("➕ Aggiungi Fase"):
    if nuova_fase_nome:
        dati["fasi"].append({
            "fase": nuova_fase_nome,
            "scadenza": str(nuova_scadenza),
            "documenti": [],
            "commenti": []
        })
        salva_dati(dati)
        st.sidebar.success(f"Fase '{nuova_fase_nome}' aggiunta con successo!")
        st.rerun()
    else:
        st.sidebar.error("Inserisci un nome valido per la fase.")

# Visualizzazione delle fasi in schede interattive
st.subheader(f"📁 Progetto: {dati['nome_progetto']}")
st.divider()

if not dati["fasi"]:
    st.info("Nessuna fase presente. Utilizza la barra laterale per aggiungerne una.")

for i, fase in enumerate(dati["fasi"]):
    with st.expander(f"📌 Fase {i+1}: {fase['fase']} (Scadenza: {fase['scadenza']})", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📂 Documenti Archiviati")
            if fase["documenti"]:
                for doc in fase["documenti"]:
                    st.text(f"• {doc}")
            else:
                st.caption("Nessun documento associato.")
                
            nuovo_doc = st.text_input(f"Aggiungi percorso file (Fase {i+1})", key=f"doc_input_{i}")
            if st.button("Salva Documento", key=f"btn_doc_{i}"):
                if nuovo_doc:
                    fase["documenti"].append(nuovo_doc)
                    salva_dati(dati)
                    st.success("Documento archiviato!")
                    st.rerun()

        with col2:
            st.markdown("### 💬 Commenti e Note Tecniche")
            if fase["commenti"]:
                for comm in fase["commenti"]:
                    st.info(f"**[{comm['timestamp']}]** {comm['testo']}")
            else:
                st.caption("Nessun commento registrato.")
                
            nuovo_commento = st.text_area(f"Scrivi un commento (Fase {i+1})", key=f"comm_input_{i}")
            if st.button("Invia Commento", key=f"btn_comm_{i}"):
                if nuovo_commento:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                    fase["commenti"].append({"timestamp": timestamp, "testo": nuovo_commento})
                    salva_dati(dati)
                    st.success("Commento aggiunto!")
                    st.rerun()