
from pathlib import Path
from rdflib import Graph

base = Path("ontologia")
archivos = sorted((base / "ttl").rglob("*.ttl"))

grafo = Graph()

for archivo in archivos:
    grafo.parse(archivo, format="turtle")
    print(f"Integrado: {archivo.name}")

print(f"Total de triples únicos: {len(grafo)}")

salida = base / "jsonld" / "ontologia.jsonld"
salida.parent.mkdir(parents=True, exist_ok=True)

grafo.serialize(
    destination=str(salida),
    format="json-ld",
    indent=2,
    ensure_ascii=False
)

verificacion = Graph()
verificacion.parse(salida, format="json-ld")

if not grafo.isomorphic(verificacion):
    raise RuntimeError("La conversión no conservó el grafo RDF")

print("Conversión validada: grafos RDF equivalentes")
print(f"Archivo generado: {salida}")

