def calcola_priorita(answers):

    flat_text = " ".join([
        str(v.get("answer", ""))
        for v in answers.values()
    ]).lower()

    score = 0
    ipotesi = "Non determinata"
    red_flags = []

    # -------------------------
    # DOLORE (PULPITE)
    # -------------------------
    if "dolore" in flat_text:

        if "notte" in flat_text:
            score += 3
            ipotesi = "Pulpite probabile"

        if "freddo" in flat_text or "caldo" in flat_text:
            score += 3
            ipotesi = "Pulpite"

        if any(x in flat_text for x in ["8", "9", "10", "forte"]):
            score += 3
            ipotesi = "Pulpite acuta"

        if "continuo" in flat_text:
            score += 2

    # -------------------------
    # INFEZIONE / ASCESSO
    # -------------------------
    if "gonfiore" in flat_text:

        score += 3

        if "febbre" in flat_text or "pus" in flat_text:
            score += 4
            ipotesi = "Ascesso dentale"
        else:
            ipotesi = "Infezione odontogena"

    # -------------------------
    # TRAUMA (FRATTURE)
    # -------------------------
    if "trauma" in flat_text or "caduta" in flat_text:

        score += 4

        if "uscito" in flat_text or "completamente" in flat_text:
            score += 5
            ipotesi = "Avulsione dentale (urgenza massima)"
        elif "frattura" in flat_text or "scheggi" in flat_text:
            ipotesi = "Frattura dentale"
        else:
            ipotesi = "Trauma dentale"

    # -------------------------
    # ORTODONZIA
    # -------------------------
    if "apparecchio" in flat_text or "ortod" in flat_text:
        score += 1
        ipotesi = "Problema ortodontico"

    # -------------------------
    # IMPIANTI
    # -------------------------
    if "impianto" in flat_text:

        score += 2

        if "mobile" in flat_text or "pus" in flat_text:
            score += 4
            ipotesi = "Peri-implantite sospetta"
        else:
            ipotesi = "Valutazione implantare"

    # -------------------------
    # PARODONTO
    # -------------------------
    if "sanguinamento" in flat_text or "gengive" in flat_text:

        score += 2

        if "mobile" in flat_text or "alito" in flat_text:
            ipotesi = "Parodontite sospetta"
        else:
            ipotesi = "Gengivite / valutazione parodontale"

    # -------------------------
    # ESTETICA / CONTROLLO / IGIENE
    # -------------------------
    if "estetica" in flat_text:
        ipotesi = "Valutazione estetica"

    if "controllo" in flat_text:
        ipotesi = "Visita di controllo"

    if "pulizia dei denti" in flat_text:
        ipotesi = "Seduta di igiene orale professionale"

    # -------------------------
    # PRIORITA
    # -------------------------
    if score >= 8:
        priorita = "ALTA"
    elif score >= 4:
        priorita = "MEDIA"
    else:
        priorita = "BASSA"

    return priorita, score, red_flags, ipotesi
