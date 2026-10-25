from copy import deepcopy


def validar_anclajes_skos(propuesta, conceptos_skos):
    """Valida referencias explícitas a conceptos de la ontología."""

    anclajes = propuesta.get("anclajes_skos", [])

    if not isinstance(anclajes, list):
        raise ValueError("anclajes_skos debe ser una lista")

    if not isinstance(conceptos_skos, dict):
        raise TypeError("La ontología debe ser un diccionario")

    if not anclajes:
        return {
            "estado": "sin_anclajes",
            "anclajes_validados": [],
        }

    if len(set(anclajes)) != len(anclajes):
        raise ValueError("Hay anclajes SKOS duplicados")

    for uri in anclajes:
        if not isinstance(uri, str) or not uri.strip():
            raise ValueError("URI SKOS inválida")

        if uri not in conceptos_skos:
            raise ValueError(f"Concepto SKOS inexistente: {uri}")

    return {
        "estado": "validado",
        "anclajes_validados": deepcopy(anclajes),
    }


if __name__ == "__main__":
    ontologia = {
        "urn:cctr:innovacion": {
            "label": "Innovación"
        },
        "urn:cctr:empleo": {
            "label": "Empleo"
        },
    }

    propuesta = {
        "operacion": "crear_nodo",
        "id_nuevo": "C",
        "claim": "Innovación con protección laboral",
        "justificacion": "Articular dos perspectivas.",
        "anclajes_skos": [
            "urn:cctr:innovacion",
            "urn:cctr:empleo",
        ],
    }

    resultado = validar_anclajes_skos(propuesta, ontologia)

    assert resultado["estado"] == "validado"
    assert len(resultado["anclajes_validados"]) == 2
    print("ANCLAJES SKOS VÁLIDOS: OK")

    propuesta_invalida = deepcopy(propuesta)
    propuesta_invalida["anclajes_skos"] = [
        "urn:cctr:concepto_inventado"
    ]

    try:
        validar_anclajes_skos(propuesta_invalida, ontologia)
    except ValueError:
        print("CONCEPTO INEXISTENTE: BLOQUEADO")
    else:
        raise AssertionError("Se aceptó un concepto inexistente")

    propuesta_sin_anclajes = deepcopy(propuesta)
    propuesta_sin_anclajes.pop("anclajes_skos")

    resultado = validar_anclajes_skos(
        propuesta_sin_anclajes, ontologia
    )

    assert resultado["estado"] == "sin_anclajes"
    print("AUSENCIA DE ANCLAJES IDENTIFICADA: OK")

    print("VALIDADOR ONTOLÓGICO BÁSICO: OK")
