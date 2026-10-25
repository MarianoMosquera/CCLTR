"""Riqueza SKOS comparable entre ramas experimentales."""

import math

from orquestador2.medicion.riqueza_normalizada import riqueza_rarefactada


def medir_riqueza_comparable(clasificaciones, configuracion):
    configuracion.validar()

    resultado = riqueza_rarefactada(
        clasificaciones,
        tamano_muestra=configuracion.tamano_muestra,
        repeticiones=configuracion.repeticiones,
        semilla=configuracion.semilla
    )

    referencia = configuracion.referencia_riqueza
    riqueza = resultado["riqueza_media"]
    valor = riqueza / referencia

    if not math.isfinite(valor):
        raise ValueError("Riqueza normalizada no finita")

    if valor > 1:
        raise ValueError(
            "La riqueza supera la referencia común. "
            "Revisar la configuración experimental."
        )

    return {
        **resultado,
        "referencia_riqueza": referencia,
        "riqueza_normalizada": valor,
        "estado": "calculado"
    }


if __name__ == "__main__":
    from orquestador2.medicion.configuracion import ConfiguracionMedicion

    configuracion = ConfiguracionMedicion(
        tamano_muestra=2,
        repeticiones=100,
        semilla=42,
        referencia_riqueza=4,
        modelo_embeddings="MODELO_DE_PRUEBA",
        version_embeddings="VERSION_DE_PRUEBA"
    )

    clasificaciones = {
        "A": {"anclajes": [{"uri": "urn:A"}]},
        "B": {"anclajes": [{"uri": "urn:B"}]},
        "C": {"anclajes": [{"uri": "urn:C"}]},
        "D": {"anclajes": [{"uri": "urn:D"}]}
    }

    resultado = medir_riqueza_comparable(
        clasificaciones, configuracion
    )

    assert resultado["riqueza_media"] == 2
    assert resultado["riqueza_normalizada"] == 0.5

    print("RIQUEZA COMPARABLE: OK")
    print("RIQUEZA MEDIA:", resultado["riqueza_media"])
    print("RIQUEZA NORMALIZADA:", resultado["riqueza_normalizada"])
