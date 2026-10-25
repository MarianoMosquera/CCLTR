from .diagnostico_longitud import diagnosticar_longitudes


def comparar_longitud_ramas(grafo_a, grafo_b, modelo):
    a = diagnosticar_longitudes(grafo_a, modelo)
    b = diagnosticar_longitudes(grafo_b, modelo)

    if not a["argumentos"] or not b["argumentos"]:
        raise ValueError("Ambas ramas deben contener argumentos")

    media_a = a["longitud_media"]
    media_b = b["longitud_media"]

    variacion = 100 * (media_b - media_a) / media_a

    return {
        "rama_a": {
            "argumentos": a["argumentos"],
            "media_tokens": media_a,
            "maximo_tokens": a["longitud_maxima"],
            "excedidos": a["argumentos_excedidos"],
        },
        "rama_b": {
            "argumentos": b["argumentos"],
            "media_tokens": media_b,
            "maximo_tokens": b["longitud_maxima"],
            "excedidos": b["argumentos_excedidos"],
        },
        "variacion_media_porcentual": variacion,
        "comparacion_sin_truncamientos": (
            a["argumentos_excedidos"] == 0
            and b["argumentos_excedidos"] == 0
        ),
    }


if __name__ == "__main__":
    from .generador_embeddings import cargar_modelo

    modelo, _ = cargar_modelo()

    grafo_a = {
        "nodes": [
            {"id": "A1", "claim": "La inteligencia artificial mejora la productividad."},
            {"id": "A2", "claim": "La inteligencia artificial amenaza algunos empleos."},
        ],
        "edges": [],
    }

    grafo_b = {
        "nodes": [
            {"id": "B1", "claim": "La inteligencia artificial mejora la productividad cuando existe supervisión humana."},
            {"id": "B2", "claim": "La inteligencia artificial transforma el empleo y exige políticas de formación profesional."},
        ],
        "edges": [],
    }

    resultado = comparar_longitud_ramas(grafo_a, grafo_b, modelo)

    assert resultado["rama_a"]["argumentos"] == 2
    assert resultado["rama_b"]["argumentos"] == 2
    assert resultado["comparacion_sin_truncamientos"]
    assert resultado["variacion_media_porcentual"] > 0

    print("COMPARACIÓN DE LONGITUD A/B: OK")
    print("MEDIA A:", resultado["rama_a"]["media_tokens"])
    print("MEDIA B:", resultado["rama_b"]["media_tokens"])
    print("VARIACIÓN %:", round(resultado["variacion_media_porcentual"], 2))
    print("SIN TRUNCAMIENTOS:", resultado["comparacion_sin_truncamientos"])
