# CCLTR - Orquestador 2

## Arquitectura
Rama A: grafo original, clasificación SKOS y medición.
Rama B: transformación semántica, validación,
reclasificación SKOS y medición independiente.

La Rama B no recibe clasificaciones de la Rama A.

## Indicadores
- Diversidad dimensional
- Riqueza SKOS
- Diversidad funcional
- Diversidad semántica
- Ajuste por tamaño

## Test 0988
Ejecutor: Test/debate-0988/ejecutar_test_0988.py
Grafo: Test/debate-0988/grafo-original-20.json
Resultados: Test/debate-0988/resultados/

## Entorno
Crear y activar un entorno virtual de Python.
Instalar las dependencias del proyecto.
Ejecutar desde la raiz de CCLTR.

## Comprobacion previa sin API
PYTHONPATH=. python Test/debate-0988/ejecutar_test_0988.py

## Ejecucion con API
PYTHONPATH=. python Test/debate-0988/ejecutar_test_0988.py --ejecutar

## Comprobacion confirmada el 27-10-2026
PREFLIGHT OK
Nodos: 20
Conceptos SKOS: 398
Solicitudes Rama A: 20
Muestra comun: 10
Repeticiones: 1000
Modelo embeddings:
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
Revision:
e8f8c211226b894fcb81acc59f3b34ba3efd5f42

No se realizaron llamadas API durante esta comprobacion.

## Reglas
Preservar el grafo original.
Conservar independencia entre ramas.
Registrar respuestas y metadatos ASTRA.
Validar las transformaciones antes de medir.
No ejecutar llamadas pagas sin autorizacion.
