"""Control estructural de grafos argumentativos."""

from collections import Counter


def medir_estructura(debate):
    nodos = debate["nodes"]
    aristas = debate["edges"]

    ids = {str(n["id"]) for n in nodos}

    if len(ids) != len(nodos):
        raise ValueError("Existen identificadores de nodos duplicados")

    entradas = Counter()
    salidas = Counter()
    valencias = Counter()

    for arista in aristas:
        source = str(arista["source"])
        target = str(arista["target"])

        if source not in ids or target not in ids:
            raise ValueError("Arista con nodo inexistente")

        salidas[source] += 1
        entradas[target] += 1
        valencias[str(arista.get("valence", "SIN_VALENCIA"))] += 1

    return {
        "nodos": len(nodos),
        "aristas": len(aristas),
        "valencias": dict(sorted(valencias.items())),
        "nodos_sin_entradas": sum(entradas[n] == 0 for n in ids),
        "nodos_sin_salidas": sum(salidas[n] == 0 for n in ids),
        "grado_entrada_maximo": max(entradas.values(), default=0),
        "grado_salida_maximo": max(salidas.values(), default=0),
        "densidad_dirigida": (
            len(aristas) / (len(nodos) * (len(nodos) - 1))
            if len(nodos) > 1 else None
        ),
    }


if __name__ == "__main__":
    debate = {
        "nodes": [
            {"id": "A", "claim": "Argumento central"},
            {"id": "B", "claim": "Argumento favorable"},
            {"id": "C", "claim": "Argumento contrario"},
        ],
        "edges": [
            {"source": "B", "target": "A", "valence": "PRO", "target_idx": 0},
            {"source": "C", "target": "A", "valence": "CON", "target_idx": 1},
        ],
    }

    resultado = medir_estructura(debate)

    assert resultado["nodos"] == 3
    assert resultado["aristas"] == 2
    assert resultado["valencias"] == {"CON": 1, "PRO": 1}
    assert resultado["nodos_sin_salidas"] == 1
    assert abs(resultado["densidad_dirigida"] - 1 / 3) < 1e-12

    print("CONTROL ESTRUCTURAL: OK")
    print("NODOS:", resultado["nodos"])
    print("ARISTAS:", resultado["aristas"])
    print("VALENCIAS:", resultado["valencias"])
