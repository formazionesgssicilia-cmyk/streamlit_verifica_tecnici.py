
import streamlit as st
import pandas as pd

# Titolo
st.title("Verifica requisiti Settore Tecnico - Club Giovanili SGS Sicilia")

st.header("Dati Responsabile Tecnico Settore Giovanile")
rt_nome = st.text_input("Nome Responsabile Tecnico")
rt_cognome = st.text_input("Cognome Responsabile Tecnico")
rt_qualifica = st.selectbox("Qualifica Federale Responsabile Tecnico", [
    "UEFA Pro", "UEFA A", "UEFA B", "UEFA C", "D-Level", "E-Level", "Scienze Motorie"
])

# Categorie per le prime squadre
st.header("Allenatori Prime Squadre per Categoria")
categorie = ["Esordienti", "Pulcini", "Primi Calci", "Piccoli Amici"]
allenatori = {}

for cat in categorie:
    nome = st.text_input(f"Nome Allenatore {cat}")
    cognome = st.text_input(f"Cognome Allenatore {cat}")
    qualifica = st.selectbox(f"Qualifica Allenatore {cat}", [
        "UEFA Pro", "UEFA A", "UEFA B", "UEFA C", "D-Level", "E-Level", "Scienze Motorie"
    ], key=cat)
    allenatori[cat] = {"nome": nome, "cognome": cognome, "qualifica": qualifica}

# Controlli
errori = []

# 1) Controllo incompatibilità nominativo RT con allenatori prime squadre
for cat, dati in allenatori.items():
    if (rt_nome.strip().lower() == dati["nome"].strip().lower() and
        rt_cognome.strip().lower() == dati["cognome"].strip().lower()):
        errori.append(f"Incompatibilità: Il Responsabile Tecnico coincide con l'allenatore della categoria {cat}.")

# 2) Controllo qualifica RT
if rt_qualifica in ["E-Level", "Scienze Motorie"]:
    errori.append("Il Responsabile Tecnico non può avere qualifica E-Level o Scienze Motorie.")

# 3) Controllo Scienze Motorie per allenatori
for cat, dati in allenatori.items():
    if dati["qualifica"] == "Scienze Motorie" and cat not in ["Primi Calci", "Piccoli Amici"]:
        errori.append(f"La qualifica 'Scienze Motorie' non è valida per la categoria {cat}.")

# Output risultati
if st.button("Verifica Requisiti"):
    if errori:
        for err in errori:
            st.error(err)
    else:
        st.success("Tutti i requisiti sono rispettati. ✔️")
