# -*- coding: utf-8 -*-
import re

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

old_select = re.search(r'<select id="evaluation-type".*?</select>', text, re.DOTALL).group(0)

new_select = """<select id="evaluation-type" required onchange="handleEvaluationTypeChange()">
                    <option value="ronda" id="opt-ronda">Ronda Médica (60%)</option>
                    <option value="seminario" id="opt-seminario">Seminario (40%)</option>
                    <option value="minicex" id="opt-minicex" class="hidden">MiniCEX (20%)</option>
                    <option value="tema_central" id="opt-tema-central" class="hidden">Tema Central (20%)</option>
                </select>"""

text = text.replace(old_select, new_select)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print('index.html updated successfully!')
