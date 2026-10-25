from copy import deepcopy


def crear_registro_transformacion(entrada_b):
    """Conserva el grafo original y separa las futuras transformaciones."""

    if set(entrada_b) != {"grafo_original", "ontologia_skos"}:
        raise ValueError("Entrada B incompatible con la estructura esperada")

    grafo = entrada_b["grafo_original"]

    if not isinstance(grafo, dict):
        raise TypeError("El grafo original debe ser un diccionario")

    if not isinstance(grafo.get("nodes"), list):
        raise ValueError("Los nodos originales deben formar una lista")

    if not isinstance(grafo.get("edges"), list):
        raise ValueError("Las relaciones originales deben formar una lista")

    return {
        "grafo_original": deepcopy(grafo),
        "ontologia_skos": deepcopy(entrada_b["ontologia_skos"]),
        "transformaciones": [],
        "grafo_transformado": None,
    }


def verificar_integridad_original(registro, entrada_b):
    """Comprueba que nodos y relaciones originales siguen intactos."""

    if registro["grafo_original"] != entrada_b["grafo_original"]:
        raise ValueError("Se modificó el grafo original")

    return True


if __name__ == "__main__":
    from .rama_b import preparar_rama_b

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

    entrada = preparar_rama_b(debate, {"c1": {"label": "Innovación"}})
    registro = crear_registro_transformacion(entrada)

    assert verificar_integridad_original(registro, entrada)
    assert registro["transformaciones"] == []
    assert registro["grafo_transformado"] is None

    registro["transformaciones"].append({
        "operacion": "crear_nodo",
        "id_nuevo": "C",
        "justificacion": "Ejemplo sintético",
    })

    assert verificar_integridad_original(registro, entrada)

    registro["grafo_original"]["edges"][0]["valence"] = "PRO"

    try:
        verificar_integridad_original(registro, entrada)
    except ValueError:
        print("ALTERACIÓN DE RELACIONES DETECTADA: OK")
    else:
        raise AssertionError("No se detectó la alteración")

    print("REGISTRO DE TRANSFORMACIONES: OK")
    print("GRAFO ORIGINAL PROTEGIDO: OK")
    print("TRANSFORMACIONES SEPARADAS: OK")
