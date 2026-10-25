from .fundamento_skos import validar_fundamento_skos


OPERACIONES_SEMANTICAS = {
    "crear_nodo",
    "reformular_nodo",
    "fusionar_nodos",
    "crear_vinculo",
}

OPERACIONES_DE_GESTION = {
    "retirar_vinculo",
    "jerarquizar_nodo",
    "retirar_nodo",
}


def evaluar_politica_skos(propuesta, conceptos):
    """Distingue fundamento ontológico y operaciones de gestión."""

    if not isinstance(propuesta, dict):
        raise ValueError("La propuesta debe ser un diccionario")

    operacion = propuesta.get("operacion")

    if operacion in OPERACIONES_SEMANTICAS:
        resultado = validar_fundamento_skos(
            propuesta, conceptos
        )

        if resultado["estado"] != "validado":
            raise ValueError(
                "La transformación semántica requiere "
                "anclajes y rutas SKOS explícitas"
            )

        return {
            "estado": "aprobada_estructuralmente",
            "categoria": "semantica",
            "fundamento": resultado,
        }

    if operacion in OPERACIONES_DE_GESTION:
        if "anclajes_skos" in propuesta or "rutas_skos" in propuesta:
            raise ValueError(
                "Las operaciones de gestión no deben declarar "
                "nuevos desplazamientos SKOS"
            )

        return {
            "estado": "aprobada_estructuralmente",
            "categoria": "gestion",
            "fundamento": None,
        }

    raise ValueError(f"Operación desconocida: {operacion}")


if __name__ == "__main__":
    from orquestador2.lectores.ontologia import cargar_ontologia
    from .rutas_skos import buscar_rutas_skos

    conceptos = cargar_ontologia(".")

    igualdad = next(
        uri for uri, c in conceptos.items()
        if c.get("label_es") == "Igualdad"
    )

    justicia = next(
        uri for uri, c in conceptos.items()
        if c.get("label_es") == "Justicia"
    )

    ruta = next(
        r for r in buscar_rutas_skos(igualdad, conceptos, 2)
        if r["destino"] == justicia and r["longitud"] == 1
    )

    semantica = {
        "operacion": "crear_nodo",
        "id_nuevo": "S1",
        "claim": "Nueva articulación entre igualdad y justicia",
        "justificacion": "Explorar una perspectiva conceptual.",
        "anclajes_skos": [igualdad, justicia],
        "rutas_skos": [ruta],
    }

    resultado = evaluar_politica_skos(semantica, conceptos)
    assert resultado["categoria"] == "semantica"
    print("TRANSFORMACIÓN CON FUNDAMENTO SKOS: OK")

    sin_rutas = dict(semantica)
    sin_rutas.pop("rutas_skos")

    try:
        evaluar_politica_skos(sin_rutas, conceptos)
    except ValueError:
        print("TRANSFORMACIÓN SIN RUTAS: BLOQUEADA")
    else:
        raise AssertionError("Se aceptó una transformación sin rutas")

    gestion = {
        "operacion": "retirar_nodo",
        "id_nodo": "S1",
        "justificacion": "Descartar una alternativa generada.",
    }

    resultado = evaluar_politica_skos(gestion, conceptos)
    assert resultado["categoria"] == "gestion"
    print("OPERACIÓN DE GESTIÓN: OK")

    try:
        evaluar_politica_skos(
            {"operacion": "operacion_inventada"}, conceptos
        )
    except ValueError:
        print("OPERACIÓN DESCONOCIDA: BLOQUEADA")
    else:
        raise AssertionError("Se aceptó una operación desconocida")

    print("POLÍTICA ONTOLÓGICA: OK")
