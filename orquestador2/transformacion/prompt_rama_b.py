import json
from copy import deepcopy


def construir_prompt_rama_b(entrada_b):
    """Construye instrucciones para una transformación semántica independiente."""

    if not isinstance(entrada_b, dict):
        raise TypeError("La entrada debe ser un diccionario")

    if set(entrada_b) != {"grafo_original", "ontologia_skos"}:
        raise ValueError("La rama B solo admite grafo original y ontología SKOS")

    grafo = entrada_b["grafo_original"]
    conceptos = entrada_b["ontologia_skos"]

    if not isinstance(grafo, dict) or not isinstance(conceptos, dict):
        raise TypeError("Grafo y ontología deben ser diccionarios")

    if not isinstance(grafo.get("nodes"), list):
        raise ValueError("Faltan los nodos originales")

    if not isinstance(grafo.get("edges"), list):
        raise ValueError("Faltan las relaciones originales")

    instrucciones = """
Sos un agente de transformación semántica del proyecto CCLTR.

OBJETIVO
Proponer nuevas perspectivas conceptuales a partir de posiciones
argumentativas originales, utilizando la ontología SKOS como
infraestructura de exploración semántica.

PRINCIPIOS OBLIGATORIOS
1. Conservá las posiciones originales y sus contradicciones genuinas.
2. No reduzcas el debate a una posición consensual ni a una síntesis
   que simplemente elimine las diferencias.
3. Explorá generalizaciones, especializaciones y asociaciones SKOS.
4. Podés proponer nuevos nodos, reformulaciones, fusiones, vínculos
   y prioridades conceptuales.
5. Una fusión no implica eliminar los nodos originales.
6. No inventes conceptos ni relaciones atribuyéndolos a la ontología.
7. Toda ruta SKOS declarada debe existir en los datos proporcionados.
8. Justificá qué aporta cada transformación y qué tensión conserva.
9. Distinguí la conservación de una contradicción de su resolución.
10. No presupongas que más conexiones implican más diversidad.
11. No solicites ni infieras clasificaciones, métricas o resultados
    de la rama A.
12. No modifiques las relaciones originales ni su valence PRO/CON.
    La valencia de una relación no define automáticamente la
    posición global de un nodo.

SALIDA
Devolvé exclusivamente un objeto JSON con la clave "propuestas",
que contenga una lista de operaciones candidatas.

Cada propuesta debe declarar:
- operacion
- justificacion

Las operaciones deben utilizar los campos establecidos por el motor
de transformación de CCLTR.

Para operaciones semánticas incluí:
- anclajes_skos: lista de URI existentes
- rutas_skos: recorridos explícitos con origen, destino,
  longitud y pasos; cada paso contiene origen, destino, tipo
  y relacion_skos
- tension_conservada: explicación de la oposición preservada
- aporte_conceptual: explicación de la perspectiva emergente

No presentes ninguna propuesta como científicamente validada.
"""

    datos = {
        "grafo_original": deepcopy(grafo),
        "ontologia_skos": deepcopy(conceptos),
    }

    return {
        "instrucciones": instrucciones.strip(),
        "datos": datos,
    }


if __name__ == "__main__":
    entrada = {
        "grafo_original": {
            "nodes": [
                {"id": "A", "claim": "Priorizar innovación"},
                {"id": "B", "claim": "Priorizar protección laboral"},
            ],
            "edges": [
                {
                    "source": "A",
                    "target": "B",
                    "target_idx": 0,
                    "valence": "CON",
                }
            ],
        },
        "ontologia_skos": {},
    }

    resultado = construir_prompt_rama_b(entrada)

    assert set(resultado) == {"instrucciones", "datos"}
    assert resultado["datos"]["grafo_original"] == entrada["grafo_original"]
    assert "rama A" in resultado["instrucciones"]
    assert "tension_conservada" in resultado["instrucciones"]

    json.dumps(resultado, ensure_ascii=False)

    print("PROMPT DE RAMA B CONSTRUIDO: OK")
    print("INDEPENDENCIA DE RAMA A: OK")
    print("CONSERVACIÓN DE CONTRADICCIONES: OK")
    print("FORMATO JSON SERIALIZABLE: OK")
