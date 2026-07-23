import streamlit as st
from supabase import create_client


def get_supabase():

    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]

    return create_client(url, key)


def upload_pdf(file_path, file_name):

    supabase = get_supabase()

    with open(file_path, "rb") as f:
        pdf_bytes = f.read()

    supabase.storage.from_("pdfs").upload(
        path=file_name,
        file=pdf_bytes,
        file_options={
            "content-type": "application/pdf"
        }
    )

    public_url = supabase.storage.from_("pdfs").get_public_url(
        file_name
    )

    return public_url