from copy import deepcopy

from orquestador2.clasificacion.rama_a import (
    preparar_rama_a,
    validar_resultados_rama_a,
)
from .integridad_debate import verificar_conservacion_debate


def preparar_clasificacion_posterior(registro):
    """Prepara solicitudes para clasificar el grafo transformado."""

    verificar_conservacion_debate(registro)

    grafo = registro.get("grafo_transformado")
    conceptos = registro.get("ontologia_skos")

    if not isinstance(grafo, dict):
        raise ValueError("Falta el grafo transformado")

    if not isinstance(conceptos, dict):
        raise ValueError("Falta la ontología SKOS")

    solicitudes = preparar_rama_a(grafo, conceptos)

    return deepcopy(solicitudes)


def validar_clasificacion_posterior(registro, respuestas):
    """Valida las clasificaciones posteriores con los mismos criterios."""

    verificar_conservacion_debate(registro)

    grafo = registro.get("grafo_transformado")
    conceptos = registro.get("ontologia_skos")

    if not isinstance(grafo, dict) or not isinstance(conceptos, dict):
        raise ValueError("Registro incompleto")

    return validar_resultados_rama_a(
        grafo, respuestas, conceptos
    )


if __name__ == "__main__":
    from .registro import crear_registro_transformacion
    from .inicializar_grafo import inicializar_grafo_transformado

    debate = {
        "nodes": [
            {"id": "A", "claim": "Priorizar innovación"},
            {"id": "B", "claim": "Priorizar protección laboral"},
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

    registro["grafo_transformado"]["nodes"].append({
        "id": "S1",
        "claim": "Innovación con protección laboral",
        "origen": "transformacion_semantica",
    })

    solicitudes = preparar_clasificacion_posterior(registro)

    assert set(solicitudes) == {"A", "B", "S1"}
    print("CLASIFICACIÓN POSTERIOR PREPARADA: OK")
    print("NODOS ORIGINALES Y NUEVOS INCLUIDOS: OK")

    respuestas = {
        nodo_id: {
            "anclajes": [],
            "funciones": [],
        }
        for nodo_id in solicitudes
    }

    resultados = validar_clasificacion_posterior(
        registro, respuestas
    )

    assert set(resultados) == {"A", "B", "S1"}
    print("CLASIFICACIONES VALIDADAS: OK")

    incompletas = deepcopy(respuestas)
    del incompletas["S1"]

    try:
        validar_clasificacion_posterior(
            registro, incompletas
        )
    except ValueError:
        print("COBERTURA INCOMPLETA: BLOQUEADA")
    else:
        raise AssertionError("Se aceptó cobertura incompleta")

    assert registro["grafo_original"] == debate
    print("GRAFO ORIGINAL INTACTO: OK")
    print("ADAPTADOR DE CLASIFICACIÓN POSTERIOR: OK")
