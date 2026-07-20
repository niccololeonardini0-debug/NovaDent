import streamlit as st
import json
from datetime import date, datetime
from db import insert_request, init_db
from triage_engine import calcola_priorita
from pdf_engine import genera_pdf
from core import next_node
import os

st.set_page_config(layout="wide")

init_db()

# =========================
# STUDIO DA URL (compatibile e stabile)
# =========================

studio_id = None

# 1) prova formato /dr-mario-rossi
query_params = st.query_params

if len(query_params) == 1 and list(query_params.keys())[0] == "studio":
    studio_id = query_params.get("studio")

# 2) fallback classico ?studio=
if studio_id is None:
    studio_id = query_params.get("studio")

# 3) fallback assoluto
if not studio_id:
    studio_id = "default"

# pulizia
studio_id = studio_id.strip("/")

st.session_state["studio_id"] = studio_id

# =========================
# FLOW
# =========================
with open("flow.json", "r", encoding="utf-8") as f:
    FLOW = json.load(f)

def is_last_node(node_id):
    next_n = next_node(node_id, None)
    return next_n in ["completed", None, "", node_id]
# =========================
# SESSION INIT
# =========================
if "node" not in st.session_state:
    st.session_state.node = "patient_info"

if "answers" not in st.session_state:
    st.session_state.answers = {}

if "patient_data" not in st.session_state:
    st.session_state.patient_data = {}


from db import get_doctor_by_studio

doctor_name = get_doctor_by_studio(studio_id)

if not doctor_name:
    doctor_name = "Studio Odontoiatrico"

st.markdown(f"""
<div style="
    text-align:center;
    font-family:'Palatino Linotype', 'Book Antiqua', Palatino, serif;
    font-size:clamp(40px, 8vw, 64px);
    font-weight:700;
    color:#14532D;
    letter-spacing:1px;
    margin-top:15px;
    margin-bottom:15px;
    text-shadow:0px 2px 4px rgba(0,0,0,0.12);
">
    {doctor_name}
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="
    text-align:center;
    font-size:20px;
    font-weight:700;
    color:#167D5A;
    margin-bottom:25px;
">
    NovaDent
</div>
""", unsafe_allow_html=True)

# =========================
# CSS PULITO E STABILE
# =========================
st.markdown("""
<style>

/* CONTAINER */

.block-container{
    padding-top:1.5rem;
    padding-left:1rem;
    padding-right:1rem;
    max-width:100%;
}

/* Titolo domanda */

.question{
    font-size:28px;
    font-weight:700;
    margin-bottom:25px;
}

/* INPUT */

.stTextInput input,
.stNumberInput input{

    border-radius:12px;
    font-size:18px;
}

/* RADIO */

.stRadio label{
    font-size:17px;
}

/* SLIDER */

.stSlider{
    padding-top:10px;
    padding-bottom:15px;
}

/* BOTTONI */

.stButton>button{

    width:100%;
    height:54px;

    border-radius:12px;

    font-size:18px;
    font-weight:700;

}

/* footer */

.novadent-footer{

    position:fixed;

    right:25px;
    bottom:18px;

    opacity:.45;

    font-size:13px;

}

/* Nasconde header */

header{
    visibility:hidden;
}

</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="novadent-footer">
NovaDent • Digital Dental Workflow
</div>
""", unsafe_allow_html=True)
# =========================
# HEADER
# =========================

# =========================
# ROUTING
# =========================
node = st.session_state.node

