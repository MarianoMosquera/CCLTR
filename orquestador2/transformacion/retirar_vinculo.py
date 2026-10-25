from copy import deepcopy

from .registro import verificar_integridad_original
from .validacion_relaciones import validar_relacion


def ejecutar_retirada_vinculo(registro, entrada_b):
    """Retira un vínculo de la copia transformada con auditoría."""

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

    if propuesta["operacion"] != "retirar_vinculo":
        raise ValueError("La operación pendiente no es retirar_vinculo")

    validar_relacion(propuesta, grafo)

    coincidencias = [
        (indice, relacion)
        for indice, relacion in enumerate(grafo["edges"])
        if relacion.get("source") == propuesta["source"]
        and relacion.get("target") == propuesta["target"]
        and relacion.get("tipo", relacion.get("valence")) == propuesta["tipo"]
    ]

    if len(coincidencias) != 1:
        raise ValueError("La relación debe identificarse de forma única")

    indice, relacion = coincidencias[0]

    copia = deepcopy(grafo)
    retirada = copia["edges"].pop(indice)

    verificar_integridad_original(registro, entrada_b)

    registro["grafo_transformado"] = copia
    evento["estado"] = "ejecutada"
    evento["relacion_retirada"] = deepcopy(retirada)

    return deepcopy(evento)


if __name__ == "__main__":
    from .registro import crear_registro_transformacion
    from .registro_operaciones import registrar_operacion
    from .inicializar_grafo import inicializar_grafo_transformado
    from .crear_vinculo import ejecutar_creacion_vinculo

    debate = {
        "nodes": [
            {"id": "A", "claim": "Innovación"},
            {"id": "B", "claim": "Protección laboral"},
        ],
        "edges": [
            {"source": "A", "target": "B", "target_idx": 0, "valence": "CON"}
        ],
    }

    entrada = {
        "grafo_original": deepcopy(debate),
        "ontologia_skos": {},
    }

    registro = crear_registro_transformacion(entrada)
    inicializar_grafo_transformado(registro, entrada)

    registrar_operacion(registro, entrada, {
        "operacion": "crear_vinculo",
        "source": "A",
        "target": "B",
        "tipo": "complementariedad",
        "justificacion": "Explorar una conexión conceptual.",
    })

    ejecutar_creacion_vinculo(registro, entrada)

    assert len(registro["grafo_transformado"]["edges"]) == 2

    registrar_operacion(registro, entrada, {
        "operacion": "retirar_vinculo",
        "source": "A",
        "target": "B",
        "tipo": "complementariedad",
        "justificacion": "Reorganizar las conexiones conceptuales.",
    })

    resultado = ejecutar_retirada_vinculo(registro, entrada)

    assert resultado["estado"] == "ejecutada"
    assert resultado["relacion_retirada"]["tipo"] == "complementariedad"
    assert registro["grafo_transformado"]["edges"] == debate["edges"]
    assert registro["grafo_original"] == debate

    print("RETIRADA DE VÍNCULO: OK")
    print("RELACIÓN RETIRADA DOCUMENTADA: OK")
    print("RELACIÓN ORIGINAL PRO/CON CONSERVADA: OK")
    print("GRAFO ORIGINAL INTACTO: OK")
