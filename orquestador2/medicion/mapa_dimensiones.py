"""Deriva dimensiones de medición desde la jerarquía SKOS existente."""

import json
from pathlib import Path

from orquestador2.lectores.ontologia import cargar_ontologia


RAICES = {
    "Valores": "https://marianomosquera.github.io/ontology/Valores",
    "Agenda": "https://marianomosquera.github.io/etica/etica#Agenda",
    "Racionalidad": "https://marianomosquera.github.io/racionalidad/Racionalidad",
    "Gobernanza": "https://marianomosquera.github.io/etica/etica#Gobernanza",
}


def construir_mapa_dimensiones(raiz="."):
    base = Path(raiz)
    conceptos = cargar_ontologia(raiz)

    archivo_alias = base / "ontologia/config/correspondencias.json"
    alias = json.loads(archivo_alias.read_text(encoding="utf-8"))

    if not isinstance(alias, dict):
        raise ValueError("Las correspondencias SKOS deben ser un diccionario")

    def canonica(uri):
        vistos = set()
        while uri in alias:
            if uri in vistos:
                raise ValueError(f"Ciclo en correspondencias SKOS: {uri}")
            vistos.add(uri)
            uri = alias[uri]
        return uri

    hijos = {}

    for uri, concepto in conceptos.items():
        origen = canonica(uri)
        hijos.setdefault(origen, set())

        relaciones = concepto.get("relaciones", {})

        for destino in relaciones.get("narrower", []):
            hijos[origen].add(canonica(destino))

        for superior in relaciones.get("broader", []):
            hijos.setdefault(canonica(superior), set()).add(origen)

    mapa = {
        uri: {"dimensiones": []}
        for uri in conceptos
    }

    raices_agenda = [
        "https://marianomosquera.github.io/institucional/Institucional",
        "https://marianomosquera.github.io/politica/Politica",
        "https://marianomosquera.github.io/social/Social",
        "https://marianomosquera.github.io/ambiental/Ambiental",
        "https://marianomosquera.github.io/economica/Economica",
        "https://marianomosquera.github.io/tecnologica/Tecnologica",
    ]

    for dimension, raiz_dimension in RAICES.items():
        raiz_canonica = canonica(raiz_dimension)

        if dimension == "Agenda":
            hijos.setdefault(raiz_canonica, set()).update(
                canonica(uri) for uri in raices_agenda
            )

        if raiz_canonica not in hijos:
            raise ValueError(
                f"No se encontró la raíz SKOS de {dimension}: "
                f"{raiz_canonica}"
            )

        pendientes = [raiz_canonica]
        visitados = set()

        while pendientes:
            actual = pendientes.pop()

            if actual in visitados:
                continue

            visitados.add(actual)

            for uri in mapa:
                if canonica(uri) == actual:
                    mapa[uri]["dimensiones"].append(dimension)

            pendientes.extend(hijos.get(actual, ()))

    for registro in mapa.values():
        registro["dimensiones"] = sorted(set(registro["dimensiones"]))

    return mapa


if __name__ == "__main__":
    mapa = construir_mapa_dimensiones()

    cubiertos = sum(
        bool(registro["dimensiones"])
        for registro in mapa.values()
    )

    print("CONCEPTOS SKOS:", len(mapa))
    print("CONCEPTOS CON DIMENSIÓN:", cubiertos)
    print("CONCEPTOS SIN DIMENSIÓN:", len(mapa) - cubiertos)

    for dimension in RAICES:
        cantidad = sum(
            dimension in registro["dimensiones"]
            for registro in mapa.values()
        )
        print(f"{dimension}: {cantidad}")

    print("MAPA DIMENSIONAL: CONSTRUIDO")
