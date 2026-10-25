"""Comparación descriptiva de longitud entre ramas A y B."""

import math

from orquestador2.medicion.control_longitud import medir_longitudes


def comparar_longitudes(debate_a, debate_b):
    a = medir_longitudes(debate_a)
    b = medir_longitudes(debate_b)

    if a["estado"] != "calculado" or b["estado"] != "calculado":
        raise ValueError("Ambas ramas deben contener argumentos")

    media_a = a["media_palabras"]
    media_b = b["media_palabras"]

    return {
        "estado": "calculado",
        "argumentos_a": a["argumentos"],
        "argumentos_b": b["argumentos"],
        "media_a": media_a,
        "media_b": media_b,
        "diferencia_media": media_b - media_a,
        "variacion_porcentual": (
            100 * (media_b - media_a) / media_a
            if media_a > 0 else None
        ),
        "mediana_a": a["mediana_palabras"],
        "mediana_b": b["mediana_palabras"],
        "diferencia_mediana": (
            b["mediana_palabras"] - a["mediana_palabras"]
        ),
    }


if __name__ == "__main__":
    a = {
        "nodes": [
            {"id": "A", "claim": "Uno dos tres cuatro"},
            {"id": "B", "claim": "Cinco seis siete ocho"},
        ],
        "edges": [],
    }

    b = {
        "nodes": [
            {"id": "A", "claim": "Uno dos tres cuatro cinco seis"},
            {"id": "B", "claim": "Siete ocho nueve diez once doce"},
        ],
        "edges": [],
    }

    resultado = comparar_longitudes(a, b)

    assert resultado["argumentos_a"] == 2
    assert resultado["argumentos_b"] == 2
    assert math.isclose(resultado["variacion_porcentual"], 50.0)
    assert resultado["diferencia_mediana"] == 2

    print("ROBUSTEZ POR LONGITUD: OK")
    print("MEDIA A:", resultado["media_a"])
    print("MEDIA B:", resultado["media_b"])
    print("VARIACIÓN:", resultado["variacion_porcentual"], "%")
