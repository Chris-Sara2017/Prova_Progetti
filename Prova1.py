from datetime import date
import json
import os
from google import genai
import streamlit as st

# Configurazione della pagina Streamlit
st.set_page_config(
    page_title="Gestore Progetti Ingegneristici", page_icon="🏗️", layout="wide"
)

# Nomi dei file di persistenza locale
DATA_FILE = "progetto_dati.json"
CONFIG_FILE = "fasi_config.json"


def carica_config_fasi():
  """Carica la configurazione standard di fasi e sottofasi o restituisce un default ingegneristico."""
  if os.path.exists(CONFIG_FILE):
    try:
      with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    except Exception as e:
      st.error(f"Errore nella lettura del file di configurazione fasi: {e}")

  return {
      "Studio di Fattibilità": [
          "Analisi preliminare vincoli",
          "Valutazione economica di massima",
          "Sopralluogo tecnico",
      ],
      "Progettazione Preliminare": [
          "Layout impiantistico",
          "Relazione tecnica di base",
          "Stima dimensionamento componenti",
      ],
      "Progettazione Esecutiva": [
          "Disegni costruttivi dettagliati",
          "Specifiche tecniche materiali",
          "Computo metrico estimativo",
      ],
      "Installazione e Cantiere": [
          "Allestimento area di lavoro",
          "Montaggio strutturale/meccanico",
          "Cablaggi e connessioni elettriche",
      ],
      "Collaudo e Avviamento": [
          "Test funzionali a freddo",
          "Commissioning e messa in servizio",
          "Rilascio documentazione finale",
      ],
  }


def salva_config_fasi(config):
  """Salva la configurazione delle fasi nel file JSON dedicato."""
  try:
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
      json.dump(config, f, indent=4, ensure_ascii=False)
  except Exception as e:
    st.error(f"Errore durante il salvataggio della configurazione fasi: {e}")


def carica_dati():
  """Carica i dati del progetto dal file JSON o restituisce una struttura di default."""
  if os.path.exists(DATA_FILE):
    try:
      with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    except Exception as e:
      st.error(f"Errore durante la lettura del file di progetto: {e}")

  return {
      "progetto": "Nuovo Progetto Impiantistico",
      "elementi": [
          {
              "fase": "Studio di Fattibilità",
              "sottofase": "Analisi preliminare vincoli",
              "data_inizio": "2026-03-01",
              "data_fine": "2026-03-15",
              "stato": "Completato",
              "commenti": "Verificati i carichi e le normative locali.",
              "file_allegato": "nessuno",
          }
      ],
  }


def salva_dati(dati):
  """Salva i dati di progetto aggiornati nel file JSON."""
  try:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
      json.dump(dati, f, indent=4, ensure_ascii=False)
  except Exception as e:
    st.error(f"Errore durante il salvataggio dei dati di progetto: {e}")


# Inizializzazione sicura dello stato della sessione
if "dati_progetto" not in st.session_state:
  st.session_state.dati_progetto = carica_dati()

if "config_fasi" not in st.session_state:
  st.session_state.config_fasi = carica_config_fasi()

# --- MENU DI NAVIGAZIONE ---
st.sidebar.title("🧭 Navigazione Progetto")
scelta_pagina = st.sidebar.radio(
    "Seleziona la sezione:",
    [
        "🏠 Home / Scelta",
        "📝 Inserimento e Modifica Dati",
        "⚙️ Configurazione Fasi (Admin)",
        "📊 Consultazione & IA",
    ],
)

dati = st.session_state.dati_progetto
config_fasi = st.session_state.config_fasi

if scelta_pagina == "🏠 Home / Scelta":
  st.title("🏗️ Dashboard Ingegneristica Integrata")
  st.markdown("""
        Benvenuto nel pannello di controllo centrale. Utilizza il menu laterale per navigare tra:
        - **Inserimento e Modifica Dati**: Per gestire le attività selezionando fasi e sottofasi standardizzate, date, commenti e allegati.
        - **Configurazione Fasi (Admin)**: Area protetta da password per personalizzare l'alberatura delle fasi e delle relative sottofasi (con opzioni di aggiunta ed eliminazione puntuale).
        - **Consultazione & IA**: Per analizzare lo stato del database e interrogare l'intelligenza artificiale di Google Gemini per audit tecnici.
        """)
  st.info(f"Progetto attualmente in gestione: **{dati.get('progetto')}**")

