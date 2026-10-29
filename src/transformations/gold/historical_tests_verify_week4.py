"""Verificación de entrega sin Spark ni datos transaccionales: python tests/verify_week4.py."""
import ast
import csv
import json
import re
from pathlib import Path

root=Path(__file__).resolve().parents[1]
for name in ['eda_por_fecha','eda_por_sucursal']:
    with (root/f'reports/week4/{name}.csv').open(encoding='utf-8-sig') as f:
        rows=list(csv.DictReader(f))
    assert sum(int(r['tickets']) for r in rows)==2142846, name
    assert sum(int(r['tickets_con_descuento']) for r in rows)==268590, name
    for r in rows:
        assert abs(float(r['proporcion_con_descuento'])-int(r['tickets_con_descuento'])/int(r['tickets']))<1e-10
with (root/'reports/week4/catalogo_descuentos.csv').open(encoding='utf-8-sig') as f:
    rows=list(csv.DictReader(f))
assert len(rows)==106 and len({r['DiscountId'] for r in rows})==106
for p in (root/'notebooks/import').glob('*.ipynb'):
    nb=json.loads(p.read_text(encoding='utf-8'))
    assert nb['nbformat']==4
    for cell in nb['cells']:
        if cell['cell_type']=='code':
            ast.parse(''.join(cell['source']))
            assert cell['outputs']==[] and cell['execution_count'] is None
for p in (root/'docs').rglob('*.md'):
    for link in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
        if '://' not in link and not link.startswith('#'):
            assert (p.parent/link.split('#')[0]).exists(), (p,link)
print('OK: totales, proporciones, catálogo, celdas IPYNB y enlaces de documentación.')
