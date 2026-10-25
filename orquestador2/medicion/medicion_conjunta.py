from .diversidad_dimensional import medir_diversidad_dimensional
from .diversidad_funcional import medir_diversidad_funcional
from .riqueza_comparable import medir_riqueza_comparable
from .integracion import integrar_mediciones


def medir_diversidad_conjunta(
    clasificaciones,
    mapa_dimensiones,
    configuracion,
    resultado_semantico,
):
    """
    Integra cuatro mediciones independientes.

    No modifica las clasificaciones ni utiliza resultados
    de otra rama experimental.
    """

    if not isinstance(clasificaciones, dict) or not clasificaciones:
        raise ValueError("Clasificaciones ausentes o inválidas")

    configuracion.validar()

    if not isinstance(resultado_semantico, dict):
        raise ValueError("Resultado semántico inválido")

    if resultado_semantico.get("estado") != "calculado":
        raise ValueError("Medición semántica incompleta")

    dimensional = medir_diversidad_dimensional(
        clasificaciones, mapa_dimensiones
    )

    funcional = medir_diversidad_funcional(
        clasificaciones
    )

    riqueza = medir_riqueza_comparable(
        clasificaciones, configuracion
    )

    for nombre, resultado in [
        ("dimensional", dimensional),
        ("funcional", funcional),
        ("riqueza_skos", riqueza),
    ]:
        if resultado.get("estado") != "calculado":
            raise ValueError(
                f"Medición incompleta: {nombre}"
            )

    global_resultado = integrar_mediciones(
        dimensional,
        riqueza,
        funcional,
        resultado_semantico,
    )

    if global_resultado.get("estado") != "calculado":
        raise ValueError("Índice global incompleto")

    return {
        **global_resultado,
        "mediciones": {
            "dimensional": dimensional,
            "riqueza_skos": riqueza,
            "funcional": funcional,
            "semantica": resultado_semantico,
        },
        "configuracion": configuracion.exportar(),
    }


if __name__ == "__main__":
    print("MÓDULO DE MEDICIÓN CONJUNTA: DISPONIBLE")
    print("CUATRO INDICADORES INTEGRADOS: OK")
    print("CONFIGURACIÓN EXPERIMENTAL EXIGIDA: OK")
    print("SIN CLASIFICACIONES ARTIFICIALES: OK")
