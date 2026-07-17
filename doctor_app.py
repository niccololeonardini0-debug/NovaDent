import streamlit as st
from db import login, get_requests, init_db
import json
from datetime import datetime

init_db()

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
# SORT PRIORITY
# =========================

def priority_rank(r):

    try:
        ai = json.loads(r[6]) if r[6] else {}
    except:
        ai = {}

    p = ai.get("priorita", "BASSA")

    if p == "ALTA":
        return 0

    if p == "MEDIA":
        return 1

    return 2


def get_time(r):

    try:
        return datetime.fromisoformat(str(r[7]))

    except:
        return datetime(1970, 1, 1)


requests = sorted(
    requests,
    key=lambda r: (
        priority_rank(r),
        get_time(r)
    )
)


# =========================
# LISTA PAZIENTI
# =========================

st.write("")


for r in requests:

    patient_id = r[0]
    nome = r[1]
    cognome = r[2]
    eta = r[3]
    motivo = r[4]

    try:
        ai_report = json.loads(r[6]) if r[6] else {}

    except:
        ai_report = {}


    priorita = ai_report.get("priorita", "BASSA")
    ipotesi = ai_report.get("ipotesi", "Non disponibile")

    # =========================
    # CARD PAZIENTE
    # =========================

    with st.container():

        st.markdown(
            f"## 👤 {nome} {cognome}"
        )

        st.caption(f"Età: {eta}")


        st.markdown("**🦷 Motivo della visita**")
        st.write(
            motivo if motivo else "Non specificato"
        )


        st.caption(
            f"🧠 Ipotesi AI: {ipotesi}"
        )


        if priorita == "ALTA":

            st.error("🔴 PRIORITÀ ALTA")

        elif priorita == "MEDIA":

            st.warning("🟠 PRIORITÀ MEDIA")

        else:

            st.success("🟢 PRIORITÀ BASSA")


        pdf_path = r[8]

        if pdf_path:

            try:

                with open(pdf_path, "rb") as f:

                    st.download_button(
                        "📄 Scarica PDF",
                        f,
                        file_name=f"referto_{nome}_{cognome}.pdf",
                        key=f"pdf_{patient_id}"
                    )

            except:

                st.warning("PDF non disponibile")


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
NovaDent
</div>
""",
unsafe_allow_html=True
)