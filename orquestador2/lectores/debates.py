import copy
import json
from pathlib import Path

CAMPOS_OBLIGATORIOS = ("nodes", "edges")


def cargar_debate(ruta):
    ruta = Path(ruta)
    datos = json.loads(ruta.read_text(encoding="utf-8"))

    if not isinstance(datos, dict):
        raise ValueError("El debate debe ser un objeto JSON.")

    for campo in CAMPOS_OBLIGATORIOS:
        if campo not in datos or not isinstance(datos[campo], list):
            raise ValueError(f"Campo obligatorio inválido: {campo}")

    identificadores = set()

    for nodo in datos["nodes"]:
        if not isinstance(nodo, dict) or "id" not in nodo:
            raise ValueError("Todos los nodos deben tener un id.")

        identificador = nodo["id"]

        if not isinstance(identificador, (str, int)):
            raise ValueError("Los identificadores deben ser cadenas o enteros.")

        if identificador in identificadores:
            raise ValueError(f"Nodo duplicado: {identificador}")

        identificadores.add(identificador)

    for i, arista in enumerate(datos["edges"]):
        if not isinstance(arista, dict):
            raise ValueError(f"Arista {i} inválida.")

        origen = arista.get("source")
        destino = arista.get("target")

        if origen not in identificadores:
            raise ValueError(f"Arista {i}: origen inexistente.")

        if destino not in identificadores:
            raise ValueError(f"Arista {i}: destino inexistente.")

    return datos


def preparar_ramas(debate):
    # Copias independientes: ninguna rama modifica la otra.
    return {
        "rama_a": copy.deepcopy(debate),
        "rama_b": copy.deepcopy(debate),
    }


def resumen(debate):
    valencias = {}

    for arista in debate["edges"]:
        valor = arista.get("valence", "SIN_VALENCIA")
        valencias[str(valor)] = valencias.get(str(valor), 0) + 1

    return {
        "nodos": len(debate["nodes"]),
        "aristas": len(debate["edges"]),
        "dirigido": debate.get("directed"),
        "valencias": valencias,
    }


if __name__ == "__main__":
    print("Lector general de debates: disponible.")
    print("No se ha seleccionado ni cargado ningún debate.")
