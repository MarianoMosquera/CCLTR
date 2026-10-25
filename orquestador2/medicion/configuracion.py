"""Configuración reproducible de la medición de diversidad CCLTR."""

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class ConfiguracionMedicion:
    tamano_muestra: int
    repeticiones: int = 1000
    semilla: int = 42
    referencia_riqueza: float = 1.0
    modelo_embeddings: str = "PENDIENTE"
    version_embeddings: str = "PENDIENTE"

    def validar(self):
        if self.tamano_muestra < 1:
            raise ValueError("Tamaño de muestra inválido")
        if self.repeticiones < 1:
            raise ValueError("Repeticiones inválidas")
        if self.referencia_riqueza <= 0:
            raise ValueError("Referencia de riqueza inválida")
        if self.modelo_embeddings == "PENDIENTE":
            raise ValueError("Modelo de embeddings no definido")
        if self.version_embeddings == "PENDIENTE":
            raise ValueError("Versión de embeddings no definida")
        return True

    def exportar(self):
        return asdict(self)


if __name__ == "__main__":
    configuracion = ConfiguracionMedicion(
        tamano_muestra=100,
        repeticiones=1000,
        semilla=42,
        referencia_riqueza=50.0,
        modelo_embeddings="MODELO_DE_PRUEBA",
        version_embeddings="VERSION_DE_PRUEBA"
    )

    assert configuracion.validar()
    assert configuracion.exportar()["tamano_muestra"] == 100

    print("CONFIGURACIÓN EXPERIMENTAL: OK")
    print("MUESTRA:", configuracion.tamano_muestra)
    print("REPETICIONES:", configuracion.repeticiones)
