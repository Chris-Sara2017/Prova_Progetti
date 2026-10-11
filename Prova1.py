import json
import os
from google import genai
import streamlit as st

# Configurazione della pagina Streamlit
st.set_page_config(
    page_title="Gestore Progetti Ingegneristici", page_icon="📊", layout="wide"
)

# Nome del file di persistenza locale per i dati
DATA_FILE = "progetto_dati.json"


def carica_dati():
  """Carica i dati dal file JSON o restituisce una struttura di default."""
  if os.path.exists(DATA_FILE):
    try:
      with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    except Exception as e:
      st.error(f"Errore durante la lettura del file JSON: {e}")
  # Struttura di default nel caso il file non esista
  return {
      "progetto": "Nuovo Progetto Ingegneristico",
      "fasi": [
          {
              "nome": "Fase 1: Studio di Fattibilità",
              "stato": "Completato",
              "note": "Analisi preliminare completata.",
          },
          {
              "nome": "Fase 2: Progettazione Esecutiva",
              "stato": "In Corso",
              "note": "Definizione specifiche tecniche.",
          },
      ],
  }


def salva_dati(dati):
  """Salva i dati aggiornati nel file JSON."""
  try:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
      json.dump(dati, f, indent=4, ensure_ascii=False)
  except Exception as e:
    st.error(f"Errore durante il salvataggio dei dati: {e}")


# Inizializzazione dello stato della sessione
if "dati_progetto" not in st.session_state:
  st.session_state.dati_progetto = carica_dati()

# --- INTERFACCIA GRAFICA PRINCIPALE ---
st.title("📊 Dashboard Gestione Progetti & Assistente IA")
st.markdown(
    "Benvenuto nel tuo pannello di controllo ingegneristico. Gestisci le fasi"
    " del progetto e sfrutta l'intelligenza artificiale per l'analisi dei"
    " rischi e dei flussi di lavoro."
)

# Visualizzazione dati correnti
progetto = st.session_state.dati_progetto

st.subheader(f"📁 Progetto: {progetto.get('progetto', 'Senza Nome')}")

# Tabella interattiva o visualizzazione delle fasi
st.markdown("### Stato Avanzamento Fasi")
for i, fase in enumerate(progetto.get("fasi", [])):
  col1, col2, col3 = st.columns([3, 2, 4])
  with col1:
    st.text(fase["nome"])
  with col2:
    # Selezione dello stato
    nuovo_stato = st.selectbox(
        f"Stato_{i}",
        ["Da Iniziare", "In Corso", "Completato"],
        index=["Da Iniziare", "In Corso", "Completato"].index(
            fase.get("stato", "Da Iniziare")
        )
        if fase.get("stato") in ["Da Iniziare", "In Corso", "Completato"]
        else 0,
        key=f"stato_{i}",
    )
    progetto["fasi"][i]["stato"] = nuovo_stato
  with col3:
    nuove_note = st.text_input(
        f"Note_{i}", value=fase.get("note", ""), key=f"note_{i}"
    )
    progetto["fasi"][i]["note"] = nuove_note

# Pulsante per salvare le modifiche nel file JSON locale
if st.button("Salva Modifiche Progetto"):
  salva_dati(st.session_state.dati_progetto)
  st.success("Dati salvati correttamente nel file JSON!")

st.divider()

# --- SEZIONE INTELLIGENZA ARTIFICIALE (GOOGLE GENAI) ---
st.subheader("🤖 Assistente IA per Analisi Ingegneristica")
st.markdown(
    "Interroga il modello avanzato di Google per ottenere un'analisi"
    " strutturata dello stato di avanzamento e suggerimenti operativi."
)

# Configurazione del client Gemini
# Legge la chiave in modo sicuro dai secrets di Streamlit (locale o cloud) oppure dalle variabili d'ambiente
api_key = None
if "GEMINI_API_KEY" in st.secrets:
  api_key = st.secrets["GEMINI_API_KEY"]
else:
  api_key = os.environ.get("GEMINI_API_KEY")

if st.button("Genera Analisi con IA"):
  if not api_key:
    st.error(
        "⚠️ Chiave API di Gemini non configurata! Aggiungila nel file"
        " `.streamlit/secrets.toml` o nelle impostazioni di Streamlit Cloud."
    )
  else:
    with st.spinner(
        "L'intelligenza artificiale sta elaborando i dati di progetto..."
    ):
      try:
        client = genai.Client(api_key=api_key)

        # Leggiamo il contenuto attuale del file JSON
        if os.path.exists(DATA_FILE):
          with open(DATA_FILE, "r", encoding="utf-8") as f:
            contenuto_json = f.read()
        else:
          contenuto_json = str(st.session_state.dati_progetto)

        # Prompt ingegneristico specializzato
        prompt = f"""
                Sei un project manager senior e consulente ingegneristico industriale.
                Analizza i seguenti dati di progetto in formato JSON:
                {contenuto_json}
                
                Fornisci un report professionale e dettagliato che includa:
                1. Un giudizio sintetico sullo stato di avanzamento complessivo.
                2. Una valutazione critica dei potenziali colli di bottiglia o rischi operativi.
                3. Tre raccomandazioni tecniche e strategiche per ottimizzare le tempistiche e i flussi di lavoro.
                """

        # Chiamata al modello Gemini (es. gemini-2.5-flash)
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )

        st.success("Analisi completata con successo!")
        st.markdown(response.text)

      except Exception as e:
        st.error(f"Si è verificato un errore durante la chiamata all'IA: {e}")