# =========================
# PATIENT INFO
# =========================
if node == "patient_info":

    st.markdown("""
    <div style="
        text-align:center;
        font-size:26px;
        font-weight:700;
        margin-top:20px;
        color:#14532D;
    ">
    Benvenuto
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="
        text-align:center;
        font-size:17px;
        margin-top:15px;
        margin-bottom:10px;
    ">
    Per consentire al medico di conoscere al meglio la sua situazione clinica,
    le chiediamo di compilare un breve questionario.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="
        text-align:center;
        color:#6b7280;
        margin-bottom:30px;
    ">
    Tempo di compilazione: circa 5 minuti.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns([3, 2])

    nome = st.text_input("Nome", key="nome_input")

    cognome = st.text_input("Cognome", key="cognome_input")

    data_nascita = st.text_input(
        "Data di nascita (GG/MM/AAAA)",
        placeholder="es. 01/01/2001"
    )

    codice_fiscale = st.text_input("Codice fiscale")

    luogo_nascita = st.text_input(
        "Luogo di nascita",
        placeholder="es. Firenze, Italia"
    )

    residenza = st.text_input(
        "Residenza",
        placeholder="es. Via Roma 25, Firenze"
    )

    telefono = st.text_input(
        "Telefono",
        placeholder="es. 333 1234567"
    )

    email = st.text_input(
        "Email",
        placeholder="es. nome.cognome@email.it"
    )

    if st.button("Inizia il questionario"):

        if (
                nome.strip() == ""
                or cognome.strip() == ""
                or codice_fiscale.strip() == ""
                or luogo_nascita.strip() == ""
                or residenza.strip() == ""
                or telefono.strip() == ""
                or email.strip() == ""
        ):
            st.error("Compila tutti i campi.")
            st.stop()

            if "@" not in email or "." not in email:
                st.error("Inserisci un indirizzo email valido.")
                st.stop()

            telefono_pulito = telefono.replace(" ", "")

            if not telefono_pulito.isdigit():
                st.error("Inserisci un numero di telefono valido.")
                st.stop()
        try:
            data_nascita_obj = datetime.strptime(
                data_nascita,
                "%d/%m/%Y"
            )

            oggi = date.today()

            eta = (
                    oggi.year
                    - data_nascita_obj.year
                    - (
                            (oggi.month, oggi.day)
                            < (data_nascita_obj.month, data_nascita_obj.day)
                    )
            )

        except:
            st.error("Inserisci la data nel formato GG/MM/AAAA")
            st.stop()

        st.session_state.patient_data = {
            "nome": nome,
            "cognome": cognome,
            "data_nascita": data_nascita,
            "eta": eta,
            "codice_fiscale": codice_fiscale,
            "luogo_nascita": luogo_nascita,
            "residenza": residenza,
            "telefono": telefono,
            "email": email
        }

        st.session_state.answers = {}
        st.session_state.node = "root"
        st.rerun()

# =========================
# COMPLETED
# =========================
elif node == "completed":

    st.success("Questionario completato")

    st.markdown("### 📷 Fotografie (opzionale)")

    uploaded_photos = st.file_uploader(
        "Carica fotografie utili per il dentista",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )

    if uploaded_photos:

        if len(uploaded_photos) > 4:
            st.warning("Puoi caricare massimo 4 fotografie.")
            st.stop()

        photo_folder = "uploads/photos"

        os.makedirs(photo_folder, exist_ok=True)

        saved_photos = []

        for i, photo in enumerate(uploaded_photos):
            file_path = os.path.join(
                photo_folder,
                f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}_{photo.name}"
            )

            with open(file_path, "wb") as f:
                f.write(photo.getbuffer())

            saved_photos.append(file_path)

        st.session_state["photos"] = saved_photos

        st.success(f"{len(saved_photos)} fotografie caricate")

    st.markdown("---")

    st.markdown("""
    ### Informativa Privacy

    I dati personali e sanitari inseriti nel presente questionario saranno trasmessi esclusivamente allo studio odontoiatrico presso il quale è stata richiesta la visita e utilizzati per finalità di assistenza sanitaria.

    NovaDent fornisce esclusivamente la piattaforma informatica utilizzata per la raccolta e la gestione dei dati.

    Proseguendo dichiari di aver letto l'informativa e autorizzi l'invio dei dati allo studio.
    """)

    consenso = st.checkbox(
        "Ho letto l'informativa privacy e autorizzo il trattamento dei miei dati."
    )

    if not consenso:
        st.warning("Devi accettare il consenso per inviare il questionario.")
        st.stop()

    if "saved" not in st.session_state:

        patient = st.session_state.patient_data

        nome = f"{patient['nome']} {patient['cognome']}"
        eta = patient["eta"]

        answers = st.session_state.get("answers", {})
        studio_id = st.session_state.get("studio_id", "default")

        priorita, score, red_flags, ipotesi = calcola_priorita(answers)

        ai_report = {
            "priorita": priorita,
            "score": score,
            "red_flags": red_flags,
            "ipotesi": ipotesi
        }

        pdf_path = genera_pdf(
            patient_data=patient,
            doctor_name=doctor_name,
            problema=answers.get("root", {}).get("answer", "Non specificato"),
            sintesi=answers,
            diagnosi=ipotesi,
            priorita=priorita,
            photos = st.session_state.get("photos", [])
        )

        print("answers:", type(answers), answers)
        print("ai_report:", type(ai_report), ai_report)
        print("pdf_path:", type(pdf_path), pdf_path)


        insert_request(
            patient,
            studio_id,
            answers=answers,
            ai_report=ai_report,
            pdf_path=pdf_path,
            consenso_privacy=True,
            data_consenso=datetime.now().isoformat()
        )

        st.session_state.pdf_path = pdf_path
        st.session_state.saved = True

    with open(st.session_state.pdf_path, "rb") as f:
        st.download_button("⬇️ Scarica PDF", f, file_name="referto_odonto.pdf")

# =========================
# FLOW ENGINE
# =========================
elif node in FLOW:

    flow = FLOW[node]

    total_questions = len(FLOW)

    answered = len(st.session_state.answers)

    total_questions = 15

    progress = answered / total_questions

    st.progress(min(progress, 1.0))

    st.caption("Compilazione questionario clinico")

    st.write("")

    st.markdown(f"<div class='question'>{flow['question']}</div>", unsafe_allow_html=True)

    # INPUT
    if flow.get("type") == "radio":
        answer = st.radio("", flow.get("options", []), key=node)


    elif flow.get("type") == "slider":

        answer = st.slider("", 0, 10, 5, key=node)


    elif flow.get("type") == "group":

        answer = {}

        for field in flow.get("fields", []):

            st.markdown(

                f"<div class='question'>{field['question']}</div>",

                unsafe_allow_html=True

            )

            if field["type"] == "radio":

                answer[field["question"]] = st.radio(

                    "",

                    field.get("options", []),

                    key=f"{node}_{field['question']}"

                )


            elif field["type"] == "text":

                answer[field["question"]] = st.text_input(

                    "",

                    key=f"{node}_{field['question']}"

                )


    else:

        answer = st.text_input("", key=node, placeholder=flow["question"])

    # =========================
    # BUTTON LABEL LOGIC
    # =========================

    next_n = next_node(node, answer)

    if node == "patient_info":
        button_label = "Inizia questionario"
    elif next_n == "completed":
        button_label = "Invia al dentista"
    else:
        button_label = "Avanti"

    # =========================
    # BUTTON ACTION
    # =========================
    if st.button(button_label):

        st.session_state.answers[node] = {
            "question": flow.get("question"),
            "answer": answer
        }

        if next_n not in FLOW and next_n != "completed":
            next_n = "med_5"

        st.session_state.node = next_n
        st.rerun()

else:
    st.error(f"Nodo non trovato: {node}")

