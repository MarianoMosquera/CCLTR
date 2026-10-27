"""Adaptación auditable de respuestas ASTRA al contrato del Orquestador 2."""

import json
import re
from copy import deepcopy
from pathlib import Path

from orquestador2.transformacion.operaciones import validar_operacion

PATRON_URI = re.compile(r"^\[(https?://[^\]]+)\]\((https?://[^)]+)\)$")


def normalizar_uri(valor):
    if not isinstance(valor, str):
        return valor
    coincidencia = PATRON_URI.fullmatch(valor)
    if coincidencia:
        etiqueta, destino = coincidencia.groups()
        if etiqueta != destino:
            raise ValueError(f"URI Markdown inconsistente: {valor}")
        return destino
    return valor


def normalizar_valores(objeto):
    if isinstance(objeto, dict):
        return {k: normalizar_valores(v) for k, v in objeto.items()}
    if isinstance(objeto, list):
        return [normalizar_valores(v) for v in objeto]
    return normalizar_uri(objeto)


def adaptar_respuesta(respuesta):
    original = deepcopy(respuesta)

    if not isinstance(original, dict):
        raise ValueError("Respuesta ASTRA inválida")

    propuestas = original.get("propuestas")
    if not isinstance(propuestas, list):
        raise ValueError("Falta la lista de propuestas")

    adaptadas = []

    for indice, propuesta in enumerate(propuestas, 1):
        p = normalizar_valores(deepcopy(propuesta))
        p = normalizar_rutas_skos(p)

        if p.get("operacion") == "agregar_nodo":
            nodo = p.get("nodo")

            if not isinstance(nodo, dict):
                raise ValueError(f"Propuesta {indice}: falta nodo")

            if not nodo.get("id") or not nodo.get("claim"):
                raise ValueError(
                    f"Propuesta {indice}: faltan id o claim"
                )

            p["operacion"] = "crear_nodo"
            p["id_nuevo"] = nodo["id"]
            p["claim"] = nodo["claim"]

        # Validar usando el contrato original del motor.
        validar_operacion(p)
        adaptadas.append(p)

    return {
        "original": original,
        "adaptada": {"propuestas": adaptadas},
        "cantidad": len(adaptadas),
    }



def normalizar_rutas_skos(propuesta):
    equivalencias = {
        "broader": "generalizacion",
        "narrower": "especializacion",
        "related": "asociacion",
    }

    prefijo = "http://www.w3.org/2004/02/skos/core#"

    for ruta in propuesta.get("rutas_skos", []):
        for paso in ruta.get("pasos", []):
            tipo = paso.get("tipo")
            relacion = paso.get("relacion_skos")

            if tipo in equivalencias:
                paso["tipo"] = equivalencias[tipo]

            if isinstance(relacion, str) and relacion.startswith(prefijo):
                paso["relacion_skos"] = relacion[len(prefijo):]

    return propuesta


def guardar_adaptacion(resultado, carpeta):
    destino = Path(carpeta)
    destino.mkdir(parents=True, exist_ok=True)

    archivo = destino / "transformacion_b_adaptada.json"

    with archivo.open("w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    return archivo
