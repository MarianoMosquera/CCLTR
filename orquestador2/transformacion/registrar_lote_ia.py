from copy import deepcopy

from .validar_lote_ia import validar_lote_ia
from .registro_operaciones import registrar_operacion
from .registro import verificar_integridad_original


def registrar_lote_ia(registro, entrada_b, respuesta, conceptos_skos):
    """Valida y registra un lote completo sin modificaciones parciales."""

    verificar_integridad_original(registro, entrada_b)

    validacion = validar_lote_ia(respuesta, conceptos_skos)
    estado_anterior = deepcopy(registro)

    try:
        eventos = []

        for propuesta in validacion["propuestas"]:
            evento = registrar_operacion(
                registro, entrada_b, propuesta
            )
            eventos.append(deepcopy(evento))

        verificar_integridad_original(registro, entrada_b)

    except Exception:
        registro.clear()
        registro.update(estado_anterior)
        raise

    return {
        "estado": "lote_registrado",
        "cantidad": len(eventos),
        "eventos": eventos,
    }


if __name__ == "__main__":
    from orquestador2.lectores.ontologia import cargar_ontologia
    from .rutas_skos import buscar_rutas_skos
    from .registro import crear_registro_transformacion

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

    debate = {
        "nodes": [
            {"id": "A", "claim": "Priorizar igualdad"},
            {"id": "B", "claim": "Priorizar justicia"},
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
        "ontologia_skos": deepcopy(conceptos),
    }

    registro = crear_registro_transformacion(entrada)

    lote = {
        "propuestas": [
            {
                "operacion": "crear_nodo",
                "id_nuevo": "S1",
                "claim": "Articular igualdad y justicia",
                "justificacion": "Explorar una nueva perspectiva.",
                "anclajes_skos": [igualdad, justicia],
                "rutas_skos": [ruta],
                "tension_conservada": "Igualdad y justicia en tensión.",
                "aporte_conceptual": "Articulación alternativa.",
            },
            {
                "operacion": "jerarquizar_nodo",
                "id_nodo": "S1",
                "prioridad": 0.8,
                "justificacion": "Priorizar la nueva perspectiva.",
            },
        ]
    }

    resultado = registrar_lote_ia(
        registro, entrada, lote, conceptos
    )

    assert resultado["cantidad"] == 2
    assert len(registro["transformaciones"]) == 2
    assert all(
        e["estado"] == "pendiente"
        for e in registro["transformaciones"]
    )

    print("LOTE COMPLETO REGISTRADO: OK")
    print("OPERACIONES PENDIENTES:", resultado["cantidad"])

    estado_anterior = deepcopy(registro)

    lote_invalido = deepcopy(lote)
    lote_invalido["propuestas"][1]["prioridad"] = 5

    try:
        registrar_lote_ia(
            registro, entrada, lote_invalido, conceptos
        )
    except ValueError:
        print("LOTE INVÁLIDO RECHAZADO: OK")
    else:
        raise AssertionError("Se aceptó un lote inválido")

    assert registro == estado_anterior
    print("REGISTRO SIN MODIFICACIONES PARCIALES: OK")
    print("GRAFO ORIGINAL CONSERVADO: OK")
