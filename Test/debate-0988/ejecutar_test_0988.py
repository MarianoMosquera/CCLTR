"""Ejecutor reproducible Test 0988. Ejecutar desde la raíz del repositorio CCLTR.
Por defecto solo preflight. --ejecutar habilita llamadas API, con caché.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path

from orquestador2.lectores.ontologia import cargar_ontologia
from orquestador2.experimento_ab import (
    preparar_experimento_ab, validar_clasificacion_a,
    ejecutar_transformacion_b, validar_clasificacion_b,
    medir_rama, comparar_experimento_ab,
)
from orquestador2.integracion.cliente_astra import consultar_astra, ejecutar_solicitudes
from orquestador2.integracion.normalizar_astra import adaptar_respuesta, guardar_adaptacion
from orquestador2.integracion.exportador import exportar_experimento
from orquestador2.transformacion.prompt_rama_b import construir_prompt_rama_b
from orquestador2.medicion.generador_embeddings import cargar_modelo
from orquestador2.medicion.configuracion import ConfiguracionMedicion
from orquestador2.medicion.mapa_dimensiones import construir_mapa_dimensiones

BASE = Path('Test/debate-0988')
ORIGEN = BASE / 'grafo-original-20.json'
DESTINO = BASE / 'resultados'
CACHE = DESTINO / 'cache_astra'


def guardar(ruta, obj):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')


def huella(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--ejecutar', action='store_true', help='Autorizar llamadas ASTRA')
    p.add_argument('--repeticiones', type=int, default=1000)
    p.add_argument('--tamano-muestra', type=int, default=10,
                   help='Debe ser <= número de nodos en ambas ramas')
    args = p.parse_args()
    if not ORIGEN.is_file():
        raise SystemExit(f'No existe {ORIGEN}. Ejecutá desde ~/CCLTR')
    grafo = json.loads(ORIGEN.read_text(encoding='utf-8'))
    conceptos = cargar_ontologia('.')
    experimento = preparar_experimento_ab(grafo, conceptos)
    prompt_b = construir_prompt_rama_b(experimento['rama_b']['entrada'])
    mapa = construir_mapa_dimensiones('.')
    # Obligatorio antes de cualquier gasto API: modelo y revisión instalados localmente.
    modelo, config_modelo = cargar_modelo()
    muestra = args.tamano_muestra
    if not 2 <= muestra <= len(grafo['nodes']):
        raise SystemExit('La muestra debe tener entre 2 y el número de nodos originales')
    cfg = ConfiguracionMedicion(
        tamano_muestra=muestra, repeticiones=args.repeticiones,
        semilla=42, referencia_riqueza=float(len(conceptos)),
        modelo_embeddings=config_modelo['modelo'],
        version_embeddings=config_modelo['revision'],
    )
    cfg.validar()
    original_hash = huella(ORIGEN)
    print('PREFLIGHT OK | nodos:', len(grafo['nodes']), '| SKOS:', len(conceptos),
          '| solicitudes A:', len(experimento['rama_a']['solicitudes_clasificacion']))
    print('Embeddings:', config_modelo['modelo'], 'revision:', config_modelo['revision'])
    print('Muestra común:', muestra, '| repeticiones:', args.repeticiones)
    if not args.ejecutar:
        print('SIN LLAMADAS API. Para iniciar: python3 ejecutar_test_0988.py --ejecutar')
        return
    if not os.getenv('OPENAI_API_KEY') and not all(
        (CACHE / 'rama_a' / f'{nid}.json').is_file()
        for nid in experimento['rama_a']['solicitudes_clasificacion']
    ):
        raise SystemExit('Falta OPENAI_API_KEY para las llamadas pendientes.')
    DESTINO.mkdir(parents=True, exist_ok=True)
    guardar(DESTINO / 'configuracion.json', {
        'grafo_sha256': original_hash, 'configuracion': cfg.exportar(),
        'modelo_astra': 'gpt-6-astra', 'razonamiento': 'high',
        'advertencia': 'Referencia de riqueza = cantidad de conceptos SKOS; muestra fija predefinida',
    })
    # La entrada de B no incorpora resultados de A.
    respuestas_a = ejecutar_solicitudes(
        experimento['rama_a']['solicitudes_clasificacion'], CACHE / 'rama_a')
    clas_a = validar_clasificacion_a(experimento, respuestas_a, grafo, conceptos)
    guardar(DESTINO / 'clasificaciones_a.json', clas_a)
    respuesta_b = consultar_astra(prompt_b['instrucciones'], prompt_b['datos'],
                                  CACHE / 'transformacion_b.json')
    adaptada = adaptar_respuesta(respuesta_b)
    guardar_adaptacion(adaptada, DESTINO)
    transformacion = ejecutar_transformacion_b(experimento, adaptada['adaptada'])
    grafo_b = transformacion['registro']['grafo_transformado']
    guardar(DESTINO / 'grafo_transformado_b.json', grafo_b)
    if len(grafo_b['nodes']) < muestra:
        raise SystemExit('Rama B tiene menos nodos que la muestra predefinida. '
                         'Revisar diseño y ejecutar con --tamano-muestra menor; '
                         'las respuestas ASTRA ya están en caché.')
    respuestas_b = ejecutar_solicitudes(
        transformacion['solicitudes_clasificacion'], CACHE / 'rama_b')
    clas_b = validar_clasificacion_b(transformacion, respuestas_b)
    guardar(DESTINO / 'clasificaciones_b.json', clas_b)
    med_a = medir_rama(grafo, clas_a, mapa, cfg, modelo, config_modelo)
    med_b = medir_rama(grafo_b, clas_b, mapa, cfg, modelo, config_modelo)
    comparacion = comparar_experimento_ab(med_a, med_b)
    archivos = exportar_experimento('debate-0988', grafo,
        {'grafo': grafo, 'clasificaciones': clas_a, 'medicion': med_a},
        {'grafo': grafo_b, 'clasificaciones': clas_b,
         'registro_transformacion': transformacion['registro'], 'medicion': med_b},
        comparacion, destino=DESTINO)
    if huella(ORIGEN) != original_hash:
        raise RuntimeError('ALERTA: el archivo original cambió durante el experimento')
    print('EXPERIMENTO A/B COMPLETO:', archivos)
    print('Comparación índice global:', comparacion['comparacion']['indice_global'])


if __name__ == '__main__':
    main()
