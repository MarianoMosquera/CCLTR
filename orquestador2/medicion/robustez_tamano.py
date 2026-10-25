"""Comparación descriptiva del tamaño de los grafos A y B."""

from orquestador2.medicion.control_grafo import medir_estructura


def variacion_porcentual(inicial, final):
    if inicial == 0:
        return None
    return 100 * (final - inicial) / inicial


def comparar_tamanos(debate_a, debate_b):
    a = medir_estructura(debate_a)
    b = medir_estructura(debate_b)

    return {
        "estado": "calculado",
        "nodos_a": a["nodos"],
        "nodos_b": b["nodos"],
        "diferencia_nodos": b["nodos"] - a["nodos"],
        "variacion_nodos": variacion_porcentual(
            a["nodos"], b["nodos"]
        ),
        "aristas_a": a["aristas"],
        "aristas_b": b["aristas"],
        "diferencia_aristas": b["aristas"] - a["aristas"],
        "variacion_aristas": variacion_porcentual(
            a["aristas"], b["aristas"]
        ),
        "valencias_a": a["valencias"],
        "valencias_b": b["valencias"],
        "densidad_a": a["densidad_dirigida"],
        "densidad_b": b["densidad_dirigida"],
    }


if __name__ == "__main__":
    a = {
        "nodes": [
            {"id": "A", "claim": "Argumento A"},
            {"id": "B", "claim": "Argumento B"},
        ],
        "edges": [
            {"source": "B", "target": "A",
             "valence": "CON", "target_idx": 0},
        ],
    }

    b = {
        "nodes": [
            {"id": "A", "claim": "Argumento A"},
            {"id": "B", "claim": "Argumento B"},
            {"id": "C", "claim": "Argumento C"},
        ],
        "edges": [
            {"source": "B", "target": "A",
             "valence": "CON", "target_idx": 0},
            {"source": "C", "target": "A",
             "valence": "PRO", "target_idx": 1},
        ],
    }

    resultado = comparar_tamanos(a, b)

    assert resultado["diferencia_nodos"] == 1
    assert resultado["variacion_nodos"] == 50.0
    assert resultado["diferencia_aristas"] == 1
    assert resultado["variacion_aristas"] == 100.0

    print("ROBUSTEZ POR TAMAÑO: OK")
    print("NODOS A/B:", resultado["nodos_a"], resultado["nodos_b"])
    print("VARIACIÓN NODOS:", resultado["variacion_nodos"], "%")
    print("VARIACIÓN ARISTAS:", resultado["variacion_aristas"], "%")
