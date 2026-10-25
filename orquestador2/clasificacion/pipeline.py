"""Integración de clasificación semántica, sin ejecutar modelos."""

import json

from orquestador2.clasificacion.entrada_ia import preparar_entrada
from orquestador2.clasificacion.prompt import PROMPT_CLASIFICACION
from orquestador2.clasificacion.argumentos import validar_clasificaciones


def preparar_solicitud(nodo, conceptos):
    return {
        "instrucciones": PROMPT_CLASIFICACION,
        "entrada": preparar_entrada(nodo, conceptos)
    }


def validar_respuesta(nodo, respuesta_json, conceptos):
    if isinstance(respuesta_json, str):
        respuesta = json.loads(respuesta_json)
    elif isinstance(respuesta_json, dict):
        respuesta = respuesta_json
    else:
        raise ValueError("Respuesta de IA inválida")

    if set(respuesta) != {"anclajes", "funciones"}:
        raise ValueError("Estructura de respuesta incorrecta")

    debate_minimo = {
        "nodes": [nodo],
        "edges": []
    }

    validar_clasificaciones(
        debate_minimo,
        {str(nodo["id"]): respuesta},
        conceptos
    )

    return respuesta


if __name__ == "__main__":
    nodo = {
        "id": "A",
        "claim": "La tecnología puede mejorar la seguridad pública."
    }

    conceptos = {
        "urn:ejemplo": {
            "label_es": "Seguridad",
            "label_en": "Security",
            "relaciones": {
                "broader": [],
                "narrower": [],
                "related": []
            }
        }
    }

    solicitud = preparar_solicitud(nodo, conceptos)

    respuesta = {
        "anclajes": [
            {
                "uri": "urn:ejemplo",
                "evidencia": "seguridad pública"
            }
        ],
        "funciones": ["pragmatica"]
    }

    resultado = validar_respuesta(nodo, respuesta, conceptos)

    assert solicitud["entrada"]["argumento"]["id"] == "A"
    assert resultado["anclajes"][0]["uri"] == "urn:ejemplo"

    print("PIPELINE DE CLASIFICACIÓN: OK")
