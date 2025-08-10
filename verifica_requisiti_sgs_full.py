
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Verifica requisiti Settore Tecnico - Club Giovanili SGS Sicilia", layout="wide")

# Titolo
st.title("Verifica requisiti Settore Tecnico - Club Giovanili SGS Sicilia")
st.write("Inserisci il numero di squadre per ciascuna categoria (barra laterale), poi compila i tecnici.")

# Costanti
CATEGORIES = ["Allievi", "Giovanissimi", "Esordienti", "Pulcini", "Primi Calci", "Piccoli Amici"]
QUALIFICATIONS = ["Uefa A", "Uefa B", "Uefa C", "Scienze Motorie", "E-Level"]

# Sidebar: numero squadre per categoria
st.sidebar.header("Configurazione: numero squadre")
num_teams = {}
for cat in CATEGORIES:
    num_teams[cat] = st.sidebar.number_input(cat, min_value=0, value=0, step=1, key=f"n_{cat}")

st.markdown("---")

# Responsabile Tecnico (prima domanda nel form principale)
st.header("Responsabile Tecnico Settore Giovanile (RT)")
rt_cols = st.columns(3)
rt_nome = rt_cols[0].text_input("Nome RT", key="rt_nome")
rt_cognome = rt_cols[1].text_input("Cognome RT", key="rt_cognome")
rt_qualifica = rt_cols[2].selectbox("Qualifica RT", QUALIFICATIONS, key="rt_qual")

st.markdown("---")
st.header("Inserimento dati tecnici per ogni squadra")

# Raccogliere i dati dei tecnici
teams_data = {cat: [] for cat in CATEGORIES}

for cat in CATEGORIES:
    n = num_teams[cat]
    if n == 0:
        continue
    st.subheader(f"{cat} — {n} squadra{'e' if n>1 else ''}")
    for i in range(n):
        with st.expander(f"{cat} — Squadra {i+1}", expanded=(i==0)):
            cols = st.columns([2,2,2,2])
            nome = cols[0].text_input("Nome", key=f"nome_{cat}_{i}")
            cognome = cols[1].text_input("Cognome", key=f"cognome_{cat}_{i}")
            qual = cols[2].selectbox("Qualifica federale", QUALIFICATIONS, key=f"qual_{cat}_{i}")
            note = cols[3].text_input("Note (opz.)", key=f"note_{cat}_{i}")
            teams_data[cat].append({
                "nome": nome.strip(),
                "cognome": cognome.strip(),
                "qualifica": qual,
                "note": note.strip(),
                "categoria": cat,
                "squadra_index": i+1
            })

# Helper per identificare un tecnico
def id_tecnico(t):
   return f"{t['cognome'].strip().lower()}_{t['nome'].strip().lower()}"


# Funzione per mostrare messaggi di errore in lista
def mostra_errori(errors):
    st.error("❌ Criticità riscontrate:")
    for e in errors:
        st.write("- " + e)