elif scelta_pagina == "📝 Inserimento e Modifica Dati":
  st.title("📝 Inserimento e Gestione Dati di Progetto")
  st.markdown(
      "Compilare i campi sottostanti selezionando fasi e sottofasi dal catalogo"
      " autorizzato."
  )

  dati["progetto"] = st.text_input(
      "Nome del Progetto", value=dati.get("progetto", "")
  )

  st.divider()
  st.subheader("Elenco Attività / Fasi")

  if "elementi" not in dati:
    dati["elementi"] = []

  if st.button("➕ Aggiungi Nuova Fase/Sottofase", type="primary"):
    prime_fasi = list(config_fasi.keys())
    fase_default = prime_fasi[0] if prime_fasi else "Altro"
    sottofasi_default = config_fasi.get(fase_default, ["Generico"])
    sottofase_default = (
        sottofasi_default[0] if sottofasi_default else "Generico"
    )

    dati["elementi"].append({
        "fase": fase_default,
        "sottofase": sottofase_default,
        "data_inizio": str(date.today()),
        "data_fine": str(date.today()),
        "stato": "Da Iniziare",
        "commenti": "",
        "file_allegato": "nessuno",
    })
    st.rerun()

  lista_fasi_disponibili = list(config_fasi.keys())

  for i, el in enumerate(dati["elementi"]):
    with st.expander(
        f"Fase {i+1}: {el.get('fase', '')} - Sottofase:"
        f" {el.get('sottofase', '')}",
        expanded=True,
    ):
      col1, col2 = st.columns(2)

      with col1:
        fase_attuale = el.get("fase", "")
        if fase_attuale not in lista_fasi_disponibili:
          fase_attuale = (
              lista_fasi_disponibili[0] if lista_fasi_disponibili else ""
          )

        idx_fase = lista_fasi_disponibili.index(fase_attuale)
        scelta_fase = st.selectbox(
            "Fase Principale",
            lista_fasi_disponibili,
            index=idx_fase,
            key=f"fase_{i}",
        )
        el["fase"] = scelta_fase

        sottofasi_disponibili = config_fasi.get(scelta_fase, ["Generico"])
        sottofase_attuale = el.get("sottofase", "")
        if sottofase_attuale not in sottofasi_disponibili:
          sottofase_attuale = sottofasi_disponibili[0]

        idx_sottofase = (
            sottofasi_disponibili.index(sottofase_attuale)
            if sottofase_attuale in sottofasi_disponibili
            else 0
        )
        el["sottofase"] = st.selectbox(
            "Sottofase",
            sottofasi_disponibili,
            index=idx_sottofase,
            key=f"sottofase_{i}",
        )

        stati_disponibili = [
            "Da Iniziare",
            "In Corso",
            "Completato",
            "Sospeso",
        ]
        stato_attuale = el.get("stato", "Da Iniziare")
        idx_stato = (
            stati_disponibili.index(stato_attuale)
            if stato_attuale in stati_disponibili
            else 0
        )
        el["stato"] = st.selectbox(
            "Stato", stati_disponibili, index=idx_stato, key=f"stato_{i}"
        )

      with col2:
        try:
          d_inizio_val = date.fromisoformat(
              el.get("data_inizio", str(date.today()))
          )
        except:
          d_inizio_val = date.today()

        try:
          d_fine_val = date.fromisoformat(
              el.get("data_fine", str(date.today()))
          )
        except:
          d_fine_val = date.today()

        d_inizio = st.date_input(
            "Data Inizio", value=d_inizio_val, key=f"dinizio_{i}"
        )
        d_fine = st.date_input(
            "Data Fine Prevista", value=d_fine_val, key=f"dfine_{i}"
        )

        el["data_inizio"] = str(d_inizio)
        el["data_fine"] = str(d_fine)

      el["commenti"] = st.text_area(
          "Commenti e Note Tecniche",
          value=el.get("commenti", ""),
          key=f"comm_{i}",
      )

      uploaded_file = st.file_uploader(
          f"Allega documento tecnico (Fase {i+1})", key=f"file_up_{i}"
      )
      if uploaded_file is not None:
        os.makedirs("allegati", exist_ok=True)
        file_path = os.path.join("allegati", uploaded_file.name)
        with open(file_path, "wb") as f:
          f.write(uploaded_file.getbuffer())
        el["file_allegato"] = uploaded_file.name
        st.success(f"File '{uploaded_file.name}' allegato con successo!")
      else:
        if "file_allegato" not in el:
          el["file_allegato"] = "nessuno"

      if st.button(f"🗑️ Rimuovi Fase {i+1}", key=f"del_{i}"):
        dati["elementi"].pop(i)
        st.rerun()

  st.divider()

  if st.button("💾 Salva Modifiche nel Database JSON", type="primary"):
    salva_dati(dati)
    st.success("Database aggiornato e salvato correttamente su file JSON!")

