"""Exportación reproducible de experimentos A/B del Orquestador 2."""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def _json_canonico(datos):
    return json.dumps(
        datos,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def exportar_experimento(
    identificador,
    debate_original,
    rama_a,
    rama_b,
    comparacion,
    destino="orquestador2/resultados",
):
    """Guarda el expediente completo y un JSON para visualización estática."""

    if not isinstance(identificador, str) or not identificador:
        raise ValueError("El identificador del experimento es obligatorio.")

    if not all(isinstance(x, dict) for x in
               (debate_original, rama_a, rama_b, comparacion)):
        raise ValueError("Los componentes del experimento deben ser diccionarios.")

    carpeta = Path(destino)
    carpeta.mkdir(parents=True, exist_ok=True)

    contenido = {
        "version_esquema": "1.0",
        "identificador": identificador,
        "debate_original": debate_original,
        "rama_a": rama_a,
        "rama_b": rama_b,
        "comparacion": comparacion,
    }

    huella = hashlib.sha256(
        _json_canonico(contenido).encode("utf-8")
    ).hexdigest()

    expediente = {
        **contenido,
        "integridad": {
            "algoritmo": "SHA-256",
            "huella_contenido": huella,
        },
        "exportado_utc": datetime.now(timezone.utc).isoformat(),
    }

    ruta_expediente = carpeta / f"{identificador}_expediente.json"
    ruta_visualizacion = carpeta / f"{identificador}_visualizacion.json"

    visualizacion = {
        "identificador": identificador,
        "debate_original": debate_original,
        "rama_a": rama_a,
        "rama_b": rama_b,
        "comparacion": comparacion,
        "huella_expediente": huella,
    }

    for ruta, datos in (
        (ruta_expediente, expediente),
        (ruta_visualizacion, visualizacion),
    ):
        ruta.write_text(
            json.dumps(datos, ensure_ascii=False, indent=2, allow_nan=False),
            encoding="utf-8",
        )

    return {
        "expediente": str(ruta_expediente),
        "visualizacion": str(ruta_visualizacion),
        "sha256": huella,
    }
