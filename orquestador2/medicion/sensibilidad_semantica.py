"""Sensibilidad semántica con tamaños muestrales iguales."""

import random
from statistics import mean, pstdev

from orquestador2.medicion.semantica_normalizada import (
    medir_semantica_normalizada,
)


def sensibilidad_semantica(
    embeddings_a,
    embeddings_b,
    tamano_muestra,
    repeticiones=1000,
    semilla=42,
):
    if isinstance(tamano_muestra, bool) or not isinstance(tamano_muestra, int) or tamano_muestra < 2:
        raise ValueError("La muestra debe contener al menos dos argumentos")

    if isinstance(repeticiones, bool) or not isinstance(repeticiones, int) or repeticiones < 1:
        raise ValueError("Número de repeticiones inválido")

    if tamano_muestra > min(len(embeddings_a), len(embeddings_b)):
        raise ValueError("Muestra mayor que alguna de las ramas")

    rng = random.Random(semilla)
    ids_a = sorted(embeddings_a)
    ids_b = sorted(embeddings_b)

    diferencias = []
    valores_a = []
    valores_b = []

    for _ in range(repeticiones):
        muestra_a = rng.sample(ids_a, tamano_muestra)
        muestra_b = rng.sample(ids_b, tamano_muestra)

        a = medir_semantica_normalizada({
            i: embeddings_a[i] for i in muestra_a
        })
        b = medir_semantica_normalizada({
            i: embeddings_b[i] for i in muestra_b
        })

        if a["estado"] != "calculado" or b["estado"] != "calculado":
            raise ValueError("Medición semántica incompleta")

        valor_a = a["diversidad_normalizada"]
        valor_b = b["diversidad_normalizada"]

        valores_a.append(valor_a)
        valores_b.append(valor_b)
        diferencias.append(valor_b - valor_a)

    ordenadas = sorted(diferencias)

    return {
        "estado": "calculado",
        "tamano_muestra": tamano_muestra,
        "repeticiones": repeticiones,
        "media_a": mean(valores_a),
        "media_b": mean(valores_b),
        "diferencia_media": mean(diferencias),
        "desviacion_diferencias": pstdev(diferencias),
        "proporcion_aumentos": sum(d > 0 for d in diferencias) / repeticiones,
        "intervalo_percentil_descriptivo": [
            ordenadas[int(0.025 * (repeticiones - 1))],
            ordenadas[int(0.975 * (repeticiones - 1))],
        ],
    }


if __name__ == "__main__":
    a = {
        "A": [1.0, 0.0],
        "B": [1.0, 0.0],
        "C": [1.0, 0.0],
    }

    b = {
        "A": [1.0, 0.0],
        "B": [0.0, 1.0],
        "C": [-1.0, 0.0],
    }

    resultado = sensibilidad_semantica(
        a, b, tamano_muestra=2, repeticiones=100, semilla=42
    )

    assert resultado["media_a"] == 0.0
    assert resultado["diferencia_media"] > 0
    assert resultado["proporcion_aumentos"] == 1.0

    print("SENSIBILIDAD SEMÁNTICA: OK")
    print("MUESTRA:", resultado["tamano_muestra"])
    print("DIFERENCIA MEDIA:", round(resultado["diferencia_media"], 4))
    print("PROPORCIÓN DE AUMENTOS:", resultado["proporcion_aumentos"])
