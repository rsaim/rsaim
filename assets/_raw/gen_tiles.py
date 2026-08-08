#!/usr/bin/env python3
"""Generate codegraph-style tile SVGs from raw brand logos."""
import base64
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

BG_FILL = '#f7f6f2'
BG_STROKE = '#d6d3c8'
TEXT_FILL = '#16150f'
LOGO_BOX = 44        # max logo edge
LOGO_TOP_Y = 18      # top of logo area
TEXT_Y = 88

def read_svg(path):
    with open(path, 'r', encoding='utf-8') as f:
        s = f.read()
    s = re.sub(r'<\?xml[^>]*\?>', '', s)
    s = re.sub(r'<!DOCTYPE[^>]*>', '', s)
    s = re.sub(r'<!--.*?-->', '', s, flags=re.DOTALL)
    m = re.search(r'<svg\b([^>]*)>(.*)</svg\s*>', s, re.DOTALL | re.IGNORECASE)
    if not m:
        raise ValueError(f'no <svg> found in {path}')
    attrs, inner = m.group(1), m.group(2)
    # strip inner <title>
    inner = re.sub(r'<title[^>]*>.*?</title>', '', inner, flags=re.DOTALL | re.IGNORECASE)
    vb = re.search(r'viewBox\s*=\s*"([^"]+)"', attrs)
    if vb:
        parts = [float(x) for x in vb.group(1).replace(',', ' ').split()]
        x, y, w, h = parts
    else:
        def num(name, default):
            m2 = re.search(name + r'\s*=\s*"([\d.]+)', attrs)
            return float(m2.group(1)) if m2 else default
        x, y = 0, 0
        w, h = num('width', 24), num('height', 24)
    return (x, y, w, h), inner.strip()

def make_tile_svg(name, logo_inner_group):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="104" height="104" '
        f'viewBox="0 0 104 104" role="img" aria-label="{name}">\n'
        f'  <title>{name}</title>\n'
        f'  <rect x="0.5" y="0.5" width="103" height="103" rx="8" '
        f'fill="{BG_FILL}" stroke="{BG_STROKE}"/>\n'
        f'  {logo_inner_group}\n'
        f'  <text x="52" y="{TEXT_Y}" text-anchor="middle" '
        f'font-family="-apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, '
        f'\'Helvetica Neue\', Arial, sans-serif" '
        f'font-size="12" font-weight="600" fill="{TEXT_FILL}">{name}</text>\n'
        f'</svg>\n'
    )

def make_tile(src_path, name, out_path):
    if src_path.lower().endswith('.png'):
        with open(src_path, 'rb') as f:
            b64 = base64.b64encode(f.read()).decode('ascii')
        inner = (
            f'<image href="data:image/png;base64,{b64}" '
            f'x="30" y="{LOGO_TOP_Y}" width="{LOGO_BOX}" height="{LOGO_BOX}" '
            f'preserveAspectRatio="xMidYMid meet"/>'
        )
    else:
        (x, y, w, h), inner_content = read_svg(src_path)
        scale = LOGO_BOX / max(w, h)
        sw, sh = w * scale, h * scale
        tx = (104 - sw) / 2 - x * scale
        ty = LOGO_TOP_Y + (LOGO_BOX - sh) / 2 - y * scale
        inner = (
            f'<g transform="translate({tx:.3f},{ty:.3f}) scale({scale:.4f})">'
            f'{inner_content}</g>'
        )
    svg = make_tile_svg(name, inner)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f'wrote {out_path}')

def find_src(dir_, slug):
    for ext in ('.svg', '.png'):
        p = os.path.join(dir_, slug + ext)
        if os.path.exists(p):
            return p
    raise FileNotFoundError(f'{dir_}/{slug}.*')

# Language additions
lang_add = {'bash': 'Bash', 'sql': 'SQL'}
for slug, name in lang_add.items():
    src = find_src(os.path.join(ROOT, '_raw/lang'), slug)
    make_tile(src, name, os.path.join(ROOT, 'languages', f'{slug}.svg'))

ai_map = {
    'anthropic': 'Anthropic', 'openai': 'OpenAI', 'vertexai': 'Vertex AI',
    'langchain': 'LangChain', 'langgraph': 'LangGraph', 'langsmith': 'LangSmith',
    'huggingface': 'Hugging Face', 'pinecone': 'Pinecone', 'faiss': 'FAISS',
    'weaviate': 'Weaviate', 'pytorch': 'PyTorch', 'tensorflow': 'TensorFlow',
}
for slug, name in ai_map.items():
    src = find_src(os.path.join(ROOT, '_raw/ai'), slug)
    make_tile(src, name, os.path.join(ROOT, 'ai', f'{slug}.svg'))

infra_map = {
    'azure': 'Azure', 'gcp': 'GCP', 'aws': 'AWS', 'kubernetes': 'Kubernetes',
    'docker': 'Docker', 'terraform': 'Terraform', 'jenkins': 'Jenkins',
    'spinnaker': 'Spinnaker', 'grafana': 'Grafana', 'kafka': 'Kafka',
    'postgresql': 'PostgreSQL', 'mongodb': 'MongoDB', 'mysql': 'MySQL',
    'redis': 'Redis', 'dynamodb': 'DynamoDB', 'bigquery': 'BigQuery',
    'linux': 'Linux',
}
for slug, name in infra_map.items():
    src = find_src(os.path.join(ROOT, '_raw/infra'), slug)
    make_tile(src, name, os.path.join(ROOT, 'infra', f'{slug}.svg'))
