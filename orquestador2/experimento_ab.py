from copy import deepcopy

from .clasificacion.rama_a import preparar_rama_a
from .transformacion.rama_b import preparar_rama_b
from .transformacion.registro import crear_registro_transformacion


def preparar_experimento_ab(debate_original, conceptos_skos):
    """
    Prepara las dos ramas independientes del experimento.

    Rama A: clasificación del debate original.
    Rama B: transformación del debate original mediante SKOS.

    No comunica clasificaciones ni mediciones de A hacia B.
    """
    original = deepcopy(debate_original)
    ontologia = deepcopy(conceptos_skos)

    solicitudes_a = preparar_rama_a(
        deepcopy(original),
        deepcopy(ontologia)
    )

    entrada_b = preparar_rama_b(
        deepcopy(original),
        deepcopy(ontologia)
    )

    registro_b = crear_registro_transformacion(entrada_b)

    return {
        "rama_a": {
            "solicitudes_clasificacion": solicitudes_a
        },
        "rama_b": {
            "entrada": entrada_b,
            "registro": registro_b
        },
        "estado": "preparado"
    }


if __name__ == "__main__":
    print("COORDINADOR EXPERIMENTAL A/B: DISPONIBLE")
    print("PREPARACIÓN INDEPENDIENTE: IMPLEMENTADA")
    print("SIN EJECUCIÓN DE IA: OK")
    print("SIN COMPARACIÓN PREMATURA: OK")


def validar_clasificacion_a(
    experimento, respuestas, debate_original, conceptos_skos
):
    """Valida A sin modificar ni consultar la rama B."""
    from .clasificacion.rama_a import validar_resultados_rama_a

    if experimento.get("estado") != "preparado":
        raise ValueError("Experimento no preparado")

    return validar_resultados_rama_a(
        deepcopy(debate_original),
        deepcopy(respuestas),
        deepcopy(conceptos_skos)
    )


def validar_clasificacion_b(resultado_transformacion, respuestas):
    """Valida B exclusivamente contra el registro efectivamente transformado."""
    from .transformacion.clasificacion_posterior import (
        validar_clasificacion_posterior,
    )

    if not isinstance(resultado_transformacion, dict):
        raise ValueError("Resultado de transformación B inválido")

    registro = resultado_transformacion.get("registro")

    if not isinstance(registro, dict):
        raise ValueError("Falta el registro transformado de B")

    return validar_clasificacion_posterior(
        registro, deepcopy(respuestas)
    )


def medir_rama(
    grafo,
    clasificaciones,
    mapa_dimensiones,
    configuracion,
    modelo,
    config_modelo
):
    """
    Mide una rama con los cuatro indicadores de diversidad.

    Exige correspondencia entre la configuración experimental
    y el modelo semántico efectivamente utilizado.
    """
    from .medicion.pipeline_semantico import medir_grafo_semanticamente
    from .medicion.medicion_conjunta import medir_diversidad_conjunta
    from .medicion.ajuste_tamano import medir_diversidad_ajustada

    configuracion.validar()

    if config_modelo["modelo"] != configuracion.modelo_embeddings:
        raise ValueError("Modelo de embeddings incompatible")

    if config_modelo["revision"] != configuracion.version_embeddings:
        raise ValueError("Revisión de embeddings incompatible")

    ids_grafo = [str(nodo["id"]) for nodo in grafo["nodes"]]

    if len(ids_grafo) != len(set(ids_grafo)):
        raise ValueError("Identificadores duplicados en el grafo")

    if set(ids_grafo) != set(clasificaciones):
        raise ValueError("Clasificaciones y grafo no coinciden")

    resultado_semantico = medir_grafo_semanticamente(
        deepcopy(grafo),
        modelo,
        deepcopy(config_modelo)
    )

    resultado = medir_diversidad_conjunta(
        deepcopy(clasificaciones),
        deepcopy(mapa_dimensiones),
        configuracion,
        resultado_semantico["normalizada"]
    )

    resultado["ajuste_tamano"] = medir_diversidad_ajustada(
        deepcopy(clasificaciones),
        deepcopy(mapa_dimensiones),
        resultado_semantico["embeddings"],
        configuracion
    )

    return resultado


def comparar_experimento_ab(resultado_a, resultado_b):
    """
    Compara dos mediciones completas e independientes.

    No ejecuta clasificaciones ni transformaciones.
    No permite comparar configuraciones diferentes.
    """
    from .medicion.comparacion import comparar_ramas

    for nombre, resultado in [
        ("A", resultado_a),
        ("B", resultado_b)
    ]:
        if not isinstance(resultado, dict):
            raise ValueError(f"Resultado de rama {nombre} inválido")

        if resultado.get("estado") != "calculado":
            raise ValueError(f"Medición de rama {nombre} incompleta")

        if "configuracion" not in resultado:
            raise ValueError(f"Falta configuración de rama {nombre}")

        if "mediciones" not in resultado:
            raise ValueError(f"Faltan mediciones de rama {nombre}")

        componentes = resultado.get("componentes", {})

        esperados = {
            "dimensional",
            "riqueza_skos",
            "funcional",
            "semantica"
        }

        if set(componentes) != esperados:
            raise ValueError(
                f"Componentes incompletos en rama {nombre}"
            )

    comparacion_original = comparar_ramas(
        resultado_a,
        resultado_b,
        resultado_a["configuracion"],
        resultado_b["configuracion"]
    )

    from .medicion.comparacion import comparar_ajustes_tamano

    ajuste_a = resultado_a.get("ajuste_tamano")
    ajuste_b = resultado_b.get("ajuste_tamano")

    if ajuste_a is None or ajuste_b is None:
        raise ValueError(
            "Ambas ramas deben incluir el ajuste por tamaño"
        )

    comparacion_ajustada = comparar_ajustes_tamano(
        ajuste_a, ajuste_b
    )

    return {
        **comparacion_original,
        "comparacion_ajustada": comparacion_ajustada,
    }


def ejecutar_transformacion_b(experimento, respuesta_ia):
    """
    Ejecuta las propuestas de transformación de B mediante
    el motor existente, sin consultar resultados de A.
    """
    from .transformacion.inicializar_grafo import (
        inicializar_grafo_transformado
    )
    from .transformacion.pipeline_rama_b import (
        procesar_respuesta_rama_b
    )
    from .transformacion.clasificacion_posterior import (
        preparar_clasificacion_posterior
    )
    from .transformacion.registro import verificar_integridad_original

    if experimento.get("estado") != "preparado":
        raise ValueError("Experimento no preparado")

    rama_b = experimento["rama_b"]
    entrada = deepcopy(rama_b["entrada"])
    registro = deepcopy(rama_b["registro"])

    verificar_integridad_original(registro, entrada)

    if registro["grafo_transformado"] is None:
        inicializar_grafo_transformado(registro, entrada)

    resultado = procesar_respuesta_rama_b(
        registro,
        entrada,
        deepcopy(respuesta_ia)
    )

    verificar_integridad_original(registro, entrada)

    solicitudes = preparar_clasificacion_posterior(registro)

    return {
        "registro": registro,
        "resultado_transformacion": resultado,
        "solicitudes_clasificacion": solicitudes,
    }
