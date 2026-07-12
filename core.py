import json

with open("flow.json", "r", encoding="utf-8") as f:
    FLOW = json.load(f)

# =========================
# VALIDAZIONE FLOW
# =========================

for node, data in FLOW.items():

    nxt = data.get("next")

    if nxt and nxt != "completed" and nxt not in FLOW:
        raise Exception(
            f"Errore nel flow.json: il nodo '{node}' punta a '{nxt}' che non esiste."
        )

def next_node(node, answer):

    answer = str(answer).strip().lower()

    # ROOT (solo qui logica clinica iniziale)
    if node == "root":

        if "dolore" in answer:
            return "pain_1"

        elif "gonfiore" in answer:
            return "sw_1"

        elif "trauma" in answer:
            return "tr_1"

        elif "dente rotto" in answer or "scheggiato" in answer:
            return "tr_1"

        elif "otturazione" in answer or "corona" in answer:
            return "tr_1"

        elif "sanguinamento" in answer:
            return "paro_1"

        elif "gengive" in answer or "mobili" in answer:
            return "paro_1"

        elif "impianto" in answer:
            return "imp_1"


        elif "apparecchio" in answer or "ortodont" in answer:

            return "ortho_1"


        elif "protesi" in answer or "mancante" in answer:

            return "prost_1"


        elif "estetica" in answer:

            return "est_1"

        elif "controllo" in answer:
            return "med_1"

        else:
            return "med_1"

    # 🔵 LOGICA GENERICA (FLOW GUIDATO SOLO DA JSON)
    if node in FLOW:

        # se esiste "next" nel flow lo usa
        base = FLOW[node].get("next")

        # se non c'è next → fine
        if not base:
            return "completed"

        # 🔥 VALIDAZIONE: se nodo non esiste, fallback sicuro
        if base not in FLOW and base != "completed":
            return "med_1"

        return base

    # 🔴 FALLBACK ASSOLUTO (MAI CRASH)
    return "med_1"

    base = FLOW.get(node, {}).get("next", "completed")

    # gestione trauma frattura
    if node == "tr_1":

        if "mastic" in answer or "cibo" in answer or "morso" in answer:
            return "tr_2"

        if "caduta" in answer or "colpo" in answer or "sport" in answer:
            return "tr_2"

    return base