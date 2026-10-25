"""Riqueza SKOS estandarizada por tamaño de muestra."""

import random
from statistics import mean, pstdev


def riqueza_rarefactada(clasificaciones, tamano_muestra, repeticiones=1000, semilla=42):
    if not isinstance(tamano_muestra, int) or tamano_muestra < 1:
        raise ValueError("Tamaño de muestra inválido")
    if not isinstance(repeticiones, int) or repeticiones < 1:
        raise ValueError("Número de repeticiones inválido")

    argumentos = list(clasificaciones.values())

    if tamano_muestra > len(argumentos):
        raise ValueError("La muestra supera la cantidad de argumentos")

    rng = random.Random(semilla)
    resultados = []

    for _ in range(repeticiones):
        muestra = rng.sample(argumentos, tamano_muestra)
        conceptos = {
            anclaje["uri"]
            for argumento in muestra
            for anclaje in argumento["anclajes"]
        }
        resultados.append(len(conceptos))

    return {
        "riqueza_media": mean(resultados),
        "desviacion_estandar": pstdev(resultados),
        "tamano_muestra": tamano_muestra,
        "repeticiones": repeticiones,
        "semilla": semilla
    }


if __name__ == "__main__":
    clasificaciones = {
        "1": {"anclajes": [{"uri": "urn:A"}]},
        "2": {"anclajes": [{"uri": "urn:B"}]},
        "3": {"anclajes": [{"uri": "urn:C"}]},
        "4": {"anclajes": [{"uri": "urn:D"}]}
    }

    resultado = riqueza_rarefactada(
        clasificaciones,
        tamano_muestra=2,
        repeticiones=100,
        semilla=42
    )

    assert resultado["riqueza_media"] == 2
    assert resultado["desviacion_estandar"] == 0

    print("RAREFACCIÓN SKOS: OK")
    print("RIQUEZA MEDIA:", resultado["riqueza_media"])
    print("TAMAÑO DE MUESTRA:", resultado["tamano_muestra"])
