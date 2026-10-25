"""Integración de las mediciones de diversidad CCLTR."""

from orquestador2.medicion.indice_global import calcular_indice_global


def integrar_mediciones(
    diversidad_dimensional,
    riqueza_skos,
    diversidad_funcional,
    diversidad_semantica,
):
    componentes = {
        "dimensional": diversidad_dimensional.get("diversidad"),
        "riqueza_skos": riqueza_skos.get("riqueza_normalizada"),
        "funcional": diversidad_funcional.get("diversidad"),
        "semantica": diversidad_semantica.get("diversidad_normalizada"),
    }

    faltantes = [
        nombre
        for nombre, valor in componentes.items()
        if valor is None
    ]

    if faltantes:
        return {
            "estado": "incompleto",
            "componentes": componentes,
            "faltantes": faltantes,
            "indice_global": None,
        }

    return calcular_indice_global(componentes)


if __name__ == "__main__":
    resultado = integrar_mediciones(
        diversidad_dimensional={"diversidad": 1.0},
        riqueza_skos={"riqueza_normalizada": 0.5},
        diversidad_funcional={"diversidad": 1.0},
        diversidad_semantica={"diversidad_normalizada": 0.5},
    )

    assert abs(resultado["indice_global"] - 0.75) < 1e-12

    incompleto = integrar_mediciones(
        diversidad_dimensional={"diversidad": None},
        riqueza_skos={"riqueza_normalizada": 0.5},
        diversidad_funcional={"diversidad": 1.0},
        diversidad_semantica={"diversidad_normalizada": 0.5},
    )

    assert incompleto["estado"] == "incompleto"
    assert incompleto["indice_global"] is None

    print("INTEGRACIÓN DE DIVERSIDAD: OK")
    print("ÍNDICE DE PRUEBA:", resultado["indice_global"])
    print("CONTROL DE DATOS INCOMPLETOS: OK")
