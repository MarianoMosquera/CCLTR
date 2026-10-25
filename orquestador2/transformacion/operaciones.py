OPERACIONES_PERMITIDAS = {
    "crear_nodo",
    "reformular_nodo",
    "fusionar_nodos",
    "crear_vinculo",
    "retirar_vinculo",
    "jerarquizar_nodo",
    "retirar_nodo",
}

CAMPOS_OBLIGATORIOS = {
    "crear_nodo": {"id_nuevo", "claim", "justificacion"},
    "reformular_nodo": {"id_original", "claim_nuevo", "justificacion"},
    "fusionar_nodos": {"ids_origen", "id_nuevo", "claim", "justificacion"},
    "crear_vinculo": {"source", "target", "tipo", "justificacion"},
    "retirar_vinculo": {"source", "target", "tipo", "justificacion"},
    "jerarquizar_nodo": {"id_nodo", "prioridad", "justificacion"},
    "retirar_nodo": {"id_nodo", "justificacion"},
}


def validar_operacion(operacion):
    if not isinstance(operacion, dict):
        raise TypeError("La operación debe ser un diccionario")

    tipo = operacion.get("operacion")

    if tipo not in OPERACIONES_PERMITIDAS:
        raise ValueError(f"Operación no permitida: {tipo}")

    faltantes = CAMPOS_OBLIGATORIOS[tipo] - set(operacion)

    if faltantes:
        raise ValueError(f"Campos faltantes: {sorted(faltantes)}")

    if not isinstance(operacion["justificacion"], str):
        raise ValueError("La justificación debe ser textual")

    if not operacion["justificacion"].strip():
        raise ValueError("La justificación no puede estar vacía")

    campos_textuales = {
        "id_nuevo", "id_original", "id_nodo",
        "claim", "claim_nuevo", "source", "target", "tipo"
    }

    for campo in CAMPOS_OBLIGATORIOS[tipo] & campos_textuales:
        valor = operacion[campo]
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError(f"Campo textual inválido: {campo}")

    if tipo == "fusionar_nodos":
        origenes = operacion["ids_origen"]
        if (
            not isinstance(origenes, list)
            or len(origenes) < 2
            or any(not isinstance(x, str) or not x.strip() for x in origenes)
            or len(origenes) != len(set(origenes))
        ):
            raise ValueError("ids_origen debe contener al menos dos IDs distintos")

    if tipo == "jerarquizar_nodo":
        prioridad = operacion["prioridad"]
        if (
            isinstance(prioridad, bool)
            or not isinstance(prioridad, (int, float))
            or not 0 <= prioridad <= 1
        ):
            raise ValueError("La prioridad debe ser numérica entre 0 y 1")

    return True


if __name__ == "__main__":
    ejemplos = [
        {
            "operacion": "crear_nodo",
            "id_nuevo": "C",
            "claim": "La innovación requiere responsabilidad institucional.",
            "justificacion": "Nueva relación conceptual propuesta.",
        },
        {
            "operacion": "retirar_nodo",
            "id_nodo": "B",
            "justificacion": "Se conserva en el registro histórico.",
        },
    ]

    assert all(validar_operacion(op) for op in ejemplos)

    try:
        validar_operacion({
            "operacion": "borrar_grafo_original",
            "justificacion": "Prueba",
        })
    except ValueError:
        print("OPERACIÓN PROHIBIDA BLOQUEADA: OK")
    else:
        raise AssertionError("No se bloqueó la operación prohibida")

    print("CATÁLOGO DE OPERACIONES: OK")
    print("OPERACIONES DISPONIBLES:", len(OPERACIONES_PERMITIDAS))
    print("VALIDACIÓN DE CAMPOS: OK")
