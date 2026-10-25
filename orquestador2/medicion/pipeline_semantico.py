from .generador_embeddings import cargar_modelo, generar_embeddings
from .diversidad_semantica import medir_diversidad_semantica
from .semantica_normalizada import medir_semantica_normalizada


def medir_grafo_semanticamente(grafo, modelo, config):
    embeddings = generar_embeddings(grafo, modelo, config)

    if len(embeddings) < 2:
        raise ValueError("Se requieren al menos dos argumentos")

    medicion = medir_diversidad_semantica(embeddings)
    normalizada = medir_semantica_normalizada(embeddings)

    return {
        "argumentos": len(embeddings),
        "modelo": config["modelo"],
        "revision": config["revision"],
        "medicion": medicion,
        "normalizada": normalizada,
    }


if __name__ == "__main__":
    modelo, config = cargar_modelo()

    grafo = {
        "nodes": [
            {"id": "A", "claim": "La inteligencia artificial mejora la productividad."},
            {"id": "B", "claim": "La inteligencia artificial puede desplazar trabajadores."},
            {"id": "C", "claim": "Los sistemas de inteligencia artificial requieren supervisión humana."},
        ],
        "edges": [],
    }

    resultado = medir_grafo_semanticamente(grafo, modelo, config)

    assert resultado["argumentos"] == 3
    assert 0 <= resultado["normalizada"]["diversidad_normalizada"] <= 1

    print("PIPELINE SEMÁNTICO: OK")
    print("ARGUMENTOS:", resultado["argumentos"])
    print("DIVERSIDAD COSENO:", round(resultado["medicion"]["diversidad"], 6))
    print(
        "DIVERSIDAD NORMALIZADA:",
        round(resultado["normalizada"]["diversidad_normalizada"], 6)
    )
