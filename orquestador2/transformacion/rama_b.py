from copy import deepcopy


CAMPOS_PROHIBIDOS = {
    "rama_a",
    "clasificaciones",
    "indicadores",
    "diversidad",
    "resultados_rama_a",
    "ponderaciones_rama_a",
}


def preparar_rama_b(debate_original, conceptos_skos):
    """Prepara una entrada independiente para transformación semántica."""

    if not isinstance(debate_original, dict):
        raise TypeError("El debate debe ser un diccionario")

    if not isinstance(conceptos_skos, dict):
        raise TypeError("Los conceptos SKOS deben ser un diccionario")

    contaminacion = CAMPOS_PROHIBIDOS.intersection(debate_original)

    if contaminacion:
        raise ValueError(
            f"Información prohibida de la rama A: {sorted(contaminacion)}"
        )

    if "nodes" not in debate_original or "edges" not in debate_original:
        raise ValueError("El grafo debe contener nodes y edges")

    return {
        "grafo_original": deepcopy(debate_original),
        "ontologia_skos": deepcopy(conceptos_skos),
    }


if __name__ == "__main__":
    debate = {
        "nodes": [
            {"id": "A", "claim": "La IA mejora la productividad."},
            {"id": "B", "claim": "La IA puede desplazar empleos."},
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

    conceptos = {
        "concepto_1": {"label": "Responsabilidad"},
        "concepto_2": {"label": "Innovación"},
    }

    entrada = preparar_rama_b(debate, conceptos)

    assert entrada["grafo_original"] == debate
    assert entrada["ontologia_skos"] == conceptos
    assert set(entrada) == {"grafo_original", "ontologia_skos"}

    entrada["grafo_original"]["nodes"][0]["claim"] = "Texto modificado"
    assert debate["nodes"][0]["claim"] == "La IA mejora la productividad."

    try:
        preparar_rama_b({**debate, "resultados_rama_a": {}}, conceptos)
    except ValueError:
        pass
    else:
        raise AssertionError("No se bloqueó la información prohibida")

    print("ENTRADA INDEPENDIENTE RAMA B: OK")
    print("NODOS ORIGINALES:", len(debate["nodes"]))
    print("RELACIONES ORIGINALES:", len(debate["edges"]))
    print("INDEPENDENCIA DE COPIAS: OK")
    print("BLOQUEO DE RESULTADOS RAMA A: OK")
