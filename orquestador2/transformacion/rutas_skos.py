from collections import deque

from .desplazamiento_skos import identificar_desplazamientos


def buscar_rutas_skos(origen, conceptos, profundidad_maxima=2):
    """Explora rutas SKOS sin repetir conceptos dentro de cada recorrido."""

    if not isinstance(profundidad_maxima, int) or isinstance(
        profundidad_maxima, bool
    ) or profundidad_maxima < 1:
        raise ValueError("La profundidad debe ser un entero positivo")

    if origen not in conceptos:
        raise ValueError("Concepto de origen inexistente")

    cola = deque([(origen, [])])
    rutas = []

    while cola:
        actual, pasos = cola.popleft()

        if len(pasos) >= profundidad_maxima:
            continue

        movimientos = identificar_desplazamientos(actual, conceptos)

        visitados = {origen}
        visitados.update(paso["destino"] for paso in pasos)

        for tipo, destinos in movimientos.items():
            for destino in destinos:
                uri = destino["uri"]

                if uri in visitados:
                    continue

                paso = {
                    "origen": actual,
                    "destino": uri,
                    "tipo": tipo,
                    "relacion_skos": destino["relacion_skos"],
                }

                nueva_ruta = pasos + [paso]

                rutas.append({
                    "origen": origen,
                    "destino": uri,
                    "pasos": nueva_ruta,
                    "longitud": len(nueva_ruta),
                })

                cola.append((uri, nueva_ruta))

    return rutas


if __name__ == "__main__":
    from orquestador2.lectores.ontologia import cargar_ontologia

    conceptos = cargar_ontologia(".")

    igualdad = next(
        uri for uri, concepto in conceptos.items()
        if concepto.get("label_es") == "Igualdad"
    )

    rutas = buscar_rutas_skos(
        igualdad, conceptos, profundidad_maxima=2
    )

    assert rutas
    assert all(1 <= r["longitud"] <= 2 for r in rutas)

    print("CONCEPTO DE PARTIDA: Igualdad")
    print("RUTAS ENCONTRADAS:", len(rutas))

    for ruta in rutas[:10]:
        etiquetas = ["Igualdad"]

        for paso in ruta["pasos"]:
            etiquetas.append(
                conceptos[paso["destino"]]["label_es"]
            )

        print(" -> ".join(etiquetas))

    assert any(
        conceptos[r["destino"]]["label_es"] == "Justicia"
        and r["longitud"] == 1
        for r in rutas
    )

    assert any(r["longitud"] == 2 for r in rutas)

    print("RUTAS DIRECTAS: OK")
    print("RUTAS DE DOS PASOS: OK")
    print("TRAZABILIDAD DE RELACIONES SKOS: OK")
