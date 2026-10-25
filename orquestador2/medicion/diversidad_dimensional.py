"""Diversidad dimensional de argumentos clasificados mediante SKOS."""

import math

DIMENSIONES = ("Valores", "Agenda", "Racionalidad", "Gobernanza")


def medir_diversidad_dimensional(clasificaciones, mapa_dimensiones):
    conteos = {dimension: 0.0 for dimension in DIMENSIONES}
    sin_dimension = 0

    for registro in clasificaciones.values():
        dimensiones = set()

        for anclaje in registro["anclajes"]:
            uri = anclaje["uri"]
            if uri not in mapa_dimensiones:
                raise ValueError(f"Concepto sin registro dimensional: {uri}")

            dimensiones.update(
                d for d in mapa_dimensiones[uri]["dimensiones"]
                if d in DIMENSIONES
            )

        if not dimensiones:
            sin_dimension += 1
            continue

        peso = 1.0 / len(dimensiones)

        for dimension in dimensiones:
            conteos[dimension] += peso

    total = sum(conteos.values())

    if total == 0:
        return {
            "diversidad": None,
            "conteos": conteos,
            "sin_dimension": sin_dimension,
            "estado": "sin_datos"
        }

    probabilidades = [valor / total for valor in conteos.values()]

    entropia = -sum(
        p * math.log(p) for p in probabilidades if p > 0
    )

    diversidad = entropia / math.log(len(DIMENSIONES))

    return {
        "diversidad": diversidad,
        "conteos": conteos,
        "sin_dimension": sin_dimension,
        "estado": "calculado"
    }


if __name__ == "__main__":
    clasificaciones = {
        "A": {"anclajes": [{"uri": "urn:valor"}]},
        "B": {"anclajes": [{"uri": "urn:agenda"}]},
        "C": {"anclajes": [{"uri": "urn:racionalidad"}]},
        "D": {"anclajes": [{"uri": "urn:gobernanza"}]},
    }

    mapa = {
        "urn:valor": {"dimensiones": ["Valores"]},
        "urn:agenda": {"dimensiones": ["Agenda"]},
        "urn:racionalidad": {"dimensiones": ["Racionalidad"]},
        "urn:gobernanza": {"dimensiones": ["Gobernanza"]},
    }

    resultado = medir_diversidad_dimensional(
        clasificaciones, mapa
    )

    assert abs(resultado["diversidad"] - 1.0) < 1e-12
    assert resultado["sin_dimension"] == 0

    print("DIVERSIDAD DIMENSIONAL: OK")
    print("ENTROPÍA NORMALIZADA:", resultado["diversidad"])
