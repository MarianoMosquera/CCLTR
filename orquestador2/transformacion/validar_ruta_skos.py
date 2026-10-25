from copy import deepcopy

RELACIONES = {
    "generalizacion": "broader",
    "especializacion": "narrower",
    "asociacion": "related",
}


def validar_ruta_skos(ruta, conceptos):
    """Comprueba que cada paso corresponde a una relación SKOS real."""

    if not isinstance(ruta, dict):
        raise ValueError("La ruta debe ser un diccionario")

    origen = ruta.get("origen")
    destino = ruta.get("destino")
    pasos = ruta.get("pasos")

    if origen not in conceptos:
        raise ValueError("Origen inexistente en SKOS")

    if not isinstance(pasos, list) or not pasos:
        raise ValueError("La ruta debe contener pasos")

    actual = origen
    visitados = {origen}

    for indice, paso in enumerate(pasos, start=1):
        if not isinstance(paso, dict):
            raise ValueError("Paso inválido")

        siguiente = paso.get("destino")
        tipo = paso.get("tipo")

        if paso.get("origen") != actual:
            raise ValueError(f"Ruta discontinua en paso {indice}")

        if tipo not in RELACIONES:
            raise ValueError(f"Movimiento desconocido: {tipo}")

        relacion = RELACIONES[tipo]

        if paso.get("relacion_skos") != relacion:
            raise ValueError("Tipo y relación SKOS no coinciden")

        if siguiente not in conceptos:
            raise ValueError("Destino inexistente en SKOS")

        if siguiente in visitados:
            raise ValueError("La ruta contiene un ciclo")

        relaciones = conceptos[actual].get("relaciones", {})
        destinos_validos = relaciones.get(relacion, [])

        if siguiente not in destinos_validos:
            raise ValueError(
                f"Relación SKOS inexistente en paso {indice}"
            )

        actual = siguiente
        visitados.add(actual)

    if actual != destino:
        raise ValueError("El destino final no coincide")

    if ruta.get("longitud") != len(pasos):
        raise ValueError("Longitud de ruta inconsistente")

    return {
        "estado": "validada",
        "origen": origen,
        "destino": destino,
        "pasos_verificados": len(pasos),
    }


if __name__ == "__main__":
    from orquestador2.lectores.ontologia import cargar_ontologia
    from .rutas_skos import buscar_rutas_skos

    conceptos = cargar_ontologia(".")

    igualdad = next(
        uri for uri, concepto in conceptos.items()
        if concepto.get("label_es") == "Igualdad"
    )

    rutas = buscar_rutas_skos(
        igualdad, conceptos, profundidad_maxima=2
    )

    for ruta in rutas:
        resultado = validar_ruta_skos(ruta, conceptos)
        assert resultado["estado"] == "validada"

    print("RUTAS REALES VALIDADAS:", len(rutas))

    falsa = deepcopy(rutas[0])
    falsa["pasos"][0]["relacion_skos"] = "related"

    try:
        validar_ruta_skos(falsa, conceptos)
    except ValueError:
        print("RELACIÓN FALSA RECHAZADA: OK")
    else:
        raise AssertionError("Se aceptó una relación falsa")

    discontinua = deepcopy(rutas[-1])
    discontinua["pasos"][1]["origen"] = igualdad

    try:
        validar_ruta_skos(discontinua, conceptos)
    except ValueError:
        print("RUTA DISCONTINUA RECHAZADA: OK")
    else:
        raise AssertionError("Se aceptó una ruta discontinua")

    print("TRAZABILIDAD ONTOLÓGICA: OK")
    print("VALIDADOR DE RUTAS SKOS: OK")
