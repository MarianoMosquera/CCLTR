import json
from copy import deepcopy

from .operaciones import validar_operacion
from .rama_b import CAMPOS_PROHIBIDOS


def validar_respuesta_ia(respuesta):
    """Valida la estructura de una respuesta candidata de la rama B."""

    if isinstance(respuesta, str):
        try:
            respuesta = json.loads(respuesta)
        except json.JSONDecodeError as error:
            raise ValueError("La respuesta no contiene JSON válido") from error

    if not isinstance(respuesta, dict):
        raise ValueError("La respuesta debe ser un objeto JSON")

    if set(respuesta) != {"propuestas"}:
        raise ValueError("La respuesta debe contener solo 'propuestas'")

    propuestas = respuesta["propuestas"]

    if not isinstance(propuestas, list):
        raise ValueError("'propuestas' debe ser una lista")

    if not propuestas:
        raise ValueError("No se recibieron propuestas")

    for indice, propuesta in enumerate(propuestas, start=1):
        if not isinstance(propuesta, dict):
            raise ValueError(f"Propuesta {indice} inválida")

        contaminacion = CAMPOS_PROHIBIDOS.intersection(propuesta)

        if contaminacion:
            raise ValueError(
                f"Información de rama A en propuesta {indice}"
            )

        validar_operacion(propuesta)

    return {
        "estado": "estructura_validada",
        "cantidad": len(propuestas),
        "propuestas": deepcopy(propuestas),
    }


if __name__ == "__main__":
    valida = {
        "propuestas": [
            {
                "operacion": "crear_nodo",
                "id_nuevo": "S1",
                "claim": "Innovación con protección laboral",
                "justificacion": "Explorar una perspectiva alternativa.",
                "anclajes_skos": [],
                "rutas_skos": [],
                "tension_conservada": "Innovación frente a protección.",
                "aporte_conceptual": "Nueva articulación conceptual.",
            }
        ]
    }

    resultado = validar_respuesta_ia(json.dumps(valida))
    assert resultado["cantidad"] == 1
    print("RESPUESTA JSON RECONOCIDA: OK")

    invalida = deepcopy(valida)
    invalida["propuestas"][0]["operacion"] = "inventar_operacion"

    try:
        validar_respuesta_ia(invalida)
    except ValueError:
        print("OPERACIÓN DESCONOCIDA: BLOQUEADA")
    else:
        raise AssertionError("Se aceptó una operación desconocida")

    contaminada = deepcopy(valida)
    contaminada["propuestas"][0]["rama_a"] = {}

    try:
        validar_respuesta_ia(contaminada)
    except ValueError:
        print("CONTAMINACIÓN DE RAMA A: BLOQUEADA")
    else:
        raise AssertionError("Se aceptó información de rama A")

    print("VALIDADOR ESTRUCTURAL DE RESPUESTAS: OK")
