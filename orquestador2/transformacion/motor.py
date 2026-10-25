from copy import deepcopy
from .registro import verificar_integridad_original
from .integridad_debate import verificar_conservacion_debate
from .ejecutor import ejecutar_creacion_nodo
from .reformular import ejecutar_reformulacion
from .fusionar import ejecutar_fusion
from .crear_vinculo import ejecutar_creacion_vinculo
from .retirar_vinculo import ejecutar_retirada_vinculo
from .jerarquizar import ejecutar_jerarquizacion
from .retirar_nodo import ejecutar_retirada_nodo


EJECUTORES = {
    "crear_nodo": ejecutar_creacion_nodo,
    "reformular_nodo": ejecutar_reformulacion,
    "fusionar_nodos": ejecutar_fusion,
    "crear_vinculo": ejecutar_creacion_vinculo,
    "retirar_vinculo": ejecutar_retirada_vinculo,
    "jerarquizar_nodo": ejecutar_jerarquizacion,
    "retirar_nodo": ejecutar_retirada_nodo,
}


def ejecutar_siguiente_operacion(registro, entrada_b, conceptos_skos=None):
    """Despacha la primera operación pendiente al ejecutor correspondiente."""

    verificar_integridad_original(registro, entrada_b)

    pendientes = [
        evento for evento in registro["transformaciones"]
        if evento["estado"] == "pendiente"
    ]

    if not pendientes:
        raise ValueError("No hay operaciones pendientes")

    tipo = pendientes[0]["propuesta"]["operacion"]

    if tipo not in EJECUTORES:
        raise ValueError(f"Operación sin ejecutor: {tipo}")

    estado_anterior = deepcopy(registro)

    try:
        verificar_conservacion_debate(registro)

        if conceptos_skos is not None:
            from .politica_skos import evaluar_politica_skos
            evaluar_politica_skos(
                pendientes[0]["propuesta"],
                conceptos_skos
            )

        resultado = EJECUTORES[tipo](registro, entrada_b)

        verificar_integridad_original(registro, entrada_b)
        verificar_conservacion_debate(registro)

    except Exception:
        registro.clear()
        registro.update(estado_anterior)
        raise

    return resultado


if __name__ == "__main__":
    from copy import deepcopy
    from .registro import crear_registro_transformacion
    from .registro_operaciones import registrar_operacion
    from .inicializar_grafo import inicializar_grafo_transformado

    debate = {
        "nodes": [
            {"id": "A", "claim": "La IA mejora la productividad"},
            {"id": "B", "claim": "La IA puede desplazar empleos"},
        ],
        "edges": [
            {"source": "A", "target": "B",
             "target_idx": 0, "valence": "CON"}
        ],
    }

    entrada = {
        "grafo_original": deepcopy(debate),
        "ontologia_skos": {},
    }

    registro = crear_registro_transformacion(entrada)
    inicializar_grafo_transformado(registro, entrada)

    propuestas = [
        {
            "operacion": "crear_nodo",
            "id_nuevo": "C",
            "claim": "Innovación con protección laboral",
            "justificacion": "Explorar una tercera perspectiva.",
        },
        {
            "operacion": "jerarquizar_nodo",
            "id_nodo": "C",
            "prioridad": 0.8,
            "justificacion": "Priorizar la perspectiva emergente.",
        },
        {
            "operacion": "crear_vinculo",
            "source": "A",
            "target": "C",
            "tipo": "relacion_conceptual",
            "justificacion": "Vincular innovación y protección.",
        },
    ]

    for propuesta in propuestas:
        registrar_operacion(registro, entrada, propuesta)
        resultado = ejecutar_siguiente_operacion(registro, entrada)
        assert resultado["estado"] == "ejecutada"

    grafo = registro["grafo_transformado"]

    assert len(grafo["nodes"]) == 3
    assert len(grafo["edges"]) == 2
    assert grafo["nodes"][2]["prioridad_semantica"] == 0.8
    assert registro["grafo_original"] == debate
    assert all(
        evento["estado"] == "ejecutada"
        for evento in registro["transformaciones"]
    )

    print("MOTOR INTEGRADO: OK")
    print("OPERACIONES DISPONIBLES:", len(EJECUTORES))
    print("OPERACIONES EJECUTADAS:", len(registro["transformaciones"]))
    print("TRAZABILIDAD CONSERVADA: OK")
    print("GRAFO ORIGINAL INTACTO: OK")
