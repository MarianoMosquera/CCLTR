def identificar_desplazamientos(uri_origen, conceptos):
    """Recupera desplazamientos explícitos desde un concepto SKOS."""

    if uri_origen not in conceptos:
        raise ValueError(f"Concepto inexistente: {uri_origen}")

    relaciones = conceptos[uri_origen].get("relaciones", {})

    correspondencias = {
        "generalizacion": "broader",
        "especializacion": "narrower",
        "asociacion": "related",
    }

    resultado = {}

    for movimiento, relacion in correspondencias.items():
        destinos = relaciones.get(relacion, [])

        if not isinstance(destinos, list):
            raise ValueError(f"Relación SKOS inválida: {relacion}")

        resultado[movimiento] = []

        for destino in destinos:
            if destino not in conceptos:
                raise ValueError(
                    f"Destino SKOS inexistente: {destino}"
                )

            concepto = conceptos[destino]

            resultado[movimiento].append({
                "uri": destino,
                "label_es": concepto.get("label_es"),
                "relacion_skos": relacion,
            })

    return resultado


if __name__ == "__main__":
    from orquestador2.lectores.ontologia import cargar_ontologia

    conceptos = cargar_ontologia(".")

    igualdad = next(
        uri for uri, concepto in conceptos.items()
        if concepto.get("label_es") == "Igualdad"
    )

    movimientos = identificar_desplazamientos(
        igualdad, conceptos
    )

    print("CONCEPTO DE PARTIDA: Igualdad")

    for tipo, destinos in movimientos.items():
        print(f"\n{tipo.upper()}: {len(destinos)}")

        for destino in destinos:
            print(" -", destino["label_es"])

    assert any(
        destino["label_es"] == "Justicia"
        for destino in movimientos["asociacion"]
    )

    assert any(
        destino["label_es"] == "Valores"
        for destino in movimientos["generalizacion"]
    )

    print("\nGENERALIZACIÓN IDENTIFICADA: OK")
    print("ASOCIACIÓN IDENTIFICADA: OK")
    print("DESPLAZAMIENTOS SKOS RECUPERADOS: OK")
