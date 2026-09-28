# -*- coding: utf-8 -*-
with open('app.js', 'r', encoding='utf-8') as f:
    js = f.read()

import re

# 1. Provide a custom selectScore for MiniCex
minicex_score_func = """
function selectScoreMiniCex(itemId, val) {
    const score9 = parseFloat(val);
    const score5 = (score9 / 9.0) * 5.0; // Convierte a escala de 5.0
    itemSelections[itemId] = { level: 'minicex', value: score5, raw: score9 };
}
"""
js = js.replace("function selectScore(itemId, levelKey, btnEl) {", minicex_score_func + "\nfunction selectScore(itemId, levelKey, btnEl) {")

# 2. Update renderRubric to use selectScoreMiniCex
# Wait, I already added the slider. Let's find it and replace the oninput event.
old_slider_html = "selectScore('${item.id}', this.value, this)"
new_slider_html = "selectScoreMiniCex('${item.id}', this.value)"
js = js.replace(old_slider_html, new_slider_html)

# 3. Ensure initialization uses the same struct for MiniCEX
js = js.replace("itemSelections[item.id] = \"5\"; // Default slider value", "itemSelections[item.id] = { level: 'minicex', value: (5/9)*5, raw: 5 };")

# 4. In calculateResults, we don't have `#resident-select` anymore, we use `selectedResidentId` and `document.getElementById('form-resident-name').innerText`.
# Let's fix that.
old_res_sel = """const resSel = document.getElementById('resident-select');
    const eticosNode = document.querySelector('input[name="eticos"]:checked');
    const eticosVal = eticosNode ? eticosNode.value : 'NO';
    const fortalezas = document.getElementById('fortalezas').value;
    const mejoras = document.getElementById('mejoras').value;
    const residentName = resSel.options[resSel.selectedIndex].text;"""
    
new_res_sel = """const eticosNode = document.querySelector('input[name="eticos"]:checked');
    const eticosVal = eticosNode ? eticosNode.value : 'NO';
    const fortalezas = document.getElementById('eval-fortalezas').value;
    const mejoras = document.getElementById('eval-mejoras').value;
    const residentName = document.getElementById('form-resident-name').innerText;"""

js = js.replace(old_res_sel, new_res_sel)

# Also fix the fallback in loadResidents since it references old inputs
js = js.replace("document.getElementById('fortalezas').value", "document.getElementById('eval-fortalezas').value")
js = js.replace("document.getElementById('mejoras').value", "document.getElementById('eval-mejoras').value")

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("app.js Slider fixes and calculation applied.")
