from copy import deepcopy

from .validacion_skos import validar_anclajes_skos
from .validar_ruta_skos import validar_ruta_skos


def validar_fundamento_skos(propuesta, conceptos):
    """Verifica anclajes y rutas declaradas para una transformación."""

    if not isinstance(propuesta, dict):
        raise ValueError("La propuesta debe ser un diccionario")

    anclajes = validar_anclajes_skos(propuesta, conceptos)

    rutas = propuesta.get("rutas_skos", [])

    if not isinstance(rutas, list):
        raise ValueError("rutas_skos debe ser una lista")

    if not rutas:
        return {
            "estado": "sin_rutas",
            "anclajes": anclajes,
            "rutas_validadas": [],
        }

    if anclajes["estado"] != "validado":
        raise ValueError(
            "Las rutas SKOS requieren anclajes explícitos"
        )

    uris_ancladas = set(anclajes["anclajes_validados"])
    resultados = []

    for ruta in rutas:
        resultado = validar_ruta_skos(ruta, conceptos)

        if ruta["origen"] not in uris_ancladas:
            raise ValueError(
                "El origen de la ruta no está entre los anclajes"
            )

        if ruta["destino"] not in uris_ancladas:
            raise ValueError(
                "El destino de la ruta no está entre los anclajes"
            )

        resultados.append(resultado)

    return {
        "estado": "validado",
        "anclajes": deepcopy(anclajes),
        "rutas_validadas": deepcopy(resultados),
    }


if __name__ == "__main__":
    from orquestador2.lectores.ontologia import cargar_ontologia
    from .rutas_skos import buscar_rutas_skos

    conceptos = cargar_ontologia(".")

    igualdad = next(
        uri for uri, concepto in conceptos.items()
        if concepto.get("label_es") == "Igualdad"
    )

    justicia = next(
        uri for uri, concepto in conceptos.items()
        if concepto.get("label_es") == "Justicia"
    )

    rutas = buscar_rutas_skos(
        igualdad, conceptos, profundidad_maxima=2
    )

    ruta = next(
        r for r in rutas
        if r["destino"] == justicia and r["longitud"] == 1
    )

    propuesta = {
        "operacion": "crear_nodo",
        "id_nuevo": "S1",
        "claim": "Una nueva articulación entre igualdad y justicia",
        "justificacion": "Explorar una relación conceptual existente.",
        "anclajes_skos": [igualdad, justicia],
        "rutas_skos": [ruta],
    }

    resultado = validar_fundamento_skos(
        propuesta, conceptos
    )

    assert resultado["estado"] == "validado"
    assert len(resultado["rutas_validadas"]) == 1

    print("PROPUESTA CON FUNDAMENTO SKOS: OK")
    print("ANCLAJES Y RUTA COHERENTES: OK")

    invalida = deepcopy(propuesta)
    invalida["anclajes_skos"] = [igualdad]

    try:
        validar_fundamento_skos(invalida, conceptos)
    except ValueError:
        print("DESTINO SIN ANCLAJE: BLOQUEADO")
    else:
        raise AssertionError(
            "Se aceptó una ruta sin anclaje de destino"
        )

    sin_rutas = deepcopy(propuesta)
    sin_rutas.pop("rutas_skos")

    resultado = validar_fundamento_skos(
        sin_rutas, conceptos
    )

    assert resultado["estado"] == "sin_rutas"

    print("AUSENCIA DE RUTAS IDENTIFICADA: OK")
    print("VALIDACIÓN DEL FUNDAMENTO SKOS: OK")
