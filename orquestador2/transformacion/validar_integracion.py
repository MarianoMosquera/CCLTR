"""Valida que los nodos nuevos estén conectados con vínculos justificados."""


def verificar_integracion_nodos_nuevos(grafo_original, grafo_transformado):
    originales = {n["id"] for n in grafo_original["nodes"]}
    actuales = {n["id"] for n in grafo_transformado["nodes"]}
    nuevos = actuales - originales
    conectados = set()
    for arista in grafo_transformado["edges"]:
        source, target = arista.get("source"), arista.get("target")
        if source not in actuales or target not in actuales:
            raise ValueError("Vínculo con extremos inexistentes")
        if source == target:
            continue
        if source in nuevos or target in nuevos:
            if arista.get("tipo") not in {"PRO", "CON", "SIN_DEFINIR"}:
                raise ValueError(f"Vínculo de nodo nuevo sin tipo PRO/CON/SIN_DEFINIR: {source} -> {target}")
            justificacion = arista.get("justificacion")
            if not isinstance(justificacion, str) or not justificacion.strip():
                raise ValueError(f"Vínculo de nodo nuevo sin justificación: {source} -> {target}")
        conectados.update((source, target))
    aislados = sorted(nuevos - conectados)
    if aislados:
        raise ValueError("Nodos nuevos sin integración relacional: " + ", ".join(aislados))
    return True
