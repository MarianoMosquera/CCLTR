"""Diversidad a tamaño constante mediante muestreo conjunto de argumentos."""

import random
from itertools import combinations
from math import comb
from statistics import mean, pstdev

from .diversidad_dimensional import medir_diversidad_dimensional
from .diversidad_funcional import medir_diversidad_funcional
from .semantica_normalizada import medir_semantica_normalizada
from .integracion import calcular_indice_global


def medir_diversidad_ajustada(
    clasificaciones,
    mapa_dimensiones,
    embeddings,
    configuracion,
):
    """Calcula los cuatro indicadores sobre las mismas muestras de nodos."""
    configuracion.validar()

    if not isinstance(clasificaciones, dict) or not clasificaciones:
        raise ValueError("Clasificaciones inválidas")

    ids = sorted(clasificaciones)

    if set(ids) != set(embeddings):
        raise ValueError("Embeddings y clasificaciones no coinciden")

    n = configuracion.tamano_muestra

    if n < 2 or n > len(ids):
        raise ValueError("Tamaño de muestra inválido para medición conjunta")

    rng = random.Random(configuracion.semilla)
    cantidad_combinaciones = comb(len(ids), n)

    if cantidad_combinaciones <= configuracion.repeticiones:
        muestras = list(combinations(ids, n))
        metodo = "exhaustivo"
    else:
        # Muestreo sin reemplazo entre combinaciones completas.
        # Cada combinación de nodos se evalúa como máximo una vez.
        muestras = []
        vistas = set()
        max_intentos = max(
            configuracion.repeticiones * 20,
            configuracion.repeticiones + 100,
        )
        intentos = 0

        while (
            len(muestras) < configuracion.repeticiones
            and len(muestras) < cantidad_combinaciones
            and intentos < max_intentos
        ):
            muestra = tuple(sorted(rng.sample(ids, n)))
            intentos += 1

            if muestra not in vistas:
                vistas.add(muestra)
                muestras.append(muestra)

        metodo = "monte_carlo_sin_reemplazo"

    resultados = []
    componentes_acumulados = {
        "dimensional": [],
        "riqueza_skos": [],
        "funcional": [],
        "semantica": [],
    }

    for muestra in muestras:
        clasificacion_muestra = {
            identificador: clasificaciones[identificador]
            for identificador in muestra
        }

        embeddings_muestra = {
            identificador: embeddings[identificador]
            for identificador in muestra
        }

        dimensional = medir_diversidad_dimensional(
            clasificacion_muestra, mapa_dimensiones
        )

        funcional = medir_diversidad_funcional(
            clasificacion_muestra
        )

        semantica = medir_semantica_normalizada(
            embeddings_muestra
        )

        conceptos = {
            anclaje["uri"]
            for registro in clasificacion_muestra.values()
            for anclaje in registro["anclajes"]
        }

        riqueza = len(conceptos) / configuracion.referencia_riqueza

        componentes = {
            "dimensional": dimensional["diversidad"],
            "riqueza_skos": riqueza,
            "funcional": funcional["diversidad"],
            "semantica": semantica["diversidad_normalizada"],
        }

        if any(valor is None for valor in componentes.values()):
            raise ValueError("Muestra con medición incompleta")

        resultado = calcular_indice_global(componentes)
        resultados.append(resultado["indice_global"])

        for nombre, valor in componentes.items():
            componentes_acumulados[nombre].append(valor)

    return {
        "estado": "calculado",
        "indice_ajustado": mean(resultados),
        "desviacion_estandar": pstdev(resultados),
        "componentes_ajustados": {
            nombre: mean(valores)
            for nombre, valores in componentes_acumulados.items()
        },
        "variabilidad_componentes": {
            nombre: pstdev(valores)
            for nombre, valores in componentes_acumulados.items()
        },
        "tamano_muestra": n,
        "muestras_evaluadas": len(muestras),
        "metodo": metodo,
        "semilla": configuracion.semilla,
        "referencia_riqueza": configuracion.referencia_riqueza,
    }
