#!/usr/bin/env python3
"""Exporta únicamente las operaciones registradas de Rama B; no exporta indicadores."""
import json
from pathlib import Path

base = Path('Test/debate-0988/resultados')
source = base / 'debate-0988_expediente.json'
if not source.is_file():
    raise SystemExit(f'No se encontró {source}. Ejecutá desde la raíz de CCLTR.')
data = json.loads(source.read_text(encoding='utf-8'))

# Priorizar el registro de ejecución, no la lista de operaciones posibles.
def find_logs(obj, path='raiz'):
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f'{path}.{k}'
            if k in ('transformaciones', 'operaciones_ejecutadas', 'registro_operaciones') and isinstance(v, list):
                if any(isinstance(x, dict) and ('operacion' in x or 'propuesta' in x) for x in v):
                    yield p, v
            yield from find_logs(v, p)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, (dict, list)):
                yield from find_logs(v, f'{path}[{i}]')

logs = list(find_logs(data))
logs.sort(key=lambda x: (('rama_b' not in x[0].lower()), -len(x[1])))
if not logs:
    raise SystemExit('No encontré un registro de operaciones en el expediente. No se generó un informe incompleto.')
path, entries = logs[0]
operations = [e for e in entries if isinstance(e, dict) and e.get('estado', 'ejecutada') == 'ejecutada']
if not operations:
    raise SystemExit(f'Hay un registro en {path}, pero no contiene operaciones ejecutadas.')

out = base / 'debate-0988_operaciones_rama_b.md'
raw = base / 'debate-0988_operaciones_rama_b.json'
raw.write_text(json.dumps({'fuente':str(source),'ruta_registro':path,'operaciones':operations}, ensure_ascii=False, indent=2), encoding='utf-8')
lines = ['# Debate 0988 — operaciones ejecutadas en Rama B', '',
         f'Fuente: `{source}`', f'Registro: `{path}`',
         f'Operaciones registradas: **{len(operations)}**', '',
         'Este documento excluye los indicadores y las mediciones de diversidad.', '']
for i, e in enumerate(operations, 1):
    proposal = e.get('propuesta', e)
    op = proposal.get('operacion', e.get('operacion', 'sin especificar'))
    lines.extend([f'## {i}. {op}', '',
                  f'- Estado: {e.get("estado", "no indicado")}',
                  f'- Secuencia: {e.get("secuencia", i)}', '',
                  '```json', json.dumps(e, ensure_ascii=False, indent=2), '```', ''])
out.write_text('\n'.join(lines), encoding='utf-8')
print('Registro:', path)
print('Operaciones exportadas:', len(operations))
print('Archivos:', out, 'y', raw)
