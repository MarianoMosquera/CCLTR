"""Conexión API para el Orquestador 2 de CCLTR.

No modifica prompts, grafos, ontologías ni validadores.
"""
import json
from pathlib import Path
from openai import OpenAI

MODELO = "gpt-6-astra"
RAZONAMIENTO = "high"


def consultar_astra(instrucciones, datos, archivo_cache):
    """Consulta ASTRA High o recupera una respuesta ya guardada."""
    ruta = Path(archivo_cache)

    if ruta.exists():
        with ruta.open(encoding="utf-8") as f:
            registro = json.load(f)
        print(f"Respuesta recuperada: {ruta}")
        return registro["respuesta"]

    cliente = OpenAI(timeout=600.0)

    respuesta = cliente.responses.create(
        model=MODELO,
        reasoning={"effort": RAZONAMIENTO},
        instructions=instrucciones,
        input="Devolvé exclusivamente un objeto JSON válido.\\n"
              + json.dumps(datos, ensure_ascii=False),
        text={"format": {"type": "json_object"}},
        max_output_tokens=12000,
    )

    if respuesta.status != "completed":
        raise RuntimeError(
            f"Respuesta incompleta de ASTRA: {respuesta.status}"
        )

    contenido = json.loads(respuesta.output_text)

    registro = {
        "modelo": respuesta.model,
        "razonamiento": RAZONAMIENTO,
        "respuesta_id": respuesta.id,
        "tokens_entrada": respuesta.usage.input_tokens,
        "tokens_salida": respuesta.usage.output_tokens,
        "tokens_totales": respuesta.usage.total_tokens,
        "respuesta": contenido,
    }

    ruta.parent.mkdir(parents=True, exist_ok=True)

    with ruta.open("w", encoding="utf-8") as f:
        json.dump(registro, f, ensure_ascii=False, indent=2)

    print(
        f"ASTRA: {respuesta.usage.total_tokens} tokens. "
        f"Guardado: {ruta}"
    )

    return contenido


def ejecutar_solicitudes(solicitudes, carpeta_cache):
    """Ejecuta las solicitudes originales del clasificador."""
    resultados = {}

    for indice, (nodo_id, solicitud) in enumerate(
        solicitudes.items(), start=1
    ):
        print(f"Clasificación {indice}/{len(solicitudes)}: {nodo_id}")

        resultados[nodo_id] = consultar_astra(
            instrucciones=solicitud["instrucciones"],
            datos=solicitud["entrada"],
            archivo_cache=Path(carpeta_cache) / f"{nodo_id}.json",
        )

    return resultados
