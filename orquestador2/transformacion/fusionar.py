from copy import deepcopy

from .registro import verificar_integridad_original
from .validacion_referencias import validar_referencias


def ejecutar_fusion(registro, entrada_b):
    """Crea un nodo de síntesis sin eliminar las perspectivas originales."""

    verificar_integridad_original(registro, entrada_b)

    grafo = registro.get("grafo_transformado")
    if not isinstance(grafo, dict):
        raise ValueError("El grafo transformado no está inicializado")

    pendientes = [
        evento for evento in registro["transformaciones"]
        if evento["estado"] == "pendiente"
    ]

    if not pendientes:
        raise ValueError("No hay operaciones pendientes")

    evento = pendientes[0]
    propuesta = evento["propuesta"]

    if propuesta["operacion"] != "fusionar_nodos":
        raise ValueError("La operación pendiente no es fusionar_nodos")

    validar_referencias(propuesta, grafo)

    copia = deepcopy(grafo)
    origenes = set(propuesta["ids_origen"])

    antecedentes = [
        {
            "id": nodo["id"],
            "claim": nodo["claim"],
        }
        for nodo in copia["nodes"]
        if str(nodo["id"]) in origenes
    ]

    if len(antecedentes) != len(origenes):
        raise ValueError("No se recuperaron todos los antecedentes")

    nuevo = {
        "id": propuesta["id_nuevo"],
        "claim": propuesta["claim"],
        "origen": "fusion_semantica",
        "antecedentes": antecedentes,
        "secuencia_transformacion": evento["secuencia"],
        "justificacion": propuesta["justificacion"],
    }

    copia["nodes"].append(nuevo)

    registro["grafo_transformado"] = copia
    evento["estado"] = "ejecutada"

    verificar_integridad_original(registro, entrada_b)

    return deepcopy(evento)


if __name__ == "__main__":
    from .registro import crear_registro_transformacion
    from .registro_operaciones import registrar_operacion
    from .inicializar_grafo import inicializar_grafo_transformado

    debate = {
        "nodes": [
            {"id": "A", "claim": "La IA aumenta la productividad"},
            {"id": "B", "claim": "La IA desplaza empleos"},
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

    registrar_operacion(registro, entrada, {
        "operacion": "fusionar_nodos",
        "ids_origen": ["A", "B"],
        "id_nuevo": "C",
        "claim": (
            "La innovación tecnológica debe incorporar "
            "mecanismos de protección y adaptación laboral"
        ),
        "justificacion": (
            "Construir una nueva perspectiva sin eliminar "
            "la tensión entre productividad y empleo."
        ),
    })

    resultado = ejecutar_fusion(registro, entrada)

    nodos = registro["grafo_transformado"]["nodes"]
    sintesis = nodos[-1]

    assert resultado["estado"] == "ejecutada"
    assert len(nodos) == 3
    assert len(sintesis["antecedentes"]) == 2
    assert {n["id"] for n in sintesis["antecedentes"]} == {"A", "B"}
    assert registro["grafo_original"] == debate
    assert registro["grafo_transformado"]["edges"] == debate["edges"]

    print("FUSIÓN CON TRAZABILIDAD: OK")
    print("PERSPECTIVAS ORIGINALES CONSERVADAS: OK")
    print("ANTECEDENTES DOCUMENTADOS: OK")
    print("CONTRADICCIÓN ESTRUCTURAL CONSERVADA: OK")
    print("GRAFO ORIGINAL INTACTO: OK")
