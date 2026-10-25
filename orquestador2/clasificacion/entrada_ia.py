"""Prepara argumentos y conceptos SKOS para clasificación mediante IA."""

def preparar_entrada(nodo, conceptos):
    if not isinstance(nodo, dict) or "id" not in nodo:
        raise ValueError("Nodo inválido")

    texto = nodo.get("claim")
    if not isinstance(texto, str) or not texto.strip():
        raise ValueError("Argumento sin texto")

    catalogo = []

    for uri, concepto in sorted(conceptos.items()):
        catalogo.append({
            "uri": uri,
            "label_es": concepto.get("label_es"),
            "label_en": concepto.get("label_en"),
            "broader": concepto.get("relaciones", {}).get("broader", []),
            "narrower": concepto.get("relaciones", {}).get("narrower", []),
            "related": concepto.get("relaciones", {}).get("related", [])
        })

    return {
        "argumento": {
            "id": str(nodo["id"]),
            "claim": texto
        },
        "ontologia": catalogo,
        "dimensiones": [
            "Valores", "Agenda", "Racionalidad", "Gobernanza"
        ],
        "funciones": [
            "pragmatica", "condicional", "prospectiva"
        ],
        "reglas": {
            "anclajes_minimos": 0,
            "anclajes_maximos": None,
            "uri_unica_por_concepto": True,
            "evidencia_textual_obligatoria": True,
            "preservar_pro_con_original": True
        }
    }


if __name__ == "__main__":
    ejemplo = {
        "id": "A",
        "claim": "La tecnología puede mejorar la seguridad pública."
    }
    conceptos = {
        "urn:ejemplo": {
            "label_es": "Seguridad",
            "label_en": "Security",
            "relaciones": {
                "broader": [],
                "narrower": [],
                "related": []
            }
        }
    }

    entrada = preparar_entrada(ejemplo, conceptos)
    assert len(entrada["ontologia"]) == 1
    assert entrada["argumento"]["id"] == "A"
    print("INTERFAZ DE CLASIFICACIÓN IA: OK")
