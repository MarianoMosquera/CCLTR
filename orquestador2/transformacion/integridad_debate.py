from collections import Counter
from copy import deepcopy
import json


def firma(elemento):
    return json.dumps(
        elemento, sort_keys=True, ensure_ascii=False
    )


def verificar_conservacion_debate(registro):
    original = registro["grafo_original"]
    transformado = registro["grafo_transformado"]

    if not isinstance(transformado, dict):
        raise ValueError("Grafo transformado no inicializado")

    nodos_originales = {
        str(n["id"]): n for n in original["nodes"]
    }

    nodos_transformados = {
        str(n["id"]): n for n in transformado["nodes"]
    }

    if len(nodos_transformados) != len(transformado["nodes"]):
        raise ValueError("Identificadores duplicados")

    for identificador, nodo in nodos_originales.items():
        if identificador not in nodos_transformados:
            raise ValueError("Se eliminó un nodo original")

        transformado_nodo = nodos_transformados[identificador]

        if transformado_nodo.get("id") != nodo.get("id"):
            raise ValueError("Se alteró un identificador original")

    relaciones_originales = Counter(
        firma(e) for e in original["edges"]
    )

    relaciones_transformadas = Counter(
        firma(e) for e in transformado["edges"]
    )

    for relacion, cantidad in relaciones_originales.items():
        if relaciones_transformadas[relacion] < cantidad:
            raise ValueError(
                "Se eliminó o modificó una relación original"
            )

    return True


if __name__ == "__main__":
    original = {
        "nodes": [
            {"id": "A", "claim": "Innovación"},
            {"id": "B", "claim": "Empleo"},
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

    registro = {
        "grafo_original": deepcopy(original),
        "grafo_transformado": deepcopy(original),
    }

    assert verificar_conservacion_debate(registro)
    print("DEBATE ORIGINAL CONSERVADO: OK")

    registro["grafo_transformado"]["edges"][0]["valence"] = "PRO"

    try:
        verificar_conservacion_debate(registro)
    except ValueError:
        print("ALTERACIÓN DE VALENCIA: BLOQUEADA")
    else:
        raise AssertionError("No se detectó alteración")

    registro["grafo_transformado"] = deepcopy(original)
    registro["grafo_transformado"]["nodes"].pop()

    try:
        verificar_conservacion_debate(registro)
    except ValueError:
        print("ELIMINACIÓN DE NODO ORIGINAL: BLOQUEADA")
    else:
        raise AssertionError("No se detectó eliminación")

    print("CONTROL DE INTEGRIDAD: OK")
