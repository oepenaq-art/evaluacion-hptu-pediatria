# -*- coding: utf-8 -*-
with open('app.js', 'r', encoding='utf-8') as f:
    js = f.read()
import re

# Fix calculateResults saving
js = js.replace('residente_id: resSel.value,', 'residente_id: selectedResidentId,')

# Find the mistakenly injected init code inside calculateResults
wrong_init = """        activeRubric.forEach(cat => {
            cat.items.forEach(item => {
            if (activeRubric === rubricMiniCex) {
                itemSelections[item.id] = { level: 'minicex', value: (5/9)*5, raw: 5 };
            }
                const sel = itemSelections[item.id];"""
correct_init = """        activeRubric.forEach(cat => {
            cat.items.forEach(item => {
                const sel = itemSelections[item.id];"""
js = js.replace(wrong_init, correct_init)

# Now, we need to correctly initialize the itemSelections for MiniCEX inside renderRubric!
# Let's find renderRubric
# wait, what if I just initialize them when selectResidentForEval is called?
# Yes! Let's just do it in selectResidentForEval or renderRubric.

init_in_render = """function renderRubric() {
    const container = document.getElementById('rubric-container');
    container.innerHTML = '';
    const activeRubric = getCurrentRubric(document.getElementById('evaluation-type').value);
    
    // Initialize minicex slider defaults
    if (activeRubric === rubricMiniCex) {
        activeRubric.forEach(cat => cat.items.forEach(item => {
            itemSelections[item.id] = { level: 'minicex', value: (5/9)*5, raw: 5 };
        }));
    }"""
js = re.sub(r'function renderRubric\(\) \{[\s\S]*?const activeRubric = getCurrentRubric.*?;\n', init_in_render + '\n', js)

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("app.js save and initialization fixed.")
