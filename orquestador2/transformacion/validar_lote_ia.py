from copy import deepcopy

from .respuesta_ia import validar_respuesta_ia
from .politica_skos import evaluar_politica_skos
from .calidad_conceptual import validar_calidad_conceptual


def validar_lote_ia(respuesta, conceptos_skos):
    """Valida todas las propuestas antes de autorizar su registro."""

    if not isinstance(conceptos_skos, dict):
        raise TypeError("La ontología SKOS debe ser un diccionario")

    resultado = validar_respuesta_ia(respuesta)
    propuestas = resultado["propuestas"]
    verificaciones = []

    for indice, propuesta in enumerate(propuestas, start=1):
        try:
            fundamento = evaluar_politica_skos(
                propuesta, conceptos_skos
            )
            validar_calidad_conceptual(propuesta)
        except (ValueError, TypeError, KeyError) as error:
            raise ValueError(
                f"Propuesta {indice} rechazada: {error}"
            ) from error

        verificaciones.append({
            "indice": indice,
            "operacion": propuesta["operacion"],
            "categoria": fundamento["categoria"],
            "estado": fundamento["estado"],
        })

    return {
        "estado": "lote_validado",
        "cantidad": len(propuestas),
        "verificaciones": verificaciones,
        "propuestas": deepcopy(propuestas),
    }


if __name__ == "__main__":
    from orquestador2.lectores.ontologia import cargar_ontologia
    from .rutas_skos import buscar_rutas_skos

    conceptos = cargar_ontologia(".")

    igualdad = next(
        uri for uri, c in conceptos.items()
        if c.get("label_es") == "Igualdad"
    )
    justicia = next(
        uri for uri, c in conceptos.items()
        if c.get("label_es") == "Justicia"
    )

    ruta = next(
        r for r in buscar_rutas_skos(igualdad, conceptos, 2)
        if r["destino"] == justicia and r["longitud"] == 1
    )

    propuesta_valida = {
        "operacion": "crear_nodo",
        "id_nuevo": "S1",
        "claim": "Articular igualdad y justicia",
        "justificacion": "Explorar una perspectiva conceptual.",
        "anclajes_skos": [igualdad, justicia],
        "rutas_skos": [ruta],
        "tension_conservada": "Igualdad frente a justicia.",
        "aporte_conceptual": "Nueva articulación argumentativa.",
    }

    lote = {
        "propuestas": [
            propuesta_valida,
            {
                "operacion": "jerarquizar_nodo",
                "id_nodo": "S1",
                "prioridad": 0.7,
                "justificacion": "Priorizar para evaluación posterior.",
            },
        ]
    }

    resultado = validar_lote_ia(lote, conceptos)

    assert resultado["estado"] == "lote_validado"
    assert resultado["cantidad"] == 2
    print("LOTE COMPLETO VALIDADO: OK")

    lote_invalido = deepcopy(lote)
    lote_invalido["propuestas"][1] = {
        "operacion": "crear_nodo",
        "id_nuevo": "S2",
        "claim": "Propuesta sin fundamento",
        "justificacion": "Comprobar rechazo del lote.",
    }

    try:
        validar_lote_ia(lote_invalido, conceptos)
    except ValueError:
        print("LOTE CON PROPUESTA INVÁLIDA: BLOQUEADO")
    else:
        raise AssertionError("Se aceptó un lote inválido")

    assert lote["propuestas"][0] == propuesta_valida
    print("PROPUESTAS ORIGINALES CONSERVADAS: OK")
    print("VALIDACIÓN ATÓMICA PREVIA AL REGISTRO: OK")
