from db import get_conn

USERS = [

    (
        "francesco.tartari",
        "1687",
        "dr-francesco-tartari",
        "Dr. Francesco Tartari"
    ),

    (
        "iacopo.malandrucco",
        "5191",
        "dr-iacopo-malandrucco",
        "Dr. Iacopo Malandrucco"
    ),

    (
        "niccolo.leonardini",
        "1234",
        "dr-niccolo-leonardini",
        "Dr. Niccolò Leonardini"
    ),

]

PATIENT_URL = "http://localhost:8501"
DOCTOR_URL = "http://localhost:8502"

conn = get_conn()
c = conn.cursor()

print("\n===== NOVADENT STUDIO LINKS =====\n")

for user in USERS:

    username, password, studio_id, doctor_name = user

    c.execute("""
    INSERT INTO users
    (username,password,studio_id,doctor_name)
    VALUES (%s,%s,%s,%s)
    ON CONFLICT (username) DO NOTHING
    """, user)

    patient_link = f"{PATIENT_URL}/?studio={studio_id}"
    doctor_link = DOCTOR_URL

    print(f"""
    👨‍⚕️ {doctor_name}

    🔑 Login dottore:
    Username: {username}
    Password: {password}

    🦷 Link paziente:
    {patient_link}

    👨‍⚕️ Link dottore:
    {doctor_link}
    """)

conn.commit()
conn.close()

print("\n=================================\n")
print("Seed completato")