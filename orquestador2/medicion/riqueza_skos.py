"""Riqueza conceptual y cobertura de la ontología SKOS."""

def medir_riqueza_skos(clasificaciones, conceptos):
    if not conceptos:
        raise ValueError("La ontología está vacía")

    utilizados = set()
    frecuencias = {}

    for registro in clasificaciones.values():
        for anclaje in registro["anclajes"]:
            uri = anclaje["uri"]

            if uri not in conceptos:
                raise ValueError(f"Concepto desconocido: {uri}")

            utilizados.add(uri)
            frecuencias[uri] = frecuencias.get(uri, 0) + 1

    return {
        "riqueza_observada": len(utilizados),
        "conceptos_disponibles": len(conceptos),
        "cobertura": len(utilizados) / len(conceptos),
        "frecuencias": dict(sorted(frecuencias.items()))
    }


if __name__ == "__main__":
    conceptos = {
        "urn:A": {},
        "urn:B": {},
        "urn:C": {},
        "urn:D": {}
    }

    clasificaciones = {
        "1": {"anclajes": [{"uri": "urn:A"}, {"uri": "urn:B"}]},
        "2": {"anclajes": [{"uri": "urn:A"}]},
        "3": {"anclajes": [{"uri": "urn:C"}]}
    }

    resultado = medir_riqueza_skos(clasificaciones, conceptos)

    assert resultado["riqueza_observada"] == 3
    assert resultado["conceptos_disponibles"] == 4
    assert resultado["cobertura"] == 0.75
    assert resultado["frecuencias"]["urn:A"] == 2

    print("RIQUEZA SKOS: OK")
    print("CONCEPTOS DIFERENTES:", resultado["riqueza_observada"])
    print("COBERTURA:", resultado["cobertura"])
