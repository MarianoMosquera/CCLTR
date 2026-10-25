from copy import deepcopy

from .registro import verificar_integridad_original
from .validacion_referencias import validar_referencias


def ejecutar_retirada_nodo(registro, entrada_b):
    """Retira un nodo generado, conservando su historial."""

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

    if propuesta["operacion"] != "retirar_nodo":
        raise ValueError("La operación pendiente no es retirar_nodo")

    validar_referencias(propuesta, grafo)

    id_nodo = propuesta["id_nodo"]

    originales = {
        str(n["id"]) for n in registro["grafo_original"]["nodes"]
    }

    if id_nodo in originales:
        raise ValueError("No se pueden retirar nodos originales")

    nodo = next(
        n for n in grafo["nodes"]
        if str(n["id"]) == id_nodo
    )

    if nodo.get("origen") not in {
        "transformacion_semantica", "fusion_semantica"
    }:
        raise ValueError("El nodo no tiene procedencia autorizada")

    vinculaciones = [
        e for e in grafo["edges"]
        if str(e["source"]) == id_nodo
        or str(e["target"]) == id_nodo
    ]

    if vinculaciones:
        raise ValueError("El nodo tiene vínculos que deben resolverse")

    copia = deepcopy(grafo)

    copia["nodes"] = [
        n for n in copia["nodes"]
        if str(n["id"]) != id_nodo
    ]

    verificar_integridad_original(registro, entrada_b)

    registro["grafo_transformado"] = copia
    evento["estado"] = "ejecutada"
    evento["nodo_retirado"] = deepcopy(nodo)

    return deepcopy(evento)


if __name__ == "__main__":
    from .registro import crear_registro_transformacion
    from .registro_operaciones import registrar_operacion
    from .inicializar_grafo import inicializar_grafo_transformado
    from .ejecutor import ejecutar_creacion_nodo

    debate = {
        "nodes": [
            {"id": "A", "claim": "Innovación"},
            {"id": "B", "claim": "Protección laboral"},
        ],
        "edges": [
            {"source": "A", "target": "B",
             "target_idx": 0, "valence": "CON"}
        ],
    }

    entrada = {
        "grafo_original": deepcopy(debate),
        "ontologia_skos": {},
    }

    registro = crear_registro_transformacion(entrada)
    inicializar_grafo_transformado(registro, entrada)

    registrar_operacion(registro, entrada, {
        "operacion": "crear_nodo",
        "id_nuevo": "C",
        "claim": "Nueva perspectiva conceptual",
        "justificacion": "Exploración semántica.",
    })

    ejecutar_creacion_nodo(registro, entrada)

    registrar_operacion(registro, entrada, {
        "operacion": "retirar_nodo",
        "id_nodo": "C",
        "justificacion": "La alternativa se descarta provisionalmente.",
    })

    resultado = ejecutar_retirada_nodo(registro, entrada)

    assert resultado["estado"] == "ejecutada"
    assert resultado["nodo_retirado"]["id"] == "C"
    assert len(registro["grafo_transformado"]["nodes"]) == 2
    assert registro["grafo_original"] == debate

    registrar_operacion(registro, entrada, {
        "operacion": "retirar_nodo",
        "id_nodo": "A",
        "justificacion": "Prueba de protección.",
    })

    try:
        ejecutar_retirada_nodo(registro, entrada)
    except ValueError:
        print("RETIRADA DE NODO ORIGINAL: BLOQUEADA")
    else:
        raise AssertionError("Se permitió retirar un nodo original")

    print("RETIRADA DE NODO GENERADO: OK")
    print("NODO RETIRADO DOCUMENTADO: OK")
    print("RELACIONES ORIGINALES CONSERVADAS: OK")
    print("GRAFO ORIGINAL INTACTO: OK")
