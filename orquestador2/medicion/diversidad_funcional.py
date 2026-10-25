"""Diversidad de funciones argumentativas."""

import math

FUNCIONES = ("pragmatica", "condicional", "prospectiva")


def medir_diversidad_funcional(clasificaciones):
    conteos = {f: 0.0 for f in FUNCIONES}
    sin_funcion = 0

    for registro in clasificaciones.values():
        funciones = set(registro["funciones"])

        if not funciones.issubset(FUNCIONES):
            raise ValueError(f"Funciones desconocidas: {funciones - set(FUNCIONES)}")

        if not funciones:
            sin_funcion += 1
            continue

        peso = 1.0 / len(funciones)

        for funcion in funciones:
            conteos[funcion] += peso

    total = sum(conteos.values())

    if total == 0:
        return {
            "diversidad": None,
            "conteos": conteos,
            "sin_funcion": sin_funcion,
            "estado": "sin_datos"
        }

    probabilidades = [valor / total for valor in conteos.values()]

    entropia = -sum(
        p * math.log(p) for p in probabilidades if p > 0
    )

    return {
        "diversidad": entropia / math.log(len(FUNCIONES)),
        "conteos": conteos,
        "sin_funcion": sin_funcion,
        "estado": "calculado"
    }


if __name__ == "__main__":
    clasificaciones = {
        "A": {"funciones": ["pragmatica"]},
        "B": {"funciones": ["condicional"]},
        "C": {"funciones": ["prospectiva"]},
    }

    resultado = medir_diversidad_funcional(clasificaciones)

    assert abs(resultado["diversidad"] - 1.0) < 1e-12
    assert resultado["sin_funcion"] == 0

    print("DIVERSIDAD FUNCIONAL: OK")
    print("ENTROPÍA NORMALIZADA:", resultado["diversidad"])
