"""Diversidad semántica mediante distancia coseno entre embeddings."""

import math


def medir_diversidad_semantica(embeddings):
    """Calcula distancia coseno media entre todos los pares de vectores."""

    if not isinstance(embeddings, dict):
        raise ValueError("Los embeddings deben ser un diccionario")

    if len(embeddings) < 2:
        return {
            "diversidad": None,
            "pares": 0,
            "estado": "datos_insuficientes"
        }

    vectores = list(embeddings.values())
    dimension = len(vectores[0])

    if dimension == 0:
        raise ValueError("Vectores vacíos")

    normalizados = []

    for vector in vectores:
        if len(vector) != dimension:
            raise ValueError("Dimensiones incompatibles")

        if not all(math.isfinite(x) for x in vector):
            raise ValueError("Valores no finitos")

        norma = math.sqrt(sum(x * x for x in vector))

        if norma == 0:
            raise ValueError("Vector de norma cero")

        normalizados.append([x / norma for x in vector])

    suma = 0.0
    pares = 0

    for i in range(len(normalizados)):
        for j in range(i + 1, len(normalizados)):
            similitud = sum(
                a * b
                for a, b in zip(normalizados[i], normalizados[j])
            )
            similitud = max(-1.0, min(1.0, similitud))
            suma += 1.0 - similitud
            pares += 1

    return {
        "diversidad": suma / pares,
        "pares": pares,
        "estado": "calculado"
    }


if __name__ == "__main__":
    embeddings = {
        "A": [1.0, 0.0],
        "B": [0.0, 1.0],
        "C": [1.0, 0.0]
    }

    resultado = medir_diversidad_semantica(embeddings)

    assert abs(resultado["diversidad"] - (2 / 3)) < 1e-12
    assert resultado["pares"] == 3

    print("DIVERSIDAD SEMÁNTICA: OK")
    print("DISTANCIA COSENO MEDIA:", resultado["diversidad"])
    print("PARES COMPARADOS:", resultado["pares"])
