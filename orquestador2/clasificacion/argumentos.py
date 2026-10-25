"""Validación de clasificaciones semánticas sin alterar el grafo original."""

FUNCIONES = {"pragmatica", "condicional", "prospectiva"}

def validar_clasificaciones(debate, clasificaciones, conceptos):
    if not isinstance(clasificaciones, dict):
        raise ValueError("Las clasificaciones deben ser un diccionario.")

    nodos = {str(n["id"]): n for n in debate["nodes"]}
    ids = set(nodos)

    for nodo_id, registro in clasificaciones.items():
        if str(nodo_id) not in ids:
            raise ValueError(f"Nodo inexistente: {nodo_id}")

        if not isinstance(registro, dict):
            raise ValueError(f"Registro inválido: {nodo_id}")

        anclajes = registro.get("anclajes", [])
        funciones = registro.get("funciones", [])

        if not isinstance(anclajes, list) or not isinstance(funciones, list):
            raise ValueError(f"Listas inválidas: {nodo_id}")

        if len(funciones) != len(set(funciones)):
            raise ValueError(f"Funciones duplicadas: {nodo_id}")

        if not set(funciones).issubset(FUNCIONES):
            raise ValueError(f"Función desconocida: {nodo_id}")

        uris = []
        for anclaje in anclajes:
            if not isinstance(anclaje, dict):
                raise ValueError(f"Anclaje inválido: {nodo_id}")

            uri = anclaje.get("uri")
            evidencia = anclaje.get("evidencia")

            if uri not in conceptos:
                raise ValueError(f"Concepto SKOS desconocido: {uri}")

            if not isinstance(evidencia, str) or not evidencia.strip():
                raise ValueError(f"Falta evidencia textual: {nodo_id}")

            texto = str(nodos[str(nodo_id)].get("claim", ""))
            if evidencia.strip().casefold() not in texto.casefold():
                raise ValueError(
                    f"Evidencia no encontrada en el argumento: {nodo_id}"
                )

            uris.append(uri)

        if len(uris) != len(set(uris)):
            raise ValueError(f"Conceptos duplicados: {nodo_id}")

    return True


if __name__ == "__main__":
    debate = {
        "nodes": [{"id": "A", "claim": "Argumento de prueba"}],
        "edges": []
    }
    conceptos = {"urn:concepto:1": {"label_es": "Prueba"}}
    clasificaciones = {
        "A": {
            "anclajes": [
                {"uri": "urn:concepto:1", "evidencia": "Argumento de prueba"}
            ],
            "funciones": ["pragmatica"]
        }
    }

    assert validar_clasificaciones(debate, clasificaciones, conceptos)
    print("VALIDADOR DE ARGUMENTOS: OK")
