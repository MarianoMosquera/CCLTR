"""Índice compuesto de diversidad CCLTR."""

import math


PESOS = {
    "dimensional": 0.30,
    "riqueza_skos": 0.30,
    "funcional": 0.20,
    "semantica": 0.20,
}


def calcular_indice_global(componentes):
    if set(componentes) != set(PESOS):
        raise ValueError("Componentes incompletos o desconocidos")

    for nombre, valor in componentes.items():
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ValueError(f"Valor inválido: {nombre}")

        if not math.isfinite(valor) or not 0 <= valor <= 1:
            raise ValueError(f"Fuera del intervalo [0,1]: {nombre}")

    indice = sum(
        PESOS[nombre] * componentes[nombre]
        for nombre in PESOS
    )

    return {
        "indice_global": indice,
        "componentes": dict(componentes),
        "pesos": dict(PESOS),
        "estado": "calculado"
    }


if __name__ == "__main__":
    componentes = {
        "dimensional": 1.0,
        "riqueza_skos": 0.5,
        "funcional": 1.0,
        "semantica": 0.5,
    }

    resultado = calcular_indice_global(componentes)

    assert abs(resultado["indice_global"] - 0.75) < 1e-12

    print("ÍNDICE GLOBAL CCLTR: OK")
    print("RESULTADO DE PRUEBA:", resultado["indice_global"])
