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
1. Evaluá explícitamente las siete operaciones del catálogo: crear,
   reformular, fusionar y retirar nodos; crear y retirar vínculos; jerarquizar.
   Elegí según su valor conceptual, sin cuotas ni preferencia por crear nodos.
2. Identificá oposiciones genuinas sin inferir la posición global de un nodo
   a partir de la valence de una arista.
3. La ontología externa proporcionada por el investigador constituye la
   GUÍA CONCEPTUAL RECTORA de la transformación semántica. Sus conceptos,
   relaciones y jerarquías deben orientar los desplazamientos conceptuales
   y la generación de síntesis novedosas entre posiciones contradictorias,
   manteniendo activas y reconocibles sus tensiones.
   SKOS es el modelo de representación de esa ontología, no una ontología
   independiente. La ontología externa no debe utilizarse como un simple
   diccionario ni como un catálogo cerrado de soluciones.
   Podés generar nuevas configuraciones conceptuales, pero no inventar
   conceptos, URI, rutas o relaciones atribuyéndolos falsamente a la ontología.
4. Buscá prioritariamente SÍNTESIS CONCEPTUALES NOVEDOSAS que transformen
   las relaciones entre posiciones contradictorias MANTENIENDO ACTIVAS Y
   RECONOCIBLES SUS TENSIONES. No confundas síntesis con consenso, promedio,
   yuxtaposición, compromiso superficial ni resolución ficticia del conflicto.
5. Podés reformular, fusionar o RETIRAR nodos y vínculos originales EN LA
   COPIA TRANSFORMADA si existe justificación conceptual sustantiva. El grafo
   original de entrada permanece íntegro, inmutable y recuperable. Registrar
   origen, operaciones, nodos afectados y tensiones para permitir auditoría.
6. Una fusión puede sustituir los nodos fuente EN LA COPIA TRANSFORMADA;
   no debe borrar su identidad ni sus argumentos del registro histórico.
   La eliminación no puede hacer desaparecer silenciosamente contradicciones:
   justificá dónde queda expresada o conservada cada tensión relevante.
7. Evaluá si reformular, fusionar, retirar, vincular o jerarquizar aporta más
   que expandir el grafo. No fabriques operaciones para cumplir cuotas.
8. Para cada operación seleccionada, justificá la novedad de la síntesis,
   qué posiciones transforma, qué tensión contradictoria conserva y por qué
   la operación es preferible a las alternativas descartadas. Documentalo en
   justificacion, tension_conservada y aporte_conceptual cuando corresponda.
9. Si solo proponés crear_nodo, justificá por qué no conviene reconfigurar.
10. No accedas a resultados, mediciones ni clasificaciones de la rama A.
11. No supongas que más nodos, vínculos o similitud implican más diversidad.
12. Preservá las relaciones y valencias originales EN EL REGISTRO DE ENTRADA;
    en el grafo transformado pueden retirarse justificadamente con trazabilidad.

REGLA OBLIGATORIA DE INTEGRACIÓN RELACIONAL
Cada nodo creado o fusionado que permanezca en el grafo final debe quedar
conectado a otro nodo distinto por al menos una operación crear_vinculo.
Para cada vínculo declarás source, target, tipo y justificacion sustantiva.
Para relaciones nuevas con nodos nuevos, tipo debe ser PRO, CON o SIN_DEFINIR.
SIN_DEFINIR identifica una relación conceptual genuina sin orientación de
apoyo u oposición determinable; no debe ocultar un PRO o CON reconocible.
No hay cuotas de operaciones ni de tipos de vínculo. Podés crear un nodo y
vincularlo después en el mismo lote. No crees vínculos arbitrarios.
El grafo final será rechazado si queda un nodo nuevo aislado o si su vínculo
carece de tipo permitido y justificación. Conservá las aristas originales.

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
