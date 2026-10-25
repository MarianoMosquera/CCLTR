from .operaciones import validar_operacion


def validar_referencias(operacion, grafo):
    """Comprueba referencias contra el grafo de trabajo, sin modificarlo."""

    validar_operacion(operacion)

    if not isinstance(grafo, dict) or not isinstance(grafo.get("nodes"), list):
        raise ValueError("Grafo de trabajo inválido")

    ids = [str(nodo["id"]) for nodo in grafo["nodes"]]

    if len(ids) != len(set(ids)):
        raise ValueError("Identificadores duplicados en el grafo")

    existentes = set(ids)
    tipo = operacion["operacion"]

    referencias = {
        "reformular_nodo": ["id_original"],
        "jerarquizar_nodo": ["id_nodo"],
        "retirar_nodo": ["id_nodo"],
        "crear_vinculo": ["source", "target"],
        "retirar_vinculo": ["source", "target"],
    }

    for campo in referencias.get(tipo, []):
        if operacion[campo] not in existentes:
            raise ValueError(f"Nodo inexistente: {operacion[campo]}")

    if tipo == "fusionar_nodos":
        faltantes = set(operacion["ids_origen"]) - existentes
        if faltantes:
            raise ValueError(f"Nodos inexistentes: {sorted(faltantes)}")

    if tipo in {"crear_nodo", "fusionar_nodos"}:
        if operacion["id_nuevo"] in existentes:
            raise ValueError("El identificador nuevo ya existe")

    return True


if __name__ == "__main__":
    grafo = {
        "nodes": [
            {"id": "A", "claim": "La IA mejora la productividad."},
            {"id": "B", "claim": "La IA puede desplazar empleos."},
        ],
        "edges": [
            {"source": "A", "target": "B", "target_idx": 0, "valence": "CON"}
        ],
    }

    valida = {
        "operacion": "fusionar_nodos",
        "ids_origen": ["A", "B"],
        "id_nuevo": "C",
        "claim": "Nueva perspectiva",
        "justificacion": "Explorar una síntesis.",
    }

    assert validar_referencias(valida, grafo)

    invalidas = [
        {**valida, "ids_origen": ["A", "Z"]},
        {**valida, "id_nuevo": "A"},
        {
            "operacion": "retirar_nodo",
            "id_nodo": "Z",
            "justificacion": "Prueba.",
        },
    ]

    for numero, operacion in enumerate(invalidas, 1):
        try:
            validar_referencias(operacion, grafo)
        except ValueError:
            print(f"REFERENCIA INVÁLIDA {numero}: BLOQUEADA")
        else:
            raise AssertionError("Se aceptó una referencia inválida")

    assert grafo["edges"][0]["valence"] == "CON"

    print("VALIDACIÓN DE REFERENCIAS: OK")
    print("GRAFO ORIGINAL SIN MODIFICACIONES: OK")