elif scelta_pagina == "⚙️ Configurazione Fasi (Admin)":
  st.title("⚙️ Area Amministrativa: Configurazione Fasi e Sottofasi")
  st.markdown(
      "Inserisci la password di sicurezza per modificare, aggiungere o"
      " eliminare fasi e singole sottofasi."
  )

  password_inserita = st.text_input(
      "Password di Accesso Admin", type="password"
  )
  PASSWORD_CORRETTA = "ingegneria2026"

  if password_inserita == PASSWORD_CORRETTA:
    st.success(
        "🔓 Autenticazione riuscita. Gestione configurazione attiva."
    )
    st.divider()

    st.subheader("Catalogo Attuale Fasi e Sottofasi")

    fasi_da_rimuovere = []

    for fase_nome, sottofasi_lista in list(config_fasi.items()):
      with st.expander(f"Fase: {fase_nome} ({len(sottofasi_lista)} sottofasi)"):
        nuovo_nome_fase = st.text_input(
            f"Rinomina Fase", value=fase_nome, key=f"rename_fase_{fase_nome}"
        )

        st.markdown("*Sottofasi collegate (modificabili o eliminabili):*")
        nuove_sottofasi = []
        sottofasi_da_eliminare = []

        for j, sub in enumerate(sottofasi_lista):
          col_sub1, col_sub2 = st.columns([0.8, 0.2])
          with col_sub1:
            s_mod = st.text_input(
                f"Sottofase {j+1}",
                value=sub,
                key=f"sub_{fase_nome}_{j}",
                label_visibility="collapsed",
            )
          with col_sub2:
            # Pulsante per marcare la singola sottofase per l'eliminazione
            if st.button(
                "❌ Elimina", key=f"del_sub_{fase_nome}_{j}"
            ):
              sottofasi_da_eliminare.append(sub)

          if s_mod.strip() and sub not in sottofasi_da_eliminare:
            nuove_sottofasi.append(s_mod.strip())

        # Gestione aggiunta nuova sottofase
        aggiungi_sub = st.text_input(
            f"➕ Aggiungi nuova sottofase a {fase_nome}",
            key=f"add_sub_{fase_nome}",
        )
        if aggiungi_sub.strip() and aggiungi_sub.strip() not in nuove_sottofasi:
          nuove_sottofasi.append(aggiungi_sub.strip())

        # Sincronizzazione nel dizionario temporaneo
        if nuovo_nome_fase != fase_nome:
          config_fasi[nuovo_nome_fase] = nuove_sottofasi
          del config_fasi[fase_nome]
        else:
          config_fasi[fase_nome] = nuove_sottofasi

        if st.button(
            f"🗑️ Elimina Intera Fase '{fase_nome}'", key=f"del_f_{fase_nome}"
        ):
          fasi_da_rimuovere.append(fase_nome)

    for f_rem in fasi_da_rimuovere:
      del config_fasi[f_rem]
      st.rerun()

    st.divider()
    st.subheader("➕ Aggiungi Nuova Fase Principale")
    nuova_fase_titolo = st.text_input("Nome della nuova fase principale")
    if st.button("Crea Nuova Fase"):
      if nuova_fase_titolo.strip() and nuova_fase_titolo not in config_fasi:
        config_fasi[nuova_fase_titolo.strip()] = ["Sottofase Iniziale"]
        st.success(f"Fase '{nuova_fase_titolo}' aggiunta con successo!")
        st.rerun()

    if st.button("💾 Salva Configurazione Fasi", type="primary"):
      salva_config_fasi(config_fasi)
      st.session_state.config_fasi = config_fasi
      st.success(
          "Configurazione salvata nel file 'fasi_config.json' con successo!"
      )

  elif password_inserita != "":
    st.error("❌ Password errata. Accesso negato all'area amministrativa.")
  else:
    st.info("ℹ️ Digita la password per sbloccare la gestione delle fasi.")

elif scelta_pagina == "📊 Consultazione & IA":
  st.title("📊 Consultazione Database & Assistente IA")
  st.markdown(
      "Visualizza lo stato attuale del progetto ed esegui un'analisi tecnica"
      " avanzata tramite l'intelligenza artificiale."
  )

  st.subheader("Riepilogo Struttura Dati Progetto")
  st.json(dati)

  st.divider()

  st.subheader("🤖 Analisi e Audit Tecnico con Google GenAI")

  api_key = None
  if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
  else:
    api_key = os.environ.get("GEMINI_API_KEY")

  if st.button("Esegui Audit e Analisi con IA"):
    if not api_key:
      st.error("⚠️ Chiave API di Gemini non configurata nei secrets.")
    else:
      with st.spinner(
          "L'intelligenza artificiale sta analizzando le fasi e i commenti"
          " tecnici..."
      ):
        try:
          client = genai.Client(api_key=api_key)
          contenuto_json = json.dumps(dati, indent=4, ensure_ascii=False)

          prompt = f"""
                    Sei un ingegnere capo project manager senior.
                    Esamina il seguente database di progetto in formato JSON:
                    {contenuto_json}
                    
                    Fornisci un report di audit tecnico approfondito che includa:
                    1. Valutazione della coerenza delle tempistiche (date di inizio e fine).
                    2. Analisi dei commenti e identificazione di eventuali criticità o colli di bottiglia operativi.
                    3. Tre raccomandazioni ingegneristiche mirate all'ottimizzazione del piano di lavoro.
                    """

          response = client.models.generate_content(
              model="gemini-2.5-flash", contents=prompt
          )

          st.success("Audit completato con successo!")
          st.markdown(response.text)

        except Exception as e:
          st.error(
              "Si è verificato un errore durante la comunicazione con il"
              f" modello IA: {e}"
          )