import json
from pathlib import Path

import networkx as nx
from rdflib import Graph, RDF, SKOS, URIRef

base = Path("ontologia")
g = Graph()
g.parse(base / "jsonld/ontologia.jsonld", format="json-ld")

with open(base / "config/correspondencias.json", encoding="utf-8") as f:
    aliases = json.load(f)["uri_aliases"]

def normalizar(uri):
    return aliases.get(str(uri), str(uri))

def etiqueta(uri):
    valores = list(g.objects(URIRef(uri), SKOS.prefLabel))
    return str(valores[0]) if valores else uri.rsplit("/", 1)[-1].split("#")[-1]

G = nx.MultiDiGraph()

conceptos = set(g.subjects(RDF.type, SKOS.Concept))
conceptos_normalizados = {normalizar(uri) for uri in conceptos}

for uri in sorted(conceptos_normalizados):
    G.add_node(uri, label=etiqueta(uri), tipo="concepto")

relaciones = {
    SKOS.broader: "broader",
    SKOS.related: "related",
    SKOS.exactMatch: "exactMatch",
    SKOS.closeMatch: "closeMatch",
}

for predicado, tipo in relaciones.items():
    for sujeto, objeto in g.subject_objects(predicado):
        origen = normalizar(sujeto)
        destino = normalizar(objeto)

        if origen in conceptos_normalizados and destino in conceptos_normalizados:
            G.add_edge(origen, destino, tipo=tipo)

salida = {
    "metadata": {
        "origen": "Ontologia SKOS CCLTR",
        "normalizacion_uri": aliases,
        "nodos": G.number_of_nodes(),
        "aristas": G.number_of_edges(),
    },
    "nodes": [
        {"data": {"id": uri, **atributos}}
        for uri, atributos in G.nodes(data=True)
    ],
    "edges": [
        {
            "data": {
                "id": f"e{i}",
                "source": origen,
                "target": destino,
                **atributos,
            }
        }
        for i, (origen, destino, atributos)
        in enumerate(G.edges(data=True))
    ],
}

destino = base / "visualizacion/ontologia_grafo.json"
destino.parent.mkdir(parents=True, exist_ok=True)

with open(destino, "w", encoding="utf-8") as f:
    json.dump(salida, f, ensure_ascii=False, indent=2)

print("Grafo generado correctamente")
print("Nodos:", G.number_of_nodes())
print("Aristas:", G.number_of_edges())
print("Archivo:", destino)