# Bottone per eseguire la verifica
if st.button("Esegui verifica"):
    errors = []

    # Validazione RT: campi obbligatori
    if rt_nome.strip() == "" or rt_cognome.strip() == "" or rt_qualifica.strip() == "":
        errors.append("Responsabile Tecnico non compilato completamente (nome, cognome o qualifica vuoti).")

    # RT non può avere qualifica E-Level o Scienze Motorie
    if rt_qualifica in ["E-Level", "Scienze Motorie"]:
        errors.append("Il Responsabile Tecnico non può avere qualifica E-Level o Scienze Motorie.")

    # Costruisco liste per controlli
    # 1) Allievi + Giovanissimi: tutti i tecnici (tutte le squadre) devono essere diversi tra loro e non avere Scienze Motorie o E-Level
    ag_list = []
    for cat in ["Allievi", "Giovanissimi"]:
        for t in teams_data.get(cat, []):
            if t["nome"] == "" and t["cognome"] == "":
                continue
            ag_list.append((id_tecnico(t), t))

    ag_ids = [x[0] for x in ag_list]
    if len(ag_ids) != len(set(ag_ids)):
        errors.append("Nei settori Allievi e Giovanissimi ci sono tecnici ripetuti (stesso Nome+Cognome).")

    for _id, t in ag_list:
        if t["qualifica"] in ["Scienze Motorie", "E-Level"]:
            errors.append(f"{t['cognome']} {t['nome']} in {t['categoria']} ha qualifica non permessa ({t['qualifica']}).")


    # 2) Controllo Esordienti e Pulcini: nessun tecnico (tutte le squadre) può avere Scienze Motorie
    for cat in ["Esordienti", "Pulcini"]:
        for t in teams_data.get(cat, []):
            if t["nome"] == "" and t["cognome"] == "":
                continue
            if t["qualifica"] == "Scienze Motorie":
                errors.append(f"{t['cognome']} {t['nome']} in {cat} ha qualifica Scienze Motorie non permessa.")


    # 3) Prime squadre di Esordienti, Pulcini, Primi Calci, Piccoli Amici
    base_cats = ["Esordienti", "Pulcini", "Primi Calci", "Piccoli Amici"]
    prime_list = []
    for cat in base_cats:
        if len(teams_data.get(cat, [])) > 0:
            t = teams_data[cat][0]
            # Controllo che la prima squadra sia compilata
            if t["nome"] == "" and t["cognome"] == "":
                errors.append(f"Prima squadra di {cat} ha tecnico non compilato.")
            else:
                prime_list.append((id_tecnico(t), t))

    prime_ids = [x[0] for x in prime_list]
    # 3a) prime squadre devono essere diverse tra loro
    if len(prime_ids) != len(set(prime_ids)):
        errors.append("Le prime squadre delle categorie di base hanno tecnici ripetuti tra loro.")

    # 3b) prime squadre devono essere diverse da Allievi/Giovanissimi
    overlap = set(prime_ids) & set(ag_ids)
    if overlap:
        for ov in overlap:
            tname = None
            for _id, t in ag_list + prime_list:
                if _id == ov:
                    tname = f"{t['cognome']} {t['nome']}"
                    break
            errors.append(f"Il tecnico {tname} risulta sia tra Allievi/Giovanissimi sia come prima squadra di base.")

    # 3c) qualifiche prime squadre: Esordienti & Pulcini NON possono avere Scienze Motorie o E-Level;
    # Primi Calci & Piccoli Amici possono avere Scienze Motorie ma NON E-Level.
    for _id, t in prime_list:
        cat = t["categoria"]
        qual = t["qualifica"]
        if cat in ["Esordienti", "Pulcini"] and qual in ["Scienze Motorie", "E-Level"]:
            errors.append(f"{t['cognome']} {t['nome']} in {cat} (prima squadra) ha qualifica non permessa ({qual}).")
        if cat in ["Primi Calci", "Piccoli Amici"] and qual == "E-Level":
            errors.append(f"{t['cognome']} {t['nome']} in {cat} (prima squadra) ha qualifica E-Level non permessa (Scienze Motorie è ammessa).")

    # 4) RT non può coincidere con le prime squadre di Esordienti/Pulcini/Primi Calci/Piccoli Amici
    rt_id = f"{rt_cognome.strip().lower()}_{rt_nome.strip().lower()}"
    if rt_cognome.strip() != "" or rt_nome.strip() != "":
        for _id, t in prime_list:
            if rt_id == _id:
                errors.append("Il Responsabile Tecnico non può essere allenatore della prima squadra di Esordienti, Pulcini, Primi Calci o Piccoli Amici.")
                break

    # Output finale
    if not errors:
        st.success("✅ Il tuo modulo di presentazione può essere compilato correttamente.")
        # Mostro riepilogo e offro download CSV
        all_entries = [t for cat in CATEGORIES for t in teams_data.get(cat, []) if not (t['nome']=="\" and t['cognome']==\"")]
        if all_entries:
            df = pd.DataFrame(all_entries)
            st.subheader("Riepilogo tecnici") 
            st.dataframe(df)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(\"Scarica CSV\", csv, file_name="tecnici_squadre.csv", mime='text/csv')
    else:
        mostra_errori(errors)
        # Mostra riepilogo per debug
        all_entries = [t for cat in CATEGORIES for t in teams_data.get(cat, [])]
        if all_entries:
            df = pd.DataFrame(all_entries)
            with st.expander(\"Riepilogo dati inseriti (per debug)\"):
                st.dataframe(df)
                txt = df.to_json(orient='records', force_ascii=False, indent=2)
                st.code(txt)
