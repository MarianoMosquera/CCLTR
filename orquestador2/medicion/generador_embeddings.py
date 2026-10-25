import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


CONFIGURACION = Path(__file__).with_name("modelo_embeddings.json")


def cargar_modelo():
    config = json.loads(CONFIGURACION.read_text(encoding="utf-8"))

    modelo = SentenceTransformer(
        config["modelo"],
        revision=config["revision"],
        device=config["dispositivo_referencia"],
        local_files_only=True,
    )

    if modelo.get_embedding_dimension() != config["dimensiones"]:
        raise ValueError("Dimensiones incompatibles con la configuración")

    return modelo, config


def generar_embeddings(grafo, modelo, config):
    nodos = grafo["nodes"]
    ids = [nodo["id"] for nodo in nodos]
    textos = [nodo["claim"] for nodo in nodos]

    if len(ids) != len(set(ids)):
        raise ValueError("Identificadores de argumentos duplicados")

    if not all(isinstance(t, str) and t.strip() for t in textos):
        raise ValueError("Hay argumentos sin texto válido")

    if not textos:
        return {}

    longitudes = [
        len(modelo.tokenizer(
            texto,
            add_special_tokens=True,
            truncation=False
        )["input_ids"])
        for texto in textos
    ]

    excedidos = [
        (identificador, longitud)
        for identificador, longitud in zip(ids, longitudes)
        if longitud > modelo.max_seq_length
    ]

    if excedidos:
        raise ValueError(
            f"Argumentos que superan {modelo.max_seq_length} tokens: "
            f"{excedidos[:10]}. No se generaron embeddings."
        )

    vectores = modelo.encode(
        textos,
        normalize_embeddings=config["normalizar_embeddings"],
        show_progress_bar=False,
        convert_to_numpy=True,
    )

    if vectores.shape != (len(ids), config["dimensiones"]):
        raise ValueError("Dimensiones incorrectas en los embeddings")

    if not np.isfinite(vectores).all():
        raise ValueError("Los embeddings contienen valores no finitos")

    return {
        identificador: vector.astype(float).tolist()
        for identificador, vector in zip(ids, vectores)
    }


if __name__ == "__main__":
    modelo, config = cargar_modelo()

    grafo_prueba = {
        "nodes": [
            {"id": "A", "claim": "La inteligencia artificial mejora la productividad."},
            {"id": "B", "claim": "La inteligencia artificial puede desplazar trabajadores."},
        ],
        "edges": [],
    }

    resultado = generar_embeddings(grafo_prueba, modelo, config)

    assert set(resultado) == {"A", "B"}
    assert all(len(vector) == 384 for vector in resultado.values())

    print("GENERADOR DE EMBEDDINGS: OK")
    print("ARGUMENTOS:", len(resultado))
    print("DIMENSIONES:", config["dimensiones"])
    print("MODELO:", config["modelo"])
