from copy import deepcopy

from .registro import verificar_integridad_original
from .validacion_referencias import validar_referencias


def ejecutar_creacion_nodo(registro, entrada_b):
    """Ejecuta la primera operación pendiente de creación de nodo."""

    verificar_integridad_original(registro, entrada_b)

    grafo = registro.get("grafo_transformado")
    if not isinstance(grafo, dict):
        raise ValueError("Primero debe inicializarse el grafo transformado")

    pendientes = [
        evento for evento in registro["transformaciones"]
        if evento["estado"] == "pendiente"
    ]

    if not pendientes:
        raise ValueError("No hay operaciones pendientes")

    evento = pendientes[0]
    propuesta = evento["propuesta"]

    if propuesta["operacion"] != "crear_nodo":
        raise ValueError("Esta versión solo ejecuta crear_nodo")

    validar_referencias(propuesta, grafo)

    copia = deepcopy(grafo)

    copia["nodes"].append({
        "id": propuesta["id_nuevo"],
        "claim": propuesta["claim"],
        "origen": "transformacion_semantica",
        "secuencia_transformacion": evento["secuencia"],
    })

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
        "operacion": "crear_nodo",
        "id_nuevo": "C",
        "claim": "La innovación requiere protección laboral",
        "justificacion": "Introducir una perspectiva que articule innovación y empleo.",
    })

    resultado = ejecutar_creacion_nodo(registro, entrada)

    assert resultado["estado"] == "ejecutada"
    assert len(registro["grafo_transformado"]["nodes"]) == 3
    assert len(registro["grafo_original"]["nodes"]) == 2
    assert registro["grafo_original"] == debate
    assert registro["grafo_transformado"]["edges"] == debate["edges"]

    print("TRANSFORMACIÓN EJECUTADA: OK")
    print("NODOS ORIGINALES:", len(registro["grafo_original"]["nodes"]))
    print("NODOS TRANSFORMADOS:", len(registro["grafo_transformado"]["nodes"]))
    print("RELACIONES PRO/CON CONSERVADAS: OK")
    print("TRAZABILIDAD DE LA OPERACIÓN: OK")
