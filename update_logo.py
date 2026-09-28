# -*- coding: utf-8 -*-
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('logo-eia.png', 'logo-hptu.png')
html = html.replace('Evaluación Residentes Pediatría EIA', 'Evaluación Residentes Pediatría HPTU')
html = html.replace('Evaluación de Residentes de Pediatría EIA', 'Evaluación de Residentes de Pediatría HPTU')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
