from copy import deepcopy

from .registro import verificar_integridad_original
from .validacion_referencias import validar_referencias


def ejecutar_reformulacion(registro, entrada_b):
    """Reformula un nodo en la copia de trabajo, preservando su procedencia."""

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

    if propuesta["operacion"] != "reformular_nodo":
        raise ValueError("La operación pendiente no es reformular_nodo")

    validar_referencias(propuesta, grafo)

    copia = deepcopy(grafo)
    nodo = next(
        n for n in copia["nodes"]
        if str(n["id"]) == propuesta["id_original"]
    )

    texto_anterior = nodo["claim"]
    if propuesta["claim_nuevo"] == texto_anterior:
        raise ValueError("La reformulación debe modificar el texto")

    historial = nodo.setdefault("historial_reformulaciones", [])
    historial.append({
        "secuencia": evento["secuencia"],
        "claim_anterior": texto_anterior,
        "claim_nuevo": propuesta["claim_nuevo"],
        "justificacion": propuesta["justificacion"],
    })

    nodo["claim"] = propuesta["claim_nuevo"]

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
            {"id": "A", "claim": "La IA aumenta la productividad"},
            {"id": "B", "claim": "La IA desplaza empleos"},
        ],
        "edges": [
            {
                "source": "A",
                "target": "B",
                "target_idx": 0,
                "valence": "CON",
            }
        ],
    }

    entrada = {
        "grafo_original": deepcopy(debate),
        "ontologia_skos": {},
    }

    registro = crear_registro_transformacion(entrada)
    inicializar_grafo_transformado(registro, entrada)

    registrar_operacion(registro, entrada, {
        "operacion": "reformular_nodo",
        "id_original": "B",
        "claim_nuevo": (
            "La automatización transforma las condiciones de empleo "
            "y exige mecanismos de adaptación laboral"
        ),
        "justificacion": (
            "Explorar nuevas conexiones conceptuales "
            "sin eliminar la preocupación laboral original"
        ),
    })

    resultado = ejecutar_reformulacion(registro, entrada)

    nodo = registro["grafo_transformado"]["nodes"][1]

    assert resultado["estado"] == "ejecutada"
    assert nodo["claim"] != debate["nodes"][1]["claim"]
    assert nodo["historial_reformulaciones"][0]["claim_anterior"] == (
        debate["nodes"][1]["claim"]
    )
    assert registro["grafo_original"] == debate
    assert registro["grafo_transformado"]["edges"] == debate["edges"]

    print("REFORMULACIÓN EJECUTADA: OK")
    print("TEXTO ORIGINAL CONSERVADO: OK")
    print("HISTORIAL DE REFORMULACIÓN: OK")
    print("RELACIONES PRO/CON CONSERVADAS: OK")
