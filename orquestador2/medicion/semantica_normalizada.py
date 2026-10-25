"""Normalización de diversidad semántica al intervalo [0, 1]."""

import math

from orquestador2.medicion.diversidad_semantica import (
    medir_diversidad_semantica,
)


def medir_semantica_normalizada(embeddings):
    resultado = medir_diversidad_semantica(embeddings)

    if resultado["estado"] != "calculado":
        return {
            **resultado,
            "diversidad_normalizada": None,
        }

    distancia = resultado["diversidad"]

    if not math.isfinite(distancia):
        raise ValueError("Distancia coseno no finita")

    if distancia < -1e-12 or distancia > 2 + 1e-12:
        raise ValueError("Distancia coseno fuera del intervalo esperado")

    normalizada = max(0.0, min(1.0, distancia / 2))

    return {
        **resultado,
        "diversidad_normalizada": normalizada,
    }


if __name__ == "__main__":
    embeddings = {
        "A": [1.0, 0.0],
        "B": [0.0, 1.0],
        "C": [1.0, 0.0],
    }

    resultado = medir_semantica_normalizada(embeddings)

    assert abs(resultado["diversidad"] - 2 / 3) < 1e-12
    assert abs(resultado["diversidad_normalizada"] - 1 / 3) < 1e-12
    assert resultado["pares"] == 3

    print("NORMALIZACIÓN SEMÁNTICA: OK")
    print("DISTANCIA ORIGINAL:", resultado["diversidad"])
    print("DIVERSIDAD NORMALIZADA:", resultado["diversidad_normalizada"])
