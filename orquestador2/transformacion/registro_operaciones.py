from copy import deepcopy

from .operaciones import validar_operacion
from .registro import verificar_integridad_original


def registrar_operacion(registro, entrada_b, operacion):
    """Registra una operación validada sin alterar el grafo original."""

    verificar_integridad_original(registro, entrada_b)

    if not isinstance(registro.get("transformaciones"), list):
        raise ValueError("Registro de transformaciones inválido")

    validar_operacion(operacion)

    numero = len(registro["transformaciones"]) + 1

    evento = {
        "secuencia": numero,
        "propuesta": deepcopy(operacion),
        "estado": "pendiente",
    }

    registro["transformaciones"].append(evento)

    verificar_integridad_original(registro, entrada_b)

    return deepcopy(evento)


if __name__ == "__main__":
    from .rama_b import preparar_rama_b
    from .registro import crear_registro_transformacion

    debate = {
        "nodes": [
            {"id": "A", "claim": "La IA mejora la productividad."},
            {"id": "B", "claim": "La IA puede desplazar empleos."},
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

    entrada = preparar_rama_b(
        debate,
        {"c1": {"label": "Responsabilidad"}}
    )

    registro = crear_registro_transformacion(entrada)

    operacion = {
        "operacion": "crear_nodo",
        "id_nuevo": "C",
        "claim": "La innovación requiere responsabilidad institucional.",
        "justificacion": "Explorar una alternativa conceptual.",
    }

    evento = registrar_operacion(registro, entrada, operacion)

    assert evento["secuencia"] == 1
    assert evento["estado"] == "pendiente"
    assert registro["grafo_original"] == debate
    assert registro["grafo_transformado"] is None

    operacion["claim"] = "Texto alterado"
    assert registro["transformaciones"][0]["propuesta"]["claim"] != "Texto alterado"

    try:
        registrar_operacion(
            registro,
            entrada,
            {
                "operacion": "crear_nodo",
                "id_nuevo": "D",
                "claim": 123,
                "justificacion": "Prueba inválida",
            },
        )
    except ValueError:
        pass
    else:
        raise AssertionError("No se rechazó la operación inválida")

    assert len(registro["transformaciones"]) == 1

    print("REGISTRO DE OPERACIONES: OK")
    print("OPERACIONES REGISTRADAS:", len(registro["transformaciones"]))
    print("ESTADO:", evento["estado"])
    print("GRAFO ORIGINAL CONSERVADO: OK")
    print("OPERACIÓN INVÁLIDA RECHAZADA: OK")
