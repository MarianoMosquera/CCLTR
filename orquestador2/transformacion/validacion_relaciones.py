from .validacion_referencias import validar_referencias


def validar_relacion(operacion, grafo):
    """Valida vínculos del grafo de trabajo sin modificarlo."""

    validar_referencias(operacion, grafo)

    tipo_operacion = operacion["operacion"]

    if tipo_operacion not in {"crear_vinculo", "retirar_vinculo"}:
        return True

    source = operacion["source"]
    target = operacion["target"]
    tipo = operacion["tipo"]

    if source == target:
        raise ValueError("No se permiten autovínculos")

    relaciones = grafo.get("edges", [])

    if not isinstance(relaciones, list):
        raise ValueError("Lista de relaciones inválida")

    coincidencias = [
        relacion for relacion in relaciones
        if relacion.get("source") == source
        and relacion.get("target") == target
        and relacion.get("tipo", relacion.get("valence")) == tipo
    ]

    if tipo_operacion == "crear_vinculo" and coincidencias:
        raise ValueError("La relación conceptual ya existe")

    if tipo_operacion == "retirar_vinculo" and not coincidencias:
        raise ValueError("La relación conceptual no existe")

    return True


if __name__ == "__main__":
    grafo = {
        "nodes": [
            {"id": "A", "claim": "Innovación tecnológica"},
            {"id": "B", "claim": "Responsabilidad institucional"},
        ],
        "edges": [
            {
                "source": "A",
                "target": "B",
                "target_idx": 0,
                "valence": "CON",
            },
            {
                "source": "A",
                "target": "B",
                "tipo": "complementariedad",
            },
        ],
    }

    def operacion(accion, tipo):
        return {
            "operacion": accion,
            "source": "A",
            "target": "B",
            "tipo": tipo,
            "justificacion": "Prueba de relación conceptual.",
        }

    assert validar_relacion(
        operacion("retirar_vinculo", "complementariedad"), grafo
    )

    assert validar_relacion(
        operacion("crear_vinculo", "tension_conservada"), grafo
    )

    invalidas = [
        operacion("crear_vinculo", "complementariedad"),
        operacion("retirar_vinculo", "inexistente"),
        operacion("crear_vinculo", "CON"),
        operacion("retirar_vinculo", "PRO"),
    ]

    for numero, propuesta in enumerate(invalidas, 1):
        try:
            validar_relacion(propuesta, grafo)
        except ValueError:
            print(f"RELACIÓN INVÁLIDA {numero}: BLOQUEADA")
        else:
            raise AssertionError("Se aceptó una relación inválida")

    assert grafo["edges"][0]["valence"] == "CON"

    print("VALIDACIÓN DE RELACIONES: OK")
    print("RELACIONES PRO/CON PROTEGIDAS: OK")
    print("GRAFO SIN MODIFICACIONES: OK")
