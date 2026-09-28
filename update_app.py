import re

with open('app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Add "Infectología pediátrica" to subjectsYear1
if '"Infectología pediátrica"' not in js:
    js = re.sub(r'const subjectsYear1 = \[(.*?)\];', r'const subjectsYear1 = [\1, "Infectología pediátrica"];', js, flags=re.DOTALL)

# 2. Add microcurriculo
micro = "    \"Infectología pediátrica\": \"1. Reconoce la epidemiología, historia natural y fisiopatología de infecciones.\\n2. Describe herramientas diagnósticas.\\n3. Conoce principios de manejo farmacológico y uso de antibiograma.\\n4. Conoce el uso racional de antibióticos y desescalonamiento.\\n5. Conoce principios de resistencia antimicrobiana.\\n6. Realiza educación sobre el uso responsable de antibióticos.\",\n"
if '"Infectología pediátrica":' not in js:
    js = js.replace('const MICROCURRICULOS = {', 'const MICROCURRICULOS = {\n' + micro)

# 3. Add rubricMiniCex
rubric_minicex = """
const rubricMiniCex = [
    {
        category: "Mini-CEX (Escala de 1 a 9)",
        items: [
            { id: "mc_anamnesis", title: "1. Anamnesis del paciente y/o acudiente", desc: "Facilita la narración del paciente y/o acudiente. Utiliza preguntas adecuadas de manera eficaz. Realiza un interrogatorio completo del motivo de consulta, enfermedad actual y antecedentes. Responde adecuadamente a mensajes claves verbales y no verbales.", weight: 1/8 },
            { id: "mc_examen", title: "2. Examen físico del paciente", desc: "Sigue una secuencia lógica y eficiente céfalo caudal. Exploración centrada en el problema clínico. Informa al paciente. Respeta la comodidad del paciente.", weight: 1/8 },
            { id: "mc_juicio", title: "3. Juicio clínico, análisis y diagnósticos", desc: "Realiza un diagnóstico apropiado y tiene en cuenta los diagnósticos diferenciales. Analiza de forma apropiada y crítica los diagnósticos.", weight: 1/8 },
            { id: "mc_plan", title: "4. Plan de manejo", desc: "Establece un plan terapéutico acorde al diagnóstico. Propone ayudas diagnósticas pertinentes y completas, considerando los riesgos y beneficios.", weight: 1/8 },
            { id: "mc_comunicacion", title: "5. Habilidades comunicativas", desc: "Utiliza un lenguaje claro para el paciente. Es empático. Es honesto y pertinente. Explica al paciente el diagnóstico y el plan. Educa al paciente y a su familia.", weight: 1/8 },
            { id: "mc_organizacion", title: "6. Organización / eficiencia", desc: "Prioriza. Se ajusta al tiempo. Es concreto.", weight: 1/8 },
            { id: "mc_profesionalismo", title: "7. Profesionalismo", desc: "Muestra respeto por el paciente y su familia. Establece confianza y una buena relación. Guarda la confidencialidad de la historia clínica. Considera los aspectos legales relevantes.", weight: 1/8 },
            { id: "mc_evaluacion", title: "8. Evaluación clínica global", desc: "Demuestra de forma satisfactoria el juicio clínico, síntesis y efectividad. Utiliza adecuadamente los recursos. Es consciente de sus propias limitaciones.", weight: 1/8 }
        ]
    }
];
"""
if 'const rubricMiniCex' not in js:
    js = js.replace('const rubricTemaCentral = [', rubric_minicex + '\nconst rubricTemaCentral = [')

# 4. Update selectSubject
select_subj_old = """    if (subject === "Urgencias pediátricas III nivel de fundamentación") {
        optTema.classList.remove('hidden');
    } else if (subject === "Hospitalización pediátrica tercer nivel fundamentación") {
        optMinicex.classList.remove('hidden');
    }"""
select_subj_new = """    if (subject === "Urgencias pediátricas III nivel de fundamentación" || subject === "Hospitalización pediátrica tercer nivel fundamentación") {
        optMinicex.classList.remove('hidden');
    }"""
js = js.replace(select_subj_old, select_subj_new)

# 5. Update getCurrentRubric
get_curr_old = """    if (evalType === 'seminario') return rubricSeminario;
    if (evalType === 'tema_central' || evalType === 'minicex') return rubricTemaCentral;
    return rubricStructure;"""
get_curr_new = """    if (evalType === 'seminario') return rubricSeminario;
    if (evalType === 'minicex') return rubricMiniCex;
    if (evalType === 'tema_central') return rubricTemaCentral;
    return rubricStructure;"""
js = js.replace(get_curr_old, get_curr_new)

# 6. Update renderRubric
render_cat_old = """        catDiv.innerText = cat.category;
        container.appendChild(catDiv);"""
render_cat_new = """        let legendHtml = '';
        if (activeRubric === rubricMiniCex) {
             legendHtml = '<p style="font-size: 0.85rem; font-weight: normal; margin-top: 5px; color: #555;">Califique de 1 a 9 de acuerdo al desempeño de él o la residente, siendo 9 el puntaje más alto.</p>';
        }
        catDiv.innerHTML = cat.category + legendHtml;
        container.appendChild(catDiv);"""
js = js.replace(render_cat_old, render_cat_new)

# Safe replacement for render button
render_btn_old = "const block = document.createElement('div');"
render_btn_target = """                <div class="score-buttons" id="btns-${item.id}">
                    ${SCORE_LEVELS.map(l => `
                        <button type="button" class="score-btn ${l.cls}" id="btn-${item.id}-${l.key}"
                            onclick="selectScore('${item.id}','${l.key}',this)">
                            <strong>${l.label}</strong><br><span style="font-weight:400;font-size:0.72rem;">${l.range}</span>
                        </button>`).join('')}
                </div>"""
render_btn_new = """                <div class="score-buttons" id="btns-${item.id}">
                    ${activeRubric === rubricMiniCex ? 
                        [1,2,3,4,5,6,7,8,9].map(num => `
                            <button type="button" class="score-btn btn-score-${num}" id="btn-${item.id}-${num}"
                                onclick="selectScore('${item.id}','${num}',this)">
                                <strong style="font-size:1.2rem;">${num}</strong>
                            </button>`).join('')
                        :
                        SCORE_LEVELS.map(l => `
                        <button type="button" class="score-btn ${l.cls}" id="btn-${item.id}-${l.key}"
                            onclick="selectScore('${item.id}','${l.key}',this)">
                            <strong>${l.label}</strong><br><span style="font-weight:400;font-size:0.72rem;">${l.range}</span>
                        </button>`).join('')
                    }
                </div>"""
js = js.replace(render_btn_target, render_btn_new)

render_input_old = """                <div class="score-input-row hidden" id="input-row-${item.id}"
                     style="padding:10px 15px;background:#f9fbfd;display:flex;align-items:center;gap:12px;border-top:1px solid #eee;">"""
render_input_new = """                <div class="score-input-row hidden" id="input-row-${item.id}"
                     style="padding:10px 15px;background:#f9fbfd;display:flex;align-items:center;gap:12px;border-top:1px solid #eee; ${activeRubric === rubricMiniCex ? 'display:none!important;' : ''}">"""
js = js.replace(render_input_old, render_input_new)

# 7. Update calculateResults
calc_val_old = """        if (exactInput && exactInput.value) {
            itemScore = parseFloat(exactInput.value.replace(',', '.'));
            if (isNaN(itemScore)) itemScore = 0;
        } else {
            const level = itemSelections[item.id];
            if (level === 'na' || !level) {
                unselected.push(item.title);
                isNa = true;
            } else {
                itemScore = baseValueMap[level];
                selectedLvl = level;
            }
        }"""
calc_val_new = """        if (exactInput && exactInput.value && activeRubric !== rubricMiniCex) {
            itemScore = parseFloat(exactInput.value.replace(',', '.'));
            if (isNaN(itemScore)) itemScore = 0;
        } else {
            const level = itemSelections[item.id];
            if (level === 'na' || !level) {
                unselected.push(item.title);
                isNa = true;
            } else if (activeRubric === rubricMiniCex) {
                itemScore = parseInt(level, 10);
                selectedLvl = level;
            } else {
                itemScore = baseValueMap[level];
                selectedLvl = level;
            }
        }"""
js = js.replace(calc_val_old, calc_val_new)

calc_final_old = """    let finalScoreText = "0.00";
    if (totalWeight > 0) {
        let finalScore = (totalScore / totalWeight);
        if (activeRubric === rubricMiniCex) {
            finalScore = (finalScore / 9.0) * 5.0;
        }
        finalScoreText = finalScore.toFixed(2);
    }"""
if 'finalScore = (finalScore / 9.0) * 5.0;' not in js:
    # it was:
    calc_final_old_2 = """    let finalScoreText = "0.00";
    if (totalWeight > 0) {
        const finalScore = (totalScore / totalWeight);
        finalScoreText = finalScore.toFixed(2);
    }"""
    calc_final_new_2 = """    let finalScoreText = "0.00";
    if (totalWeight > 0) {
        let finalScore = (totalScore / totalWeight);
        if (activeRubric === rubricMiniCex) {
            finalScore = (finalScore / 9.0) * 5.0;
        }
        finalScoreText = finalScore.toFixed(2);
    }"""
    js = js.replace(calc_final_old_2, calc_final_new_2)

# 8. Update generateFinalReport
rep_old = """    if (rotation === "Urgencias pediátricas III nivel de fundamentación" || rotation === "Hospitalización pediátrica tercer nivel fundamentación") {
        if (evalTemaCentral.length > 0 && evalSeminario.length > 0 && evalRonda.length > 0) {
            avgFinalNum = (avgRonda * 0.5) + (avgSeminario * 0.3) + (avgTema * 0.2);
            distribucionNotas = "Ronda Médica 50%, Seminarios 30%, Tema Central/MiniCEX 20%";
        } else if (evalTemaCentral.length === 0 && evalSeminario.length > 0 && evalRonda.length > 0) {
            avgFinalNum = (avgRonda * 0.6) + (avgSeminario * 0.4);
            distribucionNotas = "Ronda Médica 60%, Seminarios 40% (No se evaluó Tema Central/MiniCEX)";
        } else if (evalTemaCentral.length > 0 && evalSeminario.length === 0 && evalRonda.length > 0) {
            avgFinalNum = (avgRonda * 0.7) + (avgTema * 0.3);
            distribucionNotas = "Ronda Médica 70%, Tema Central/MiniCEX 30% (No se evaluaron Seminarios)";
        } else if (evalTemaCentral.length === 0 && evalSeminario.length === 0 && evalRonda.length > 0) {
            avgFinalNum = avgRonda;
            distribucionNotas = "Ronda Médica 100% (No se evaluaron Seminarios ni Tema Central/MiniCEX)";
        } else {
            const total = avgRonda + avgSeminario + avgTema;
            const count = (avgRonda > 0 ? 1 : 0) + (avgSeminario > 0 ? 1 : 0) + (avgTema > 0 ? 1 : 0);
            avgFinalNum = count > 0 ? total / count : 0;
            distribucionNotas = "Promedio ajustado según evaluaciones disponibles.";
        }
    } else {
        if (evalSeminario.length > 0 && evalRonda.length > 0) {
            avgFinalNum = (avgRonda * 0.5) + (avgSeminario * 0.5);
            distribucionNotas = "Ronda Médica 50%, Seminarios 50%";
        } else if (evalSeminario.length === 0 && evalRonda.length > 0) {
            avgFinalNum = avgRonda;
            distribucionNotas = "Ronda Médica 100% (No se evaluaron Seminarios)";
        } else if (evalSeminario.length > 0 && evalRonda.length === 0) {
            avgFinalNum = avgSeminario;
            distribucionNotas = "Seminarios 100% (No se evaluó Ronda Médica)";
        } else {
            avgFinalNum = 0;
            distribucionNotas = "No hay evaluaciones válidas.";
        }
    }"""
rep_new = """    // Global logic for ALL rotations
    if (evalTemaCentral.length > 0 && evalSeminario.length > 0 && evalRonda.length > 0) {
        avgFinalNum = (avgRonda * 0.5) + (avgSeminario * 0.3) + (avgTema * 0.2);
        distribucionNotas = "Ronda Médica 50%, Seminarios 30%, Tema Central/MiniCEX 20%";
    } else if (evalTemaCentral.length === 0 && evalSeminario.length > 0 && evalRonda.length > 0) {
        avgFinalNum = (avgRonda * 0.6) + (avgSeminario * 0.4);
        distribucionNotas = "Ronda Médica 60%, Seminarios 40% (No se evaluó Tema Central/MiniCEX)";
    } else if (evalTemaCentral.length > 0 && evalSeminario.length === 0 && evalRonda.length > 0) {
        avgFinalNum = (avgRonda * 0.7) + (avgTema * 0.3);
        distribucionNotas = "Ronda Médica 70%, Tema Central/MiniCEX 30% (No se evaluaron Seminarios)";
    } else if (evalTemaCentral.length === 0 && evalSeminario.length === 0 && evalRonda.length > 0) {
        avgFinalNum = avgRonda;
        distribucionNotas = "Ronda Médica 100% (No se evaluaron Seminarios ni Tema Central/MiniCEX)";
    } else {
        const total = avgRonda + avgSeminario + avgTema;
        const count = (avgRonda > 0 ? 1 : 0) + (avgSeminario > 0 ? 1 : 0) + (avgTema > 0 ? 1 : 0);
        avgFinalNum = count > 0 ? total / count : 0;
        distribucionNotas = "Promedio ajustado según evaluaciones disponibles.";
    }"""
js = js.replace(rep_old, rep_new)

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("Modifications done.")
