from copy import deepcopy

from .registro import verificar_integridad_original


def inicializar_grafo_transformado(registro, entrada_b):
    verificar_integridad_original(registro, entrada_b)

    if registro.get("grafo_transformado") is not None:
        raise ValueError("El grafo transformado ya fue inicializado")

    if registro.get("transformaciones"):
        raise ValueError(
            "No se puede inicializar después de registrar operaciones"
        )

    registro["grafo_transformado"] = deepcopy(
        registro["grafo_original"]
    )

    verificar_integridad_original(registro, entrada_b)

    return deepcopy(registro["grafo_transformado"])


if __name__ == "__main__":
    from .registro import crear_registro_transformacion

    debate = {
        "nodes": [
            {"id": "A", "claim": "La IA mejora la productividad"},
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

    transformado = inicializar_grafo_transformado(
        registro, entrada
    )

    assert transformado == debate
    assert transformado is not registro["grafo_original"]

    registro["grafo_transformado"]["nodes"][0]["claim"] = (
        "Nueva formulación experimental"
    )

    assert registro["grafo_original"] == debate
    assert entrada["grafo_original"] == debate

    print("GRAFO TRANSFORMADO INICIALIZADO: OK")
    print("COPIA INDEPENDIENTE: OK")
    print("GRAFO ORIGINAL CONSERVADO: OK")
