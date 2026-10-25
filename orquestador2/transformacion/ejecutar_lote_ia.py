from copy import deepcopy

from .motor import ejecutar_siguiente_operacion
from .registro import verificar_integridad_original
from .integridad_debate import verificar_conservacion_debate


def ejecutar_lote_ia(registro, entrada_b, conceptos_skos):
    """Ejecuta todas las operaciones pendientes con reversión completa."""

    verificar_integridad_original(registro, entrada_b)

    pendientes = [
        evento for evento in registro["transformaciones"]
        if evento["estado"] == "pendiente"
    ]

    if not pendientes:
        raise ValueError("No hay operaciones pendientes")

    if registro["grafo_transformado"] is None:
        raise ValueError("Primero debe inicializarse el grafo transformado")

    estado_anterior = deepcopy(registro)
    cantidad = len(pendientes)

    try:
        verificar_conservacion_debate(registro)

        for _ in range(cantidad):
            ejecutar_siguiente_operacion(
                registro, entrada_b, conceptos_skos
            )

        verificar_integridad_original(registro, entrada_b)
        verificar_conservacion_debate(registro)

    except Exception:
        registro.clear()
        registro.update(estado_anterior)
        raise

    return {
        "estado": "lote_ejecutado",
        "cantidad": cantidad,
    }


if __name__ == "__main__":
    from orquestador2.lectores.ontologia import cargar_ontologia
    from .registro import crear_registro_transformacion
    from .registro_operaciones import registrar_operacion
    from .inicializar_grafo import inicializar_grafo_transformado
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
    inicializar_grafo_transformado(registro, entrada)

    crear = {
        "operacion": "crear_nodo",
        "id_nuevo": "S1",
        "claim": "Articular igualdad y justicia",
        "justificacion": "Explorar una perspectiva.",
        "anclajes_skos": [igualdad, justicia],
        "rutas_skos": [ruta],
    }

    priorizar = {
        "operacion": "jerarquizar_nodo",
        "id_nodo": "S1",
        "prioridad": 0.8,
        "justificacion": "Destacar la perspectiva emergente.",
    }

    registrar_operacion(registro, entrada, crear)
    registrar_operacion(registro, entrada, priorizar)

    resultado = ejecutar_lote_ia(registro, entrada, conceptos)

    assert resultado["cantidad"] == 2
    assert len(registro["grafo_transformado"]["nodes"]) == 3
    assert all(
        e["estado"] == "ejecutada"
        for e in registro["transformaciones"]
    )

    print("EJECUCIÓN SECUENCIAL DEL LOTE: OK")
    print("DEPENDENCIA ENTRE OPERACIONES: OK")

    registro_fallo = crear_registro_transformacion(entrada)
    inicializar_grafo_transformado(registro_fallo, entrada)

    registrar_operacion(registro_fallo, entrada, crear)

    operacion_imposible = {
        "operacion": "retirar_nodo",
        "id_nodo": "A",
        "justificacion": "Prueba de reversión completa.",
    }

    registrar_operacion(
        registro_fallo, entrada, operacion_imposible
    )

    estado_anterior = deepcopy(registro_fallo)

    try:
        ejecutar_lote_ia(registro_fallo, entrada, conceptos)
    except ValueError:
        print("FALLO EN SEGUNDA OPERACIÓN: DETECTADO")
    else:
        raise AssertionError("Se ejecutó un lote inválido")

    assert registro_fallo == estado_anterior

    print("REVERSIÓN DE TODO EL LOTE: OK")
    print("GRAFO ORIGINAL INTACTO: OK")
