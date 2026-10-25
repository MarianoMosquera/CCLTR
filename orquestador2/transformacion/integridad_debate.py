"""Integridad estructural y auditoría de la copia transformada.

La inmutabilidad del grafo fuente la controla registro.verificar_integridad_original.
"""
from collections import Counter
import json


def firma(elemento):
    return json.dumps(elemento, sort_keys=True, ensure_ascii=False)


def verificar_conservacion_debate(registro):
    original = registro["grafo_original"]
    transformado = registro["grafo_transformado"]
    if not isinstance(transformado, dict):
        raise ValueError("Grafo transformado no inicializado")
    if not isinstance(transformado.get("nodes"), list) or not isinstance(transformado.get("edges"), list):
        raise ValueError("Estructura del grafo transformado inválida")

    ids = [str(n["id"]) for n in transformado["nodes"]]
    if len(ids) != len(set(ids)):
        raise ValueError("Identificadores duplicados")
    actuales = set(ids)
    for e in transformado["edges"]:
        if str(e["source"]) not in actuales or str(e["target"]) not in actuales:
            raise ValueError("Vínculo con extremos inexistentes")

    eventos = [e for e in registro.get("transformaciones", []) if e.get("estado") == "ejecutada"]
    nodos_retirados = {str(e["nodo_retirado"]["id"]) for e in eventos if "nodo_retirado" in e}
    aristas_retiradas = Counter(firma(e["relacion_retirada"]) for e in eventos if "relacion_retirada" in e)
    originales = {str(n["id"]) for n in original["nodes"]}
    faltantes = originales - actuales
    if not faltantes <= nodos_retirados:
        raise ValueError("Se eliminaron nodos originales sin evento auditable")

    # No se permite desaparición silenciosa de aristas originales. Si se
    # retiró un nodo, sus vínculos debieron retirarse explícitamente antes.
    actuales_aristas = Counter(firma(e) for e in transformado["edges"])
    for sig, cantidad in Counter(firma(e) for e in original["edges"]).items():
        if actuales_aristas[sig] + aristas_retiradas[sig] < cantidad:
            raise ValueError("Se eliminó o alteró una relación original sin evento auditable")
    return True
