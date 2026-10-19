# CCLTR · syncIALO Argument Map Explorer (V1)

Explorador de tesis centrales sobre IA en los mapas originales de [syncIALO](https://huggingface.co/datasets/DebateLabKIT/syncialo-raw), de DebateLab KIT.

## Arquitectura

1. Python consulta la API pública de Hugging Face y recupera archivos JSON del repositorio.
2. NetworkX lee los grafos **existentes** y detecta una tesis central por mapa.
3. Un filtro léxico reproducible selecciona tesis que mencionan IA o tecnologías asociadas.
4. Se exportan índice y grafos seleccionados en JSON.
5. La interfaz HTML/JavaScript visualiza esos JSON sin Python en ejecución.

**Limitación V1:** búsqueda léxica, no equivalencia semántica. La identificación del nodo raíz se verifica por mapa; los casos ambiguos se registran en `datos/errores.json`. No se asegura cobertura total hasta ejecutar el barrido completo.

## Primer ensayo

```bash
pip install -r requirements.txt
python -m orquestador.pipeline --limit 10
```

Para procesar todo el conjunto configurado:

```bash
python -m orquestador.pipeline
```

Se usa la caché local de `huggingface_hub`. El pipeline descarga individualmente los JSON necesarios; no descarga el repositorio completo en un único archivo.

## GitHub Actions

En **Actions → Actualizar mapas syncIALO → Run workflow**, usar `10` para prueba o `0` para todos. La acción escribe resultados en `datos/` y necesita permisos de escritura del repositorio (Settings → Actions → General → Workflow permissions).

## Publicación en Static Space gratuito

Copiar `space/index.html` y `space/app.js` al repositorio del Space y configurar `RAW_BASE` en `app.js` con la URL raw de `datos/` en GitHub público, por ejemplo:

```js
const RAW_BASE = 'https://raw.githubusercontent.com/marianomosquera/CCLTR/main/datos';
```

Alternativamente copiar `datos/` junto a la interfaz y cambiar `RAW_BASE` a `./datos`. En un Static Space no se ejecuta NetworkX: se consumen grafos precalculados y se muestran con Cytoscape.js.

## Procedencia

Los datos son de DebateLab KIT / syncIALO. Revisar la licencia y requisitos de atribución del dataset antes de redistribuir los JSON procesados. Los enlaces a archivos originales se preservan en el índice.

## Repositorio destino

https://github.com/marianomosquera/CCLTR (rama prevista: `main`).
