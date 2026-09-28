# -*- coding: utf-8 -*-
with open('app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Add MICROCURRICULO
micro = """
    "Hospitalización pediátrica III nivel profundización": "1. Conoce la fisiopatología, abordaje diagnóstico y terapéutico de patologías intrahospitalarias complejas.\\n2. Establece un plan de manejo de líquidos y electrolitos evitando la sobrecarga.\\n3. Maneja las diferentes formas de administración de oxígeno suplementario.\\n4. Conoce indicaciones y complicaciones de transfusiones de hemoderivados.\\n5. Establece planes de egreso hospitalario.\\n6. Aplica estrategias de manejo en paciente con descompensación aguda (código sepsis, alerta temprana, etc.).",
"""
js = js.replace('const MICROCURRICULOS = {\n', 'const MICROCURRICULOS = {\n' + micro)

# 2. Add Weighted Average to Word Document
# We need to calculate it based on the evaluations.
import re

calc_logic = """
        let notaPonderadaTexto = "No se pudo calcular el ponderado por falta de datos.";
        
        if (rotation === "Hospitalización pediátrica III nivel profundización") {
            // Año 3
            let sumaRonda = 0, countRonda = 0;
            let sumaSeminario = 0, countSeminario = 0;
            let sumaTema = 0, countTema = 0;
            let sumaRevistas = 0, countRevistas = 0;
            let sumaEdu = 0, countEdu = 0;
            
            reportEvaluations.forEach(e => {
                const val = parseFloat(e.nota_final);
                if(isNaN(val)) return;
                
                if (e.tipo_evaluacion === 'ronda') { sumaRonda += val; countRonda++; }
                else if (e.tipo_evaluacion === 'seminario') { sumaSeminario += val; countSeminario++; }
                else if (e.tipo_evaluacion === 'tema_central') { sumaTema += val; countTema++; }
                else if (e.tipo_evaluacion === 'club_revistas') { sumaRevistas += val; countRevistas++; }
                else if (e.tipo_evaluacion === 'actividad_educativa') { sumaEdu += val; countEdu++; }
            });
            
            const promRonda = countRonda > 0 ? sumaRonda / countRonda : 0;
            const promSeminario = countSeminario > 0 ? sumaSeminario / countSeminario : 0;
            const promTema = countTema > 0 ? sumaTema / countTema : 0;
            const promRevistas = countRevistas > 0 ? sumaRevistas / countRevistas : 0;
            const promEdu = countEdu > 0 ? sumaEdu / countEdu : 0;
            
            // Si tiene todas las notas: 40, 30, 10, 10, 10
            let final = 0;
            let totalWeights = 0;
            if (countRonda > 0) { final += promRonda * 0.4; totalWeights += 0.4; }
            if (countSeminario > 0) { final += promSeminario * 0.3; totalWeights += 0.3; }
            if (countTema > 0) { final += promTema * 0.1; totalWeights += 0.1; }
            if (countRevistas > 0) { final += promRevistas * 0.1; totalWeights += 0.1; }
            if (countEdu > 0) { final += promEdu * 0.1; totalWeights += 0.1; }
            
            if (totalWeights > 0) {
                final = final / totalWeights;
                notaPonderadaTexto = `Nota Definitiva Ponderada: ${final.toFixed(2)}`;
            }
        } else {
            // Año 1/2
            let sumaRonda = 0, countRonda = 0;
            let sumaSeminario = 0, countSeminario = 0;
            let sumaMinicex = 0, countMinicex = 0;
            
            reportEvaluations.forEach(e => {
                const val = parseFloat(e.nota_final);
                if(isNaN(val)) return;
                
                if (e.tipo_evaluacion === 'ronda') { sumaRonda += val; countRonda++; }
                else if (e.tipo_evaluacion === 'seminario') { sumaSeminario += val; countSeminario++; }
                else if (e.tipo_evaluacion === 'minicex') { sumaMinicex += val; countMinicex++; }
            });
            
            const promRonda = countRonda > 0 ? sumaRonda / countRonda : 0;
            const promSeminario = countSeminario > 0 ? sumaSeminario / countSeminario : 0;
            const promMinicex = countMinicex > 0 ? sumaMinicex / countMinicex : 0;
            
            let final = 0;
            let totalWeights = 0;
            if (countRonda > 0) { final += promRonda * 0.5; totalWeights += 0.5; }
            if (countSeminario > 0) { final += promSeminario * 0.3; totalWeights += 0.3; }
            if (countMinicex > 0) { final += promMinicex * 0.2; totalWeights += 0.2; }
            
            if (totalWeights > 0) {
                final = final / totalWeights;
                notaPonderadaTexto = `Nota Definitiva Ponderada: ${final.toFixed(2)}`;
            }
        }
        
        paragraphs.push(new Paragraph({ children: [new TextRun({ text: notaPonderadaTexto, bold: true, size: 28 })], spacing: { before: 200, after: 300 } }));
"""

# Insert calc_logic before the individual evaluations breakdown
match = re.search(r'paragraphs\.push\(new Paragraph\(\{ text: \'1\. Desglose de Evaluaciones Individuales\'', js)
if match:
    js = js[:match.start()] + calc_logic + match.group(0) + js[match.end():]

# Make sure submitEvaluation includes rotation!
js = js.replace("const rotation = document.getElementById('rotation-select').value;", "const rotation = selectedSubjectName;")


with open('app.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("app.js final logic injected.")
