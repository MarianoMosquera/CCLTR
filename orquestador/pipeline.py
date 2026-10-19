"""CCLTR V1: index syncIALO central claims and export selected argument graphs."""
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import networkx as nx
from huggingface_hub import HfApi, hf_hub_download

REPO = 'DebateLabKIT/syncialo-raw'
KEYWORDS = [
    r'\bartificial intelligence\b', r'\bgenerative ai\b', r'\bgenai\b',
    r'\blarge language models?\b', r'\bllms?\b', r'\bmachine learning\b',
    r'\bdeep learning\b', r'\bneural networks?\b', r'\bchatgpt\b',
    r'\balgorithmic (decision|bias|discrimination)\b', r'\bfacial recognition\b',
    r'\binteligencia artificial\b', r'\baprendizaje autom[aá]tico\b',
]
PATTERNS = [re.compile(k, re.I) for k in KEYWORDS]


def parse_graph(payload):
    """Importar el grafo respetando el formato node-link original."""
    if isinstance(payload, dict):
        if "nodes" in payload and ("links" in payload or "edges" in payload):
            clave = "links" if "links" in payload else "edges"
            return nx.node_link_graph(payload, edges=clave)
        for key in ("graph", "data", "node_link_data"):
            if isinstance(payload.get(key), dict):
                return parse_graph(payload[key])
    raise ValueError("Formato de grafo no reconocido")


def central_claim(graph):
    """Identificar la tesis por su posición terminal en el grafo."""
    roots = [
        n for n in graph.nodes
        if graph.out_degree(n) == 0
    ]
    if len(roots) != 1:
        raise ValueError(
            f"Tesis central ambigua: {len(roots)} nodos terminales"
        )

    node = roots[0]
    attrs = graph.nodes[node]
    claim = attrs.get("claim") or attrs.get("label") or attrs.get("text")

    if not isinstance(claim, str) or not claim.strip():
        raise ValueError("Nodo central sin tesis textual")

    return str(node), claim.strip()


def relevant(text):
    return [p.pattern for p in PATTERNS if p.search(text)]


def run(limit=None, out=Path('datos'), prefix='data/synthetic_corpus-001/'):
    out.mkdir(parents=True, exist_ok=True)
    (out / 'grafos').mkdir(exist_ok=True)
    api = HfApi()
    files = sorted(p for p in api.list_repo_files(repo_id=REPO, repo_type='dataset')
                   if p.startswith(prefix) and p.endswith('.json') and 'node_link_data' in p)
    if limit is not None:
        files = files[:limit]
    index, selected, errors = [], [], []
    for i, path in enumerate(files, 1):
        try:
            local = hf_hub_download(repo_id=REPO, repo_type='dataset', filename=path)
            graph = parse_graph(json.loads(Path(local).read_text(encoding='utf-8')))
            if graph.number_of_nodes() < 2 or graph.number_of_edges() == 0:
                continue
            root, claim = central_claim(graph)
            hits = relevant(claim)
            record = {'id': Path(path).parent.name, 'path': path, 'root_id': root,
                      'tesis': claim, 'nodos': graph.number_of_nodes(),
                      'relaciones': graph.number_of_edges(), 'coincidencias': hits,
                      'fuente': f'https://huggingface.co/datasets/{REPO}/blob/main/{path}'}
            index.append(record)
            if hits:
                selected.append(record)
                # NetworkX exports the original node attributes and edges; no inference.
                export = nx.node_link_data(graph)
                (out / 'grafos' / (record['id'] + '.json')).write_text(
                    json.dumps(export, ensure_ascii=False), encoding='utf-8')
        except Exception as exc:
            errors.append({'path': path, 'error': str(exc)})
        if i % 100 == 0:
            print(f'Procesados {i}/{len(files)}; seleccionados {len(selected)}; errores {len(errors)}', flush=True)
    metadata = {'repositorio': REPO, 'fecha_utc': datetime.now(timezone.utc).isoformat(),
                'archivos_examinados': len(files), 'mapas_indexados': len(index),
                'mapas_ia': len(selected), 'errores': len(errors),
                'metodo': 'coincidencia léxica sobre tesis central; no equivalencia semántica',
                'alcance': prefix, 'limite_prueba': limit}
    for name, obj in [('indice_mapas.json', index), ('mapas_ia.json', selected),
                      ('errores.json', errors), ('resumen.json', metadata)]:
        (out / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=None, help='Número máximo de archivos para prueba')
    parser.add_argument('--prefix', default='data/synthetic_corpus-001/', help='Prefijo del repositorio')
    parser.add_argument('--out', type=Path, default=Path('datos'))
    args = parser.parse_args()
    run(args.limit, args.out, args.prefix)
