import re

with open('styles.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Make a backup
with open('styles.css.backup', 'w', encoding='utf-8') as f:
    f.write(css)

# We will add fallback margins for older Safari while keeping gap for modern browsers.
# Actually, the safest cross-browser way (since flex gap support is the only major issue)
# is to use the lobotomized owl selector or just sibling selectors!

safari_fixes = """
/* ========================================================
   COMPATIBILIDAD SAFARI ANTIGUO (iOS < 14.5)
   Reemplazo de 'gap' en flexbox
   ======================================================== */
.options-list > * + * { margin-top: 10px; }
.form-row > * + * { margin-left: 20px; }
.rubric-legend > * { margin-right: 8px; margin-bottom: 8px; }
.score-buttons > * + * { margin-left: 6px; }
.radio-group > * + * { margin-left: 20px; }
.radio-group label > * + * { margin-left: 8px; }

@media (max-width: 768px) {
    .form-row > * + * { margin-left: 0; margin-top: 15px; }
    .score-buttons > * + * { margin-left: 0; margin-top: 8px; }
    .rubric-item-header > * + * { margin-left: 0; margin-top: 5px; }
    .score-input-row > * + * { margin-left: 0; margin-top: 8px; }
    .rubric-item-header { flex-direction: column; align-items: flex-start; }
    .score-buttons { flex-direction: column; align-items: stretch; }
    .form-row { flex-direction: column; }
}
"""

if 'COMPATIBILIDAD SAFARI ANTIGUO' not in css:
    with open('styles.css', 'a', encoding='utf-8') as f:
        f.write("\n" + safari_fixes)

print("styles.css updated for Safari compatibility.")
