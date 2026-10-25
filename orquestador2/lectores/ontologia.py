import json
from pathlib import Path

SKOS = "http://www.w3.org/2004/02/skos/core#"


def cargar_ontologia(raiz="."):
    raiz = Path(raiz)

    ruta_ont = raiz / "ontologia/jsonld/ontologia.jsonld"
    ruta_en = raiz / "ontologia/visualizacion/ontology_labels_en.json"

    ontologia = json.loads(ruta_ont.read_text(encoding="utf-8"))
    etiquetas_en = json.loads(ruta_en.read_text(encoding="utf-8"))

    if not isinstance(ontologia, list):
        raise ValueError("La ontología debe ser una lista JSON-LD.")
    if not isinstance(etiquetas_en, dict):
        raise ValueError("Las etiquetas inglesas deben ser un diccionario.")

    conceptos = {}

    for entrada in ontologia:
        uri = entrada.get("@id")
        tipos = entrada.get("@type", [])

        if isinstance(tipos, str):
            tipos = [tipos]

        if not uri or SKOS + "Concept" not in tipos:
            continue

        if uri in conceptos:
            raise ValueError(f"Concepto duplicado: {uri}")

        etiquetas = entrada.get(SKOS + "prefLabel", [])
        if isinstance(etiquetas, dict):
            etiquetas = [etiquetas]

        etiqueta_es = next(
            (
                e.get("@value")
                for e in etiquetas
                if e.get("@language") == "es"
            ),
            None
        )

        relaciones = {}

        for tipo in ("broader", "narrower", "related"):
            valores = entrada.get(SKOS + tipo, [])
            if isinstance(valores, dict):
                valores = [valores]

            relaciones[tipo] = [
                v["@id"]
                for v in valores
                if isinstance(v, dict) and "@id" in v
            ]

        conceptos[uri] = {
            "uri": uri,
            "label_es": etiqueta_es,
            "label_en": etiquetas_en.get(uri),
            "relaciones": relaciones,
        }

    return conceptos


def diagnostico(conceptos):
    sin_ingles = [
        uri for uri, c in conceptos.items()
        if not c["label_en"]
    ]

    sin_espanol = [
        uri for uri, c in conceptos.items()
        if not c["label_es"]
    ]

    relaciones = {
        tipo: sum(
            len(c["relaciones"][tipo])
            for c in conceptos.values()
        )
        for tipo in ("broader", "narrower", "related")
    }

    return {
        "conceptos_skos": len(conceptos),
        "sin_etiqueta_ingles": sin_ingles,
        "sin_etiqueta_espanol": sin_espanol,
        "relaciones": relaciones,
    }


if __name__ == "__main__":
    conceptos = cargar_ontologia()
    print(json.dumps(
        diagnostico(conceptos),
        ensure_ascii=False,
        indent=2
    ))
