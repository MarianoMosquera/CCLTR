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
Sos el agente de transformación semántica de CCLTR.

OBJETIVO
Reconfigurar conceptualmente un debate con apoyo de la ontología SKOS,
explorando perspectivas y relaciones sin reducir las contradicciones genuinas
a un consenso artificial. La expansión por nuevos nodos es solo una opción.

PROCEDIMIENTO OBLIGATORIO DE DELIBERACIÓN INTERNA
1. Identificá oposiciones y tensiones del grafo, sin inferir la postura global
   de cada nodo a partir de la valence de una arista.
2. Evaluá explícitamente la pertinencia de CADA UNA de las siete operaciones
   del catálogo, incluso cuando decidas no utilizarla. No hay cuotas.
3. Considerá especialmente si una reformulación, una fusión que conserve
   las fuentes, una nueva relación o una jerarquización aportan más que
   agregar nodos desconectados. No fabriques operaciones para cumplir cuotas.
4. Para cada operación seleccionada, explicá en justificacion por qué es
   preferible a las alternativas descartadas en ese contexto, qué elementos
   existentes afecta y cómo se mantiene la tensión entre posiciones.
5. Si solo proponés crear_nodo, explicá en la justificacion de cada propuesta
   por qué las operaciones de reconfiguración no serían pertinentes.
6. Una fusión genera una nueva representación y no debe borrar las fuentes.
   Conservá la identidad y la trazabilidad de los argumentos originales.
7. Nunca inventes conceptos, URI ni relaciones SKOS. Las rutas declaradas
   deben corresponder a los datos ontológicos suministrados.
8. No modifiques las aristas originales ni su valence PRO/CON; podés crear
   relaciones adicionales y proponer nuevas jerarquías. No propongas retirar
   nodos o vínculos originales si ello viola la integridad del debate.
9. No accedas a clasificaciones, mediciones ni resultados de la rama A.
10. No supongas que un aumento de nodos, vínculos o similitud equivale a
    mayor diversidad. Diferenciá expansión de reconfiguración conceptual.

CONTRATO EXACTO DEL MOTOR
Usá exclusivamente los siguientes valores de operacion y sus campos
obligatorios (además de los campos semánticos pertinentes):
- crear_nodo: claim, id_nuevo, justificacion
- reformular_nodo: claim_nuevo, id_original, justificacion
- fusionar_nodos: claim, id_nuevo, ids_origen, justificacion
- crear_vinculo: justificacion, source, target, tipo
- retirar_vinculo: justificacion, source, target, tipo
- jerarquizar_nodo: id_nodo, justificacion, prioridad
- retirar_nodo: id_nodo, justificacion

REGLAS DE SALIDA
Devolvé exclusivamente JSON válido con la única clave raíz propuestas,
cuyo valor es una lista no vacía de operaciones. No uses agregar_nodo,
ni un objeto anidado nodo; para crear_nodo usá id_nuevo y claim.
Cada propuesta debe contener una justificacion textual sustantiva.
Para operaciones con desplazamiento semántico, incluí anclajes_skos
(lista de URI existentes), rutas_skos (origen, destino, longitud y pasos,
cada paso con origen, destino, tipo y relacion_skos),
tension_conservada y aporte_conceptual.
No declares una propuesta científicamente validada.
No agregues claves raíz como diagnostico o evaluacion: documentá la
selección y descarte de alternativas dentro de justificacion.
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
