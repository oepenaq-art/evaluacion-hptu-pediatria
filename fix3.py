import os
import re

with open('app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

# Fix Rotacion: \
app_js = re.sub(r'Rotaci\w*n:\s*\\', 'Rotación: ${rotation}', app_js)
app_js = re.sub(r'Microcurr\w*culo.*:\s*\\', 'Microcurrículo de la rotación (Competencias esperadas): ${microcurriculo || "No especificado."}', app_js)
app_js = re.sub(r'Resumen de notas por \w*tem:\s*\\', 'Resumen de notas por ítem: ${Object.values(itemAverages).map(i => "- " + i.title + ": " + i.avg).join("\\n")}', app_js)
app_js = re.sub(r'Comentarios de Fortalezas.*:\s*\\', 'Comentarios de Fortalezas (debatidos por los docentes): ${fort.join(" | ")}', app_js)
app_js = re.sub(r'Comentarios por Mejorar.*:\s*\\', 'Comentarios por Mejorar (debatidos por los docentes): ${mej.join(" | ")}', app_js)

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)

with open(r'C:\Users\LENOVO\.gemini\antigravity\brain\11705742-ddec-4e19-bc0b-e0e230680f05\codigo_app.md', 'w', encoding='utf-8') as f:
    f.write('# Archivo app.js\n\n```javascript\n' + app_js + '\n```\n')

print("Fixed more literals.")
