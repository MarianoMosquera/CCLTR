def diagnosticar_longitudes(grafo, modelo):
    limite = modelo.max_seq_length
    registros = []

    for nodo in grafo["nodes"]:
        texto = nodo["claim"]

        tokens = modelo.tokenizer(
            texto,
            add_special_tokens=True,
            truncation=False,
            verbose=False,
        )["input_ids"]

        registros.append({
            "id": nodo["id"],
            "tokens": len(tokens),
            "excede_limite": len(tokens) > limite,
        })

    longitudes = [r["tokens"] for r in registros]

    return {
        "limite": limite,
        "argumentos": len(registros),
        "longitud_media": (
            sum(longitudes) / len(longitudes)
            if longitudes else 0
        ),
        "longitud_maxima": max(longitudes, default=0),
        "argumentos_excedidos": sum(
            r["excede_limite"] for r in registros
        ),
        "registros": registros,
    }


if __name__ == "__main__":
    from .generador_embeddings import cargar_modelo

    modelo, _ = cargar_modelo()

    grafo = {
        "nodes": [
            {"id": "A", "claim": "La inteligencia artificial mejora la productividad."},
            {"id": "B", "claim": "La inteligencia artificial requiere supervisión humana. " * 50},
        ],
        "edges": [],
    }

    resultado = diagnosticar_longitudes(grafo, modelo)

    assert resultado["argumentos"] == 2
    assert resultado["argumentos_excedidos"] == 1
    assert resultado["registros"][1]["id"] == "B"

    print("DIAGNÓSTICO DE LONGITUD: OK")
    print("LÍMITE:", resultado["limite"])
    print("LONGITUD MEDIA:", resultado["longitud_media"])
    print("LONGITUD MÁXIMA:", resultado["longitud_maxima"])
    print("ARGUMENTOS EXCEDIDOS:", resultado["argumentos_excedidos"])
