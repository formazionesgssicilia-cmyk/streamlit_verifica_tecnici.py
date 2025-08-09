import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Verifica Tecnici Squadre", layout="wide")
st.title("Verifica tecnici per categorie giovanili")

CATEGORIES = ["Allievi", "Giovanissimi", "Esordienti", "Pulcini", "Primi Calci", "Piccoli Amici"]
QUALIFICATIONS = ["UEFA A", "UEFA B", "UEFA C", "Istruttore Giovani Calciatori", "Scienze Motorie", "E-Level"]

st.markdown("\nInserisci il numero di squadre per ciascuna categoria, poi compila i dati dei tecnici.\n")

# Sidebar: numero squadre
st.sidebar.header("Configurazione: numero squadre")
num_teams = {}
for cat in CATEGORIES:
    num_teams[cat] = st.sidebar.number_input(cat, min_value=0, value=0, step=1, key=f"n_{cat}")

# Area principale: form per l'inserimento
st.header("Inserimento dati tecnici")

# We'll raccogliere i dati in una struttura
teams_data = {cat: [] for cat in CATEGORIES}

for cat in CATEGORIES:
    n = num_teams[cat]
    if n == 0:
        continue
    st.subheader(f"{cat} — {n} squadra{'e' if n>1 else ''}")
    for i in range(n):
        with st.expander(f"{cat} — Squadra {i+1}", expanded=(i==0)):
            cols = st.columns(4)
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

st.markdown("---")

# Funzione utili
def id_tecnico(t):
    return f"{t['cognome'].strip().lower()}_{t['nome'].strip().lower()}"

# Bottone di verifica
if st.button("Esegui verifica"):
    errors = []
    # 1) Allievi e Giovanissimi: tutti diversi e non Scienze Motorie/E-Level
    ag_list = []
    for cat in ["Allievi", "Giovanissimi"]:
        for t in teams_data.get(cat, []):
            if t["nome"] == "" and t["cognome"] == "":
                continue
            ag_list.append((id_tecnico(t), t))
    ag_ids = [x[0] for x in ag_list]
    if len(ag_ids) != len(set(ag_ids)):
        errors.append("Nei settori Allievi e Giovanissimi ci sono tecnici ripetuti (stesso Nome+Cognome).")
    for _, t in ag_list:
        if t["qualifica"] in ["Scienze Motorie", "E-Level"]:
            errors.append(f"{t['cognome']} {t['nome']} in {t['categoria']} ha qualifica non permessa ({t['qualifica']}).")

    # 2) Prime squadre di Esordienti, Pulcini, Primi Calci, Piccoli Amici
    base_cats = ["Esordienti", "Pulcini", "Primi Calci", "Piccoli Amici"]
    prime_list = []
    for cat in base_cats:
        if len(teams_data.get(cat, [])) > 0:
            t = teams_data[cat][0]
            if t["nome"] == "" and t["cognome"] == "":
                # consider empty as not provided — still count as missing
                errors.append(f"Prima squadra di {cat} ha tecnico non compilato.")
            else:
                prime_list.append((id_tecnico(t), t))
    prime_ids = [x[0] for x in prime_list]
    if len(prime_ids) != len(set(prime_ids)):
        errors.append("Le prime squadre delle categorie di base hanno tecnici ripetuti tra loro.")
    # Confronto con Allievi/Giovanissimi
    overlap = set(prime_ids) & set(ag_ids)
    if overlap:
        # riporta chi
        for ov in overlap:
            # trova entry
            tname = None
            for _id, t in ag_list + prime_list:
                if _id == ov:
                    tname = f"{t['cognome']} {t['nome']}"
                    break
            errors.append(f"Il tecnico {tname} risulta sia tra Allievi/Giovanissimi sia come prima squadra di base.")
    for _id, t in prime_list:
        if t["qualifica"] in ["Scienze Motorie", "E-Level"]:
            errors.append(f"{t['cognome']} {t['nome']} in {t['categoria']} (prima squadra) ha qualifica non permessa ({t['qualifica']}).")

    # 3) Esordienti e Pulcini -> non devono avere Scienze Motorie
    for cat in ["Esordienti", "Pulcini"]:
        for t in teams_data.get(cat, []):
            if t["nome"] == "" and t["cognome"] == "":
                continue
            if t["qualifica"] == "Scienze Motorie":
                errors.append(f"{t['cognome']} {t['nome']} in {cat} ha qualifica Scienze Motorie non permessa.")

    # Output
    if not errors:
        st.success("✅ Il tuo modulo di presentazione può essere compilato correttamente.")
        # Mostra riepilogo e offri download
        all_entries = [t for cat in CATEGORIES for t in teams_data.get(cat, []) if not (t['nome']=="" and t['cognome']=="")]
        if all_entries:
            df = pd.DataFrame(all_entries)
            st.subheader("Riepilogo tecnici")
            st.dataframe(df)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Scarica CSV", csv, file_name="tecnici_squadre.csv", mime='text/csv')
    else:
        st.error("❌ Criticità riscontrate. Vedi dettagli sotto:")
        for e in errors:
            st.write("- " + e)
        # Mostra riepilogo parziale
        all_entries = [t for cat in CATEGORIES for t in teams_data.get(cat, [])]
        if all_entries:
            df = pd.DataFrame(all_entries)
            with st.expander("Riepilogo dati inseriti (per debug)"):
                st.dataframe(df)
                txt = df.to_json(orient='records', force_ascii=False, indent=2)
                st.code(txt)

st.markdown("---")
st.caption("App prototype — esegui con: streamlit run streamlit_verifica_tecnici.py")
