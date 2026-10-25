from copy import deepcopy

OPERACIONES_SEMANTICAS = {
    "crear_nodo",
    "reformular_nodo",
    "fusionar_nodos",
    "crear_vinculo",
}


def validar_calidad_conceptual(propuesta):
    """Exige justificación conceptual explícita, sin juzgar su veracidad."""

    if not isinstance(propuesta, dict):
        raise TypeError("La propuesta debe ser un diccionario")

    operacion = propuesta.get("operacion")

    if operacion not in OPERACIONES_SEMANTICAS:
        return {
            "estado": "no_aplica",
            "operacion": operacion,
        }

    campos = ("tension_conservada", "aporte_conceptual")

    for campo in campos:
        valor = propuesta.get(campo)

        if not isinstance(valor, str) or not valor.strip():
            raise ValueError(
                f"La operación {operacion} requiere {campo}"
            )

    if (
        propuesta["tension_conservada"].strip()
        == propuesta["aporte_conceptual"].strip()
    ):
        raise ValueError(
            "La tensión conservada y el aporte conceptual "
            "deben explicarse por separado"
        )

    return {
        "estado": "justificacion_explicita",
        "operacion": operacion,
        "tension_conservada": deepcopy(
            propuesta["tension_conservada"]
        ),
        "aporte_conceptual": deepcopy(
            propuesta["aporte_conceptual"]
        ),
        "advertencia": (
            "La presencia de explicaciones no demuestra "
            "conservación efectiva de diversidad semántica"
        ),
    }


if __name__ == "__main__":
    valida = {
        "operacion": "crear_nodo",
        "tension_conservada": (
            "La innovación tecnológica puede aumentar "
            "la productividad y desplazar empleos."
        ),
        "aporte_conceptual": (
            "Explorar mecanismos que distribuyan "
            "los beneficios sin ocultar los costos laborales."
        ),
    }

    resultado = validar_calidad_conceptual(valida)

    assert resultado["estado"] == "justificacion_explicita"
    print("JUSTIFICACIÓN CONCEPTUAL EXPLÍCITA: OK")

    sin_tension = deepcopy(valida)
    del sin_tension["tension_conservada"]

    try:
        validar_calidad_conceptual(sin_tension)
    except ValueError:
        print("AUSENCIA DE TENSIÓN: BLOQUEADA")
    else:
        raise AssertionError("Se aceptó una propuesta sin tensión")

    sin_aporte = deepcopy(valida)
    sin_aporte["aporte_conceptual"] = " "

    try:
        validar_calidad_conceptual(sin_aporte)
    except ValueError:
        print("AUSENCIA DE APORTE: BLOQUEADA")
    else:
        raise AssertionError("Se aceptó una propuesta sin aporte")

    redundante = deepcopy(valida)
    redundante["aporte_conceptual"] = redundante["tension_conservada"]

    try:
        validar_calidad_conceptual(redundante)
    except ValueError:
        print("EXPLICACIONES IDÉNTICAS: BLOQUEADAS")
    else:
        raise AssertionError("Se aceptaron explicaciones idénticas")

    gestion = {
        "operacion": "jerarquizar_nodo",
        "prioridad": 0.7,
    }

    assert validar_calidad_conceptual(gestion)["estado"] == "no_aplica"
    print("OPERACIONES DE GESTIÓN: EXCLUIDAS CORRECTAMENTE")
    print("CONTROL CONCEPTUAL PRELIMINAR: OK")
