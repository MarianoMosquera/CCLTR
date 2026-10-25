from copy import deepcopy

from .registro import verificar_integridad_original
from .validacion_relaciones import validar_relacion


def ejecutar_creacion_vinculo(registro, entrada_b):
    """Crea una relación conceptual en el grafo transformado."""

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

    if propuesta["operacion"] != "crear_vinculo":
        raise ValueError("La operación pendiente no es crear_vinculo")

    validar_relacion(propuesta, grafo)

    copia = deepcopy(grafo)

    copia["edges"].append({
        "source": propuesta["source"],
        "target": propuesta["target"],
        "tipo": propuesta["tipo"],
        "origen": "transformacion_semantica",
        "secuencia_transformacion": evento["secuencia"],
        "justificacion": propuesta["justificacion"],
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
        "operacion": "crear_vinculo",
        "source": "A",
        "target": "B",
        "tipo": "tension_conservada",
        "justificacion": (
            "Relacionar innovación y empleo sin eliminar "
            "la contradicción original."
        ),
    })

    resultado = ejecutar_creacion_vinculo(registro, entrada)

    assert resultado["estado"] == "ejecutada"
    assert len(registro["grafo_transformado"]["edges"]) == 2
    assert len(registro["grafo_original"]["edges"]) == 1
    assert registro["grafo_transformado"]["edges"][0] == debate["edges"][0]
    assert registro["grafo_transformado"]["edges"][1]["tipo"] == (
        "tension_conservada"
    )
    assert registro["grafo_original"] == debate

    print("CREACIÓN DE VÍNCULO: OK")
    print("RELACIÓN ORIGINAL CONSERVADA: OK")
    print("NUEVA RELACIÓN CON TRAZABILIDAD: OK")
    print("INDEPENDENCIA DEL GRAFO ORIGINAL: OK")
