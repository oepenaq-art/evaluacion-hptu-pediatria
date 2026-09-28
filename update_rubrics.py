# -*- coding: utf-8 -*-
import re

with open('app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Update selectResidentForEval (Revert dropdown to 50/30/20 for everyone)
new_select_resident = """
let selectedResidentYear = 1;

async function selectResidentForEval(resId, resName, resPhoto, resYear) {
    selectedResidentId = resId;
    selectedResidentYear = resYear || 1;
    
    const photoEl = document.getElementById('form-resident-photo');
    if (resPhoto) {
        photoEl.src = resPhoto;
        photoEl.style.display = 'block';
    } else {
        photoEl.style.display = 'none';
    }
    document.getElementById('form-resident-name').innerText = resName;
    
    // Set explicit subject based on year
    if (selectedResidentYear === 3) {
        selectedSubjectName = "Hospitalización pediátrica III nivel profundización";
    } else {
        selectedSubjectName = "Hospitalización pediátrica III nivel fundamentación";
    }
    
    // Setup dropdown options (Todos con 50/30/20)
    const evalTypeSelect = document.getElementById('evaluation-type');
    evalTypeSelect.value = 'ronda';
    
    const optTema = document.getElementById('opt-tema-central');
    const optMinicex = document.getElementById('opt-minicex');
    const optRevistas = document.getElementById('opt-club-revistas');
    const optEdu = document.getElementById('opt-actividad-educativa');
    const optRonda = evalTypeSelect.querySelector('option[value="ronda"]');
    const optSeminario = evalTypeSelect.querySelector('option[value="seminario"]');
    
    optMinicex.classList.remove('hidden');
    if(optTema) optTema.classList.add('hidden');
    if(optRevistas) optRevistas.classList.add('hidden');
    if(optEdu) optEdu.classList.add('hidden');
    
    if(optRonda) optRonda.innerText = 'Ronda Médica (50%)';
    if(optSeminario) optSeminario.innerText = 'Seminario (30%)';
    
    Object.keys(itemSelections).forEach(k => delete itemSelections[k]);
    document.querySelectorAll('.score-btn').forEach(b => b.classList.remove('selected'));
    document.querySelectorAll('.score-input-row').forEach(r => { r.classList.add('hidden'); r.style.display = 'none'; });
    
    handleEvaluationTypeChange();
    
    document.getElementById('eval-date').value = new Date().toISOString().split('T')[0];
    document.getElementById('eval-teacher').value = '';
    document.getElementById('eval-fortalezas').value = '';
    document.getElementById('eval-mejoras').value = '';
    
    showStep('step-form');
    await loadTeachers(selectedSubjectName);
}
"""
js = re.sub(r'let selectedResidentYear = 1;\s*async function selectResidentForEval[\s\S]*?loadTeachers\(selectedSubjectName\);\n\}', new_select_resident, js)

# 2. Add Year 3 Advanced Rubrics
adv_rubrics = """
const rubricStructureYear3 = [
    {
        category: "Conocimientos académicos",
        items: [
            { id: "rm_c_academico_y3", title: "Conocimientos y aprendizaje", desc: "Demuestra dominio experto de la literatura reciente, guías de manejo y aplica pensamiento crítico para resolver casos complejos.", weight: 0.25 }
        ]
    },
    {
        category: "Competencias clínicas",
        items: [
            { id: "rm_c_anamnesis_y3", title: "Anamnesis", desc: "Realiza anamnesis exhaustiva, identificando sutiles determinantes sociales y correlacionando hallazgos complejos con la fisiopatología.", weight: 0.10 },
            { id: "rm_c_fisico_y3", title: "Examen físico", desc: "Dirige el examen físico a hallazgos avanzados, reconociendo signos clínicos atípicos y sutilezas semiológicas.", weight: 0.10 },
            { id: "rm_c_analisis_y3", title: "Análisis y síntesis", desc: "Elabora diagnósticos diferenciales complejos, justificando cada uno con evidencia sólida y un raciocinio fisiopatológico impecable.", weight: 0.15 },
            { id: "rm_c_plan_y3", title: "Plan de manejo", desc: "Diseña planes de manejo integrales y costo-efectivos, liderando al equipo multidisciplinario y anticipando complicaciones.", weight: 0.15 }
        ]
    },
    {
        category: "Habilidades de comunicación y Profesionalismo",
        items: [
            { id: "rm_c_comunicacion_y3", title: "Comunicación y trabajo en equipo", desc: "Se comunica de forma asertiva y empática en situaciones difíciles, transmitiendo información compleja con claridad y liderando el equipo.", weight: 0.10 },
            { id: "rm_c_profesionalismo_y3", title: "Profesionalismo", desc: "Lidera con el ejemplo ético, asumiendo responsabilidad absoluta sobre sus pacientes y orientando a los residentes de menor año.", weight: 0.15 }
        ]
    }
];

const rubricSeminarioYear3 = [
    {
        category: "Seminario / Actividad Académica (Nivel Profundización)",
        items: [
            { id: "sem_dominio_y3", title: "Dominio del tema y evidencia", desc: "Dominio absoluto del tema, integrando conceptos moleculares, fisiopatológicos y clínicos avanzados con evidencia actual.", weight: 0.40 },
            { id: "sem_analisis_y3", title: "Análisis crítico", desc: "Critica constructivamente la literatura existente, proponiendo nuevas perspectivas o áreas de incertidumbre clínica.", weight: 0.30 },
            { id: "sem_pedagogia_y3", title: "Habilidades pedagógicas", desc: "Lidera la discusión académica estimulando el razonamiento crítico en el auditorio y respondiendo preguntas complejas con solvencia.", weight: 0.20 },
            { id: "sem_tiempo_y3", title: "Manejo del tiempo y síntesis", desc: "Logra una síntesis perfecta, optimizando el tiempo para favorecer el debate de alto nivel.", weight: 0.10 }
        ]
    }
];
"""
if 'rubricStructureYear3' not in js:
    js = js.replace('const rubricSeminario = [', adv_rubrics + '\nconst rubricSeminario = [')

# 3. Update getCurrentRubric to return advanced rubrics for year 3
curr_old = """function getCurrentRubric(evalType) {
    if (evalType === 'seminario') return rubricSeminario;
    if (evalType === 'minicex') return rubricMiniCex;
    if (evalType === 'tema_central') return rubricTemaCentral;
    return rubricStructure;
}"""
curr_new = """function getCurrentRubric(evalType) {
    if (evalType === 'seminario') return selectedResidentYear === 3 ? rubricSeminarioYear3 : rubricSeminario;
    if (evalType === 'minicex') return rubricMiniCex;
    if (evalType === 'tema_central') return rubricTemaCentral;
    return selectedResidentYear === 3 ? rubricStructureYear3 : rubricStructure;
}"""
js = js.replace(curr_old, curr_new)

# 4. Render Slider for MiniCEX
render_btn_target = r"\$\{activeRubric === rubricMiniCex \?[\s\S]*?join\(\'\'\)[\s\S]*?join\(\'\'\)[\s\S]*?\}"
slider_html = """${activeRubric === rubricMiniCex ? `
                        <div style="display:flex; align-items:center; gap: 15px; width: 100%; margin-top: 15px; padding: 0 10px;">
                            <span style="font-weight:bold; font-size:1.2rem; color: #d32f2f;">1</span>
                            <input type="range" min="1" max="9" value="5" class="minicex-slider" id="slider-${item.id}"
                                oninput="document.getElementById('slider-val-${item.id}').innerText = this.value; selectScore('${item.id}', this.value, this)"
                                style="flex-grow:1; cursor:pointer; height: 8px; border-radius: 4px; background: #ddd; outline: none;">
                            <span style="font-weight:bold; font-size:1.2rem; color: #43a047;">9</span>
                            <div style="background:var(--primary-color); color:white; border-radius:50%; width:40px; height:40px; display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:1.3rem; margin-left:10px;" id="slider-val-${item.id}">5</div>
                        </div>` 
                        :
                        SCORE_LEVELS.map(l => `
                        <button type="button" class="score-btn ${l.cls}" id="btn-${item.id}-${l.key}"
                            onclick="selectScore('${item.id}','${l.key}',this)">
                            <strong>${l.label}</strong><br><span style="font-weight:400;font-size:0.72rem;">${l.range}</span>
                        </button>`).join('')
                    }"""
js = re.sub(render_btn_target, slider_html, js)

# We need to initialize the slider value in itemSelections when rendering MiniCEX
init_slider_old = """        cat.items.forEach(item => {"""
init_slider_new = """        cat.items.forEach(item => {
            if (activeRubric === rubricMiniCex) {
                itemSelections[item.id] = "5"; // Default slider value
            }"""
js = js.replace(init_slider_old, init_slider_new)

# 5. Fix Word Report weighted average logic to universally use 50/30/20!
word_avg_old = r"let notaPonderadaTexto = \"No se pudo calcular el ponderado por falta de datos\.\";[\s\S]*?paragraphs\.push\(new Paragraph\(\{ children: \[new TextRun\(\{ text: notaPonderadaTexto"
word_avg_new = """let notaPonderadaTexto = "No se pudo calcular el ponderado por falta de datos.";
        
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
        
        paragraphs.push(new Paragraph({ children: [new TextRun({ text: notaPonderadaTexto"""
js = re.sub(word_avg_old, word_avg_new, js)

# Also fix searchEvaluations fallback weighted average logic string (display only)
js = js.replace("avgFinalNum = (avgRonda * 0.5) + (avgSeminario * 0.3) + (avgTema * 0.2);", "avgFinalNum = (avgRonda * 0.5) + (avgSeminario * 0.3) + (avgMinicex * 0.2);")

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("app.js logic updated for advanced rubrics and sliders.")
