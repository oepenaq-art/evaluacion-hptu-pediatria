import os

with open(r'C:\Users\LENOVO\.gemini\antigravity\scratch\evaluacion-pediatria\app.js', 'r', encoding='utf-8') as f:
    app_content = f.read()

# Fix the broken string literals
app_content = app_content.replace('Residente: \\\n', 'Residente: ${resName}\n')
app_content = app_content.replace('Rotación: \\\n', 'Rotación: ${rotation}\n')
app_content = app_content.replace('Nota Promedio Final: \\ / 5.0\n', 'Nota Promedio Final: ${avgFinal} / 5.0\n')
app_content = app_content.replace('Microcurrículo de la rotación (Competencias esperadas): \\\n', 'Microcurrículo de la rotación (Competencias esperadas): ${microcurriculo || "No especificado."}\n')
app_content = app_content.replace('Resumen de notas por ítem: \\\n', 'Resumen de notas por ítem: ${Object.values(itemAverages).map(i => "- " + i.title + ": " + i.avg).join("\\n")}\n')
app_content = app_content.replace('Comentarios de Fortalezas (debatidos por los docentes): \\\n', 'Comentarios de Fortalezas (debatidos por los docentes): ${fort.join(" | ")}\n')
app_content = app_content.replace('Comentarios por Mejorar (debatidos por los docentes): \\', 'Comentarios por Mejorar (debatidos por los docentes): ${mej.join(" | ")}')

app_content = app_content.replace('\\{rotation}', '${rotation}')
app_content = app_content.replace('\\{resName}', '${resName}')
app_content = app_content.replace('\\{q.toUpperCase()}', '${q.toUpperCase()}')
app_content = app_content.replace('\\{avg}', '${avg}')
app_content = app_content.replace('\\{cleanFort.join(". ")}', '${cleanFort.join(". ")}')
app_content = app_content.replace('\\{cleanMej.join(". ")}', '${cleanMej.join(". ")}')
app_content = app_content.replace('e.docentes?.nombre', 'e.docente_nombre')

with open(r'C:\Users\LENOVO\.gemini\antigravity\scratch\evaluacion-pediatria\app.js', 'w', encoding='utf-8') as f:
    f.write(app_content)

print("Fixed app.js literals")
