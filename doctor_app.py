import streamlit as st
from db import (
    login,
    get_requests,
    init_db,
    mark_as_visited,
    mark_as_not_visited
)
import json
from datetime import datetime

#init_db()

st.set_page_config(page_title="NovaDent Doctor", layout="wide")

st.caption("Doctor Dashboard")

# =========================
# SESSION
# =========================
if "doctor_logged" not in st.session_state:
    st.session_state.doctor_logged = False


# =========================
# LOGIN
# =========================
if not st.session_state.doctor_logged:

    st.title("🧑‍⚕️ ARCHIVIO QUESTIONARI")
    st.caption("NovaDent")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Accedi"):

        user = login(username, password)

        if user:
            st.session_state.doctor_logged = True
            st.session_state.username = username
            st.session_state.studio_id = user[2].strip("/")
            st.session_state.doctor_name = user[3]
            st.rerun()

        else:
            st.error("Credenziali errate")

    st.stop()


# =========================
# HEADER
# =========================

studio_nome = st.session_state.get("doctor_name", "")

st.markdown(
    f"""
    <h3 style="text-align:center; color:#4CAF88;">
        NovaDent
    </h3>

    <h1 style="text-align:center; color:#14532D;">
        {studio_nome}
    </h1>
    """,
    unsafe_allow_html=True
)

st.caption("Sistema di triage odontoiatrico intelligente")
st.divider()


# =========================
# LOAD REQUESTS
# =========================

requests = get_requests(st.session_state.studio_id)

if not requests:
    st.info("Nessuna richiesta presente")
    st.stop()

# =========================
# RICERCA PAZIENTE
# =========================

search = st.text_input(
    "🔎 Cerca paziente",
    placeholder="Nome e cognome"
)

if search:

    search = search.lower().strip()

    requests = [
        r for r in requests
        if search in f"{r[1]} {r[2]}".lower()
    ]



# =========================
# LISTA PAZIENTI
# =========================


for r in requests:

    patient_id = r[0]
    visitato = r[9]

    nome = r[1]
    cognome = r[2]
    eta = r[3]
    motivo = r[4]
    data_richiesta = r[7]

    try:
        data_richiesta = datetime.fromisoformat(
            str(data_richiesta)
        ).strftime("%d/%m/%Y %H:%M")

    except:
        pass

    try:
        ai_report = json.loads(r[6]) if r[6] else {}

    except:
        ai_report = {}


    priorita = ai_report.get("priorita", "BASSA")

    ipotesi = ai_report.get("ipotesi", "—")

    # =========================
    # CARD PAZIENTE COMPATTA
    # =========================

    pdf_url = r[8]

    if priorita == "ALTA":
        badge = "🔴 ALTA"

    elif priorita == "MEDIA":
        badge = "🟡 MEDIA"

    else:
        badge = "🟢 BASSA"

    col1, col2, col3 = st.columns([5, 1, 1])

    with col1:

        st.markdown(
            f"""
    **👤 {nome} {cognome} · {eta}a**  {badge}

    🦷 {motivo if motivo else 'Non specificato'}  
    💡 {ipotesi} · 📅 {data_richiesta}
    """,
            unsafe_allow_html=True
        )

    with col2:

        if pdf_url:
            st.link_button(
                "📄",
                pdf_url
            )

    with col3:

        if visitato == 0:

            if st.button(
                    "✅",
                    key=f"visit_{patient_id}",
                    help="Segna come visitato"
            ):
                mark_as_visited(patient_id)
                st.rerun()

        else:

            if st.button(
                    "↩️",
                    key=f"unvisit_{patient_id}",
                    help="Segna come non visitato"
            ):
                mark_as_not_visited(patient_id)
                st.rerun()

    st.markdown(
        "<hr style='margin:8px 0'>",
        unsafe_allow_html=True
    )

# =========================
# FOOTER
# =========================

st.markdown(
"""
<div style="
position:fixed;
bottom:12px;
right:18px;
font-size:12px;
opacity:0.4;
">
NovaDent • Digital Dental Workflow
</div>
""",
unsafe_allow_html=True
)