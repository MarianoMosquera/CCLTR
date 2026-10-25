"""Rama A: clasificación del debate original sin transformarlo."""

import copy

from orquestador2.clasificacion.pipeline import (
    preparar_solicitud,
    validar_respuesta,
)


def preparar_rama_a(debate, conceptos):
    """Genera solicitudes independientes sin modificar el debate."""
    solicitudes = {}

    for nodo in debate["nodes"]:
        nodo_id = str(nodo["id"])
        solicitudes[nodo_id] = preparar_solicitud(nodo, conceptos)

    return solicitudes


def validar_resultados_rama_a(debate, respuestas, conceptos):
    """Valida respuestas y exige cobertura completa de los nodos."""
    nodos = {str(n["id"]): n for n in debate["nodes"]}

    if set(respuestas) != set(nodos):
        faltantes = set(nodos) - set(respuestas)
        sobrantes = set(respuestas) - set(nodos)
        raise ValueError(
            f"Cobertura incorrecta. Faltantes: {faltantes}; "
            f"Sobrantes: {sobrantes}"
        )

    resultados = {}

    for nodo_id, nodo in nodos.items():
        resultados[nodo_id] = validar_respuesta(
            nodo, respuestas[nodo_id], conceptos
        )

    return resultados


if __name__ == "__main__":
    debate = {
        "nodes": [
            {"id": "A", "claim": "La seguridad es importante."},
            {"id": "B", "claim": "La privacidad es importante."},
        ],
        "edges": [
            {
                "source": "B",
                "target": "A",
                "valence": "CON",
                "target_idx": 0,
            }
        ],
    }

    original = copy.deepcopy(debate)

    conceptos = {
        "urn:seguridad": {
            "label_es": "Seguridad",
            "label_en": "Security",
            "relaciones": {
                "broader": [], "narrower": [], "related": []
            },
        }
    }

    solicitudes = preparar_rama_a(debate, conceptos)

    respuestas = {
        "A": {
            "anclajes": [
                {
                    "uri": "urn:seguridad",
                    "evidencia": "seguridad",
                }
            ],
            "funciones": ["pragmatica"],
        },
        "B": {
            "anclajes": [],
            "funciones": [],
        },
    }

    resultados = validar_resultados_rama_a(
        debate, respuestas, conceptos
    )

    assert len(solicitudes) == 2
    assert len(resultados) == 2
    assert debate == original
    assert debate["edges"][0]["valence"] == "CON"
    assert debate["edges"][0]["target_idx"] == 0

    print("RAMA A: OK")
    print("GRAFO ORIGINAL INTACTO: OK")
    print("PRO/CON Y TARGET_IDX PRESERVADOS: OK")
