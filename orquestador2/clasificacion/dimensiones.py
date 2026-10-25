import json
from collections import deque
from pathlib import Path

SKOS = "http://www.w3.org/2004/02/skos/core#"

RAICES = {
    "Valores": "https://marianomosquera.github.io/ontology/Valores",
    "Agenda": "https://marianomosquera.github.io/etica/etica#Agenda",
    "Racionalidad": "https://marianomosquera.github.io/racionalidad/Racionalidad",
    "Gobernanza": "https://marianomosquera.github.io/etica/etica#Gobernanza",
}


def clasificar(raiz="."):
    raiz = Path(raiz)
    ont = json.loads(
        (raiz / "ontologia/jsonld/ontologia.jsonld").read_text(
            encoding="utf-8"
        )
    )
    config = json.loads(
        (raiz / "ontologia/config/correspondencias.json").read_text(
            encoding="utf-8"
        )
    )

    aliases = config.get("uri_aliases", {})
    if not isinstance(aliases, dict):
        raise ValueError("uri_aliases debe ser un diccionario")

    # Las correspondencias se usan solo para resolver identificadores.
    # No se incorporan como declaraciones de equivalencia RDF.
    def canonica(uri):
        visitadas = set()
        while uri in aliases:
            if uri in visitadas:
                raise ValueError(f"Ciclo de alias: {uri}")
            visitadas.add(uri)
            uri = aliases[uri]
        return uri

    conceptos = {
        canonica(e["@id"])
        for e in ont
        if SKOS + "Concept" in e.get("@type", [])
    }

    # Grafo dirigido de concepto general hacia concepto específico.
    hijos = {uri: set() for uri in conceptos}

    for entrada in ont:
        origen = canonica(entrada.get("@id", ""))
        if origen not in conceptos:
            continue

        for item in entrada.get(SKOS + "broader", []):
            padre = canonica(item["@id"])
            if padre in conceptos:
                hijos[padre].add(origen)

        for item in entrada.get(SKOS + "narrower", []):
            hijo = canonica(item["@id"])
            if hijo in conceptos:
                hijos[origen].add(hijo)

    def descendientes(inicio):
        distancias = {inicio: 0}
        cola = deque([inicio])

        while cola:
            actual = cola.popleft()
            for hijo in hijos.get(actual, set()):
                if hijo not in distancias:
                    distancias[hijo] = distancias[actual] + 1
                    cola.append(hijo)

        return distancias

    dimensiones = {
        nombre: descendientes(canonica(uri))
        for nombre, uri in RAICES.items()
    }

    resultado = {}

    for uri in sorted(conceptos):
        pertenencias = {
            nombre: distancias[uri]
            for nombre, distancias in dimensiones.items()
            if uri in distancias
        }

        resultado[uri] = {
            "dimensiones": sorted(pertenencias),
            "distancias": pertenencias,
            "estado": (
                "sin_clasificar" if not pertenencias
                else "unica" if len(pertenencias) == 1
                else "multiple"
            ),
        }

    return resultado


if __name__ == "__main__":
    resultado = clasificar()

    print("=== CLASIFICACIÓN DIMENSIONAL ===")
    print("Conceptos:", len(resultado))

    for dimension in RAICES:
        cantidad = sum(
            dimension in c["dimensiones"]
            for c in resultado.values()
        )
        print(f"{dimension}: {cantidad}")

    for estado in ("unica", "multiple", "sin_clasificar"):
        casos = [
            uri for uri, c in resultado.items()
            if c["estado"] == estado
        ]
        print(f"\n{estado}: {len(casos)}")

        if estado != "unica":
            for uri in casos[:20]:
                print(" ", uri, resultado[uri]["dimensiones"])
