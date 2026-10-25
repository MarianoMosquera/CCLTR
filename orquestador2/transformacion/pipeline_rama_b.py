from copy import deepcopy

from .registro import verificar_integridad_original
from .registrar_lote_ia import registrar_lote_ia
from .ejecutar_lote_ia import ejecutar_lote_ia
from .integridad_debate import verificar_conservacion_debate


def procesar_respuesta_rama_b(registro, entrada_b, respuesta):
    """Valida, registra y ejecuta una respuesta completa de la rama B."""

    verificar_integridad_original(registro, entrada_b)

    if registro["grafo_transformado"] is None:
        raise ValueError("El grafo transformado debe estar inicializado")

    if any(
        evento["estado"] == "pendiente"
        for evento in registro["transformaciones"]
    ):
        raise ValueError(
            "No se admite un nuevo lote con operaciones anteriores pendientes"
        )

    conceptos = entrada_b["ontologia_skos"]
    estado_anterior = deepcopy(registro)

    try:
        verificar_conservacion_debate(registro)

        registro_lote = registrar_lote_ia(
            registro, entrada_b, respuesta, conceptos
        )

        ejecucion = ejecutar_lote_ia(
            registro, entrada_b, conceptos
        )

        verificar_integridad_original(registro, entrada_b)
        verificar_conservacion_debate(registro)

        from .validar_integracion import verificar_integracion_nodos_nuevos
        verificar_integracion_nodos_nuevos(
            entrada_b["grafo_original"], registro["grafo_transformado"]
        )

        if registro_lote["cantidad"] != ejecucion["cantidad"]:
            raise RuntimeError("Inconsistencia en cantidad de operaciones")

    except Exception:
        registro.clear()
        registro.update(estado_anterior)
        raise

    return {
        "estado": "respuesta_procesada",
        "operaciones": ejecucion["cantidad"],
        "grafo_transformado": deepcopy(registro["grafo_transformado"]),
    }


if __name__ == "__main__":
    from orquestador2.lectores.ontologia import cargar_ontologia
    from .registro import crear_registro_transformacion
    from .inicializar_grafo import inicializar_grafo_transformado
    from .rutas_skos import buscar_rutas_skos

    conceptos = cargar_ontologia(".")

    igualdad = next(
        uri for uri, concepto in conceptos.items()
        if concepto.get("label_es") == "Igualdad"
    )
    justicia = next(
        uri for uri, concepto in conceptos.items()
        if concepto.get("label_es") == "Justicia"
    )

    ruta = next(
        ruta for ruta in buscar_rutas_skos(igualdad, conceptos, 2)
        if ruta["destino"] == justicia and ruta["longitud"] == 1
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

    respuesta = {
        "propuestas": [
            {
                "operacion": "crear_nodo",
                "id_nuevo": "S1",
                "claim": "Articular igualdad y justicia",
                "justificacion": "Explorar una nueva perspectiva.",
                "anclajes_skos": [igualdad, justicia],
                "rutas_skos": [ruta],
                "tension_conservada": "Igualdad frente a justicia.",
                "aporte_conceptual": "Articulación alternativa.",
            },
            {
                "operacion": "jerarquizar_nodo",
                "id_nodo": "S1",
                "prioridad": 0.8,
                "justificacion": "Priorizar la perspectiva emergente.",
            },
            {
                "operacion": "crear_vinculo",
                "source": "S1",
                "target": "A",
                "tipo": "SIN_DEFINIR",
                "anclajes_skos": [igualdad, justicia],
                "rutas_skos": [ruta],
                "tension_conservada": "Igualdad frente a justicia.",
                "aporte_conceptual": "Integración argumentativa.",
                "justificacion": "Conectar la articulación conceptual con igualdad sin asignar apoyo u oposición.",
            },
        ]
    }

    registro = crear_registro_transformacion(entrada)
    inicializar_grafo_transformado(registro, entrada)

    resultado = procesar_respuesta_rama_b(
        registro, entrada, respuesta
    )

    assert resultado["estado"] == "respuesta_procesada"
    assert resultado["operaciones"] == 3
    assert len(resultado["grafo_transformado"]["nodes"]) == 3
    assert all(
        evento["estado"] == "ejecutada"
        for evento in registro["transformaciones"]
    )

    print("PIPELINE COMPLETO RAMA B: OK")
    print("REGISTRO Y EJECUCIÓN INTEGRADOS: OK")

    registro_fallo = crear_registro_transformacion(entrada)
    inicializar_grafo_transformado(registro_fallo, entrada)

    respuesta_fallo = deepcopy(respuesta)
    respuesta_fallo["propuestas"][1] = {
        "operacion": "retirar_nodo",
        "id_nodo": "A",
        "justificacion": "Comprobar reversión integral.",
    }

    estado_anterior = deepcopy(registro_fallo)

    try:
        procesar_respuesta_rama_b(
            registro_fallo, entrada, respuesta_fallo
        )
    except ValueError:
        print("FALLO DE EJECUCIÓN: DETECTADO")
    else:
        raise AssertionError("Se aceptó una operación imposible")

    assert registro_fallo == estado_anterior
    assert registro_fallo["grafo_original"] == debate

    registro_aislado = crear_registro_transformacion(entrada)
    inicializar_grafo_transformado(registro_aislado, entrada)
    antes_aislado = deepcopy(registro_aislado)
    respuesta_aislada = {"propuestas": [respuesta["propuestas"][0]]}
    try:
        procesar_respuesta_rama_b(registro_aislado, entrada, respuesta_aislada)
    except ValueError as exc:
        assert "sin integración" in str(exc)
    else:
        raise AssertionError("Se aceptó un nodo nuevo aislado")
    assert registro_aislado == antes_aislado

    print("REVERSIÓN INTEGRAL DEL PIPELINE: OK")
    print("DEBATE ORIGINAL INTACTO: OK")
