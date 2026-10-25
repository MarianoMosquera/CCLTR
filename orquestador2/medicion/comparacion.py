"""Comparación controlada de diversidad entre ramas A y B."""

from orquestador2.medicion.indice_global import PESOS


def comparar_ramas(rama_a, rama_b, configuracion_a, configuracion_b):
    if configuracion_a != configuracion_b:
        raise ValueError(
            "Las ramas utilizan configuraciones experimentales diferentes"
        )

    if rama_a.get("estado") != "calculado":
        raise ValueError("La medición de la Rama A no está completa")

    if rama_b.get("estado") != "calculado":
        raise ValueError("La medición de la Rama B no está completa")

    resultados = {}

    variables = ["indice_global", *PESOS]

    for variable in variables:
        if variable == "indice_global":
            valor_a = rama_a["indice_global"]
            valor_b = rama_b["indice_global"]
        else:
            valor_a = rama_a["componentes"][variable]
            valor_b = rama_b["componentes"][variable]

        diferencia = valor_b - valor_a

        resultados[variable] = {
            "rama_a": valor_a,
            "rama_b": valor_b,
            "diferencia_absoluta": diferencia,
            "variacion_porcentual": (
                100 * diferencia / valor_a
                if valor_a != 0 else None
            ),
            "direccion": (
                "aumento" if diferencia > 1e-12
                else "reduccion" if diferencia < -1e-12
                else "sin_cambio"
            ),
        }

    return {
        "estado": "calculado",
        "comparacion": resultados,
        "configuracion_compartida": True,
    }


if __name__ == "__main__":
    from orquestador2.medicion.indice_global import calcular_indice_global

    a = calcular_indice_global({
        "dimensional": 0.6,
        "riqueza_skos": 0.4,
        "funcional": 0.5,
        "semantica": 0.3,
    })

    b = calcular_indice_global({
        "dimensional": 0.7,
        "riqueza_skos": 0.5,
        "funcional": 0.6,
        "semantica": 0.4,
    })

    configuracion = {
        "tamano_muestra": 100,
        "modelo_embeddings": "MODELO_DE_PRUEBA",
    }

    resultado = comparar_ramas(a, b, configuracion, configuracion)

    global_ = resultado["comparacion"]["indice_global"]

    assert abs(global_["rama_a"] - 0.46) < 1e-12
    assert abs(global_["rama_b"] - 0.56) < 1e-12
    assert abs(global_["diferencia_absoluta"] - 0.10) < 1e-12
    assert global_["direccion"] == "aumento"

    print("COMPARACIÓN A/B: OK")
    print("ÍNDICE A:", global_["rama_a"])
    print("ÍNDICE B:", global_["rama_b"])
    print("DIFERENCIA:", global_["diferencia_absoluta"])


def comparar_ajustes_tamano(ajuste_a, ajuste_b):
    """Compara índices ajustados y componentes de dos ramas."""
    for nombre, ajuste in (("A", ajuste_a), ("B", ajuste_b)):
        if not isinstance(ajuste, dict):
            raise ValueError(f"Ajuste de rama {nombre} inválido")
        if ajuste.get("estado") != "calculado":
            raise ValueError(f"Ajuste de rama {nombre} incompleto")

        requeridos = {
            "indice_ajustado",
            "componentes_ajustados",
            "desviacion_estandar",
            "tamano_muestra",
            "muestras_evaluadas",
            "metodo",
        }
        if not requeridos.issubset(ajuste):
            raise ValueError(f"Faltan campos en ajuste de rama {nombre}")

    if ajuste_a["tamano_muestra"] != ajuste_b["tamano_muestra"]:
        raise ValueError("Las ramas tienen tamaños de muestra diferentes")

    variables = ["indice_ajustado", *PESOS]
    resultados = {}

    for variable in variables:
        if variable == "indice_ajustado":
            valor_a = ajuste_a[variable]
            valor_b = ajuste_b[variable]
        else:
            valor_a = ajuste_a["componentes_ajustados"].get(variable)
            valor_b = ajuste_b["componentes_ajustados"].get(variable)

        if valor_a is None or valor_b is None:
            raise ValueError(f"Componente ajustado ausente: {variable}")

        diferencia = valor_b - valor_a
        resultados[variable] = {
            "rama_a": valor_a,
            "rama_b": valor_b,
            "diferencia_absoluta": diferencia,
            "variacion_porcentual": (
                100 * diferencia / valor_a if valor_a != 0 else None
            ),
            "direccion": (
                "aumento" if diferencia > 1e-12
                else "reduccion" if diferencia < -1e-12
                else "sin_cambio"
            ),
        }

    return {
        "estado": "calculado",
        "comparacion": resultados,
        "tamano_muestra": ajuste_a["tamano_muestra"],
        "rama_a": {
            "metodo": ajuste_a["metodo"],
            "muestras_evaluadas": ajuste_a["muestras_evaluadas"],
            "desviacion_estandar": ajuste_a["desviacion_estandar"],
        },
        "rama_b": {
            "metodo": ajuste_b["metodo"],
            "muestras_evaluadas": ajuste_b["muestras_evaluadas"],
            "desviacion_estandar": ajuste_b["desviacion_estandar"],
        },
    }
