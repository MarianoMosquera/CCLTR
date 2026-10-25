"""Coordinación integral del experimento A/B."""

from copy import deepcopy

from orquestador2.experimento_ab import (
    preparar_experimento_ab,
    validar_clasificacion_a,
    ejecutar_transformacion_b,
    validar_clasificacion_b,
    medir_rama,
    comparar_experimento_ab,
)
from orquestador2.integracion.exportador import exportar_experimento


def ejecutar_experimento_ab(
    identificador,
    debate_original,
    conceptos_skos,
    respuestas_a,
    respuesta_transformacion_b,
    respuestas_b,
    mapa_dimensiones,
    configuracion,
    modelo,
    config_modelo,
    destino="orquestador2/resultados",
):
    """Ejecuta ambas ramas con respuestas externas ya obtenidas."""

    experimento = preparar_experimento_ab(
        deepcopy(debate_original),
        deepcopy(conceptos_skos),
    )

    clasificaciones_a = validar_clasificacion_a(
        experimento,
        deepcopy(respuestas_a),
        deepcopy(debate_original),
        deepcopy(conceptos_skos),
    )

    transformacion_b = ejecutar_transformacion_b(
        experimento,
        deepcopy(respuesta_transformacion_b),
    )

    clasificaciones_b = validar_clasificacion_b(
        transformacion_b,
        deepcopy(respuestas_b),
    )

    grafo_b = transformacion_b["registro"]["grafo_transformado"]

    medicion_a = medir_rama(
        deepcopy(debate_original),
        clasificaciones_a,
        mapa_dimensiones,
        configuracion,
        modelo,
        config_modelo,
    )

    medicion_b = medir_rama(
        deepcopy(grafo_b),
        clasificaciones_b,
        mapa_dimensiones,
        configuracion,
        modelo,
        config_modelo,
    )

    comparacion = comparar_experimento_ab(
        medicion_a,
        medicion_b,
    )

    rama_a = {
        "grafo": deepcopy(debate_original),
        "clasificaciones": clasificaciones_a,
        "medicion": medicion_a,
    }

    rama_b = {
        "grafo": grafo_b,
        "clasificaciones": clasificaciones_b,
        "registro_transformacion": transformacion_b["registro"],
        "medicion": medicion_b,
    }

    archivos = exportar_experimento(
        identificador,
        deepcopy(debate_original),
        rama_a,
        rama_b,
        comparacion,
        destino,
    )

    return {
        "estado": "calculado",
        "rama_a": rama_a,
        "rama_b": rama_b,
        "comparacion": comparacion,
        "archivos": archivos,
    }
