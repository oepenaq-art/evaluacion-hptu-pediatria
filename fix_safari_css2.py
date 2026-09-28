import re

with open('styles.css.backup', 'r', encoding='utf-8') as f:
    css = f.read()

# We need to remove "gap: Xpx;" from the CSS except for grid, but it's easier to just remove it and use margins.
# Let's use regex to find and remove gap.

# Wait, grid uses gap safely in older Safari! (Grid gap is supported since iOS 10.3). Flex gap is supported since iOS 14.5.
# .options-grid uses grid.
css = re.sub(r'(?<!grid-template-columns: repeat\(auto-fit, minmax\(200px, 1fr\)\); )gap:\s*\d+px;', '', css)

safari_fixes = """
/* ========================================================
   COMPATIBILIDAD MÓVIL Y SAFARI (SOPORTE FLEX GAP)
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
    
    /* Asegurar que los botones ocupen el ancho y no se superpongan */
    .score-buttons .score-btn { width: 100%; margin-bottom: 8px; }
    .score-buttons > * + * { margin-top: 0; }
}
"""

# Let's do a hard replace of gap everywhere except the grid one
css = css.replace('gap: 15px;', '')
css = css.replace('gap: 10px;', '')
css = css.replace('gap: 6px;', '')
css = css.replace('gap: 20px;', '')
css = css.replace('gap: 5px;', '')
css = css.replace('gap: 8px;', '')

# restore the grid gap
css = css.replace('.options-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));  }', '.options-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }')

css += safari_fixes

with open('styles.css', 'w', encoding='utf-8') as f:
    f.write(css)

print("styles.css cleaned from gap and added safe margins.")
