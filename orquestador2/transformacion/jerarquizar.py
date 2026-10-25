from copy import deepcopy

from .registro import verificar_integridad_original
from .validacion_referencias import validar_referencias


def ejecutar_jerarquizacion(registro, entrada_b):
    """Asigna prioridad a un nodo del grafo transformado."""

    verificar_integridad_original(registro, entrada_b)

    grafo = registro.get("grafo_transformado")
    if not isinstance(grafo, dict):
        raise ValueError("El grafo transformado no está inicializado")

    pendientes = [
        evento for evento in registro["transformaciones"]
        if evento["estado"] == "pendiente"
    ]

    if not pendientes:
        raise ValueError("No hay operaciones pendientes")

    evento = pendientes[0]
    propuesta = evento["propuesta"]

    if propuesta["operacion"] != "jerarquizar_nodo":
        raise ValueError("La operación pendiente no es jerarquizar_nodo")

    validar_referencias(propuesta, grafo)

    copia = deepcopy(grafo)

    nodo = next(
        n for n in copia["nodes"]
        if str(n["id"]) == propuesta["id_nodo"]
    )

    prioridad_anterior = nodo.get("prioridad_semantica")

    historial = nodo.setdefault("historial_prioridades", [])
    historial.append({
        "secuencia": evento["secuencia"],
        "prioridad_anterior": prioridad_anterior,
        "prioridad_nueva": propuesta["prioridad"],
        "justificacion": propuesta["justificacion"],
    })

    nodo["prioridad_semantica"] = propuesta["prioridad"]

    registro["grafo_transformado"] = copia
    evento["estado"] = "ejecutada"

    verificar_integridad_original(registro, entrada_b)

    return deepcopy(evento)


if __name__ == "__main__":
    from .registro import crear_registro_transformacion
    from .registro_operaciones import registrar_operacion
    from .inicializar_grafo import inicializar_grafo_transformado

    debate = {
        "nodes": [
            {"id": "A", "claim": "Innovación tecnológica"},
            {"id": "B", "claim": "Protección laboral"},
        ],
        "edges": [
            {"source": "A", "target": "B", "target_idx": 0, "valence": "CON"}
        ],
    }

    entrada = {
        "grafo_original": deepcopy(debate),
        "ontologia_skos": {},
    }

    registro = crear_registro_transformacion(entrada)
    inicializar_grafo_transformado(registro, entrada)

    registrar_operacion(registro, entrada, {
        "operacion": "jerarquizar_nodo",
        "id_nodo": "B",
        "prioridad": 0.85,
        "justificacion": (
            "Dar mayor atención a las consecuencias laborales "
            "sin eliminar la perspectiva tecnológica."
        ),
    })

    resultado = ejecutar_jerarquizacion(registro, entrada)

    nodo = registro["grafo_transformado"]["nodes"][1]

    assert resultado["estado"] == "ejecutada"
    assert nodo["prioridad_semantica"] == 0.85
    assert nodo["historial_prioridades"][0]["prioridad_anterior"] is None
    assert registro["grafo_original"] == debate
    assert registro["grafo_transformado"]["edges"] == debate["edges"]

    print("JERARQUIZACIÓN EJECUTADA: OK")
    print("PRIORIDAD ASIGNADA:", nodo["prioridad_semantica"])
    print("HISTORIAL DE PRIORIDADES: OK")
    print("RELACIONES ORIGINALES CONSERVADAS: OK")
    print("GRAFO ORIGINAL INTACTO: OK")
