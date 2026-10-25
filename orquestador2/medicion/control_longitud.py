"""Control descriptivo de longitud de argumentos."""

from statistics import mean, median, pstdev


def medir_longitudes(debate):
    longitudes = {}

    for nodo in debate["nodes"]:
        texto = nodo.get("claim", "")

        if not isinstance(texto, str):
            raise ValueError(f"Texto inválido: {nodo['id']}")

        palabras = len(texto.split())
        caracteres = len(texto)

        longitudes[str(nodo["id"])] = {
            "palabras": palabras,
            "caracteres": caracteres
        }

    valores = [v["palabras"] for v in longitudes.values()]

    if not valores:
        return {
            "estado": "sin_datos",
            "argumentos": 0,
            "longitudes": longitudes
        }

    return {
        "estado": "calculado",
        "argumentos": len(valores),
        "media_palabras": mean(valores),
        "mediana_palabras": median(valores),
        "desviacion_palabras": pstdev(valores),
        "minimo_palabras": min(valores),
        "maximo_palabras": max(valores),
        "longitudes": longitudes
    }


if __name__ == "__main__":
    debate = {
        "nodes": [
            {"id": "A", "claim": "La seguridad es importante."},
            {"id": "B", "claim": "La privacidad también es importante."}
        ],
        "edges": [
            {
                "source": "B",
                "target": "A",
                "valence": "CON",
                "target_idx": 0
            }
        ]
    }

    resultado = medir_longitudes(debate)

    assert resultado["argumentos"] == 2
    assert resultado["media_palabras"] == 4.5
    assert resultado["mediana_palabras"] == 4.5
    assert debate["edges"][0]["valence"] == "CON"

    print("CONTROL DE LONGITUD: OK")
    print("MEDIA DE PALABRAS:", resultado["media_palabras"])
    print("ARGUMENTOS:", resultado["argumentos"])
