# -*- coding: utf-8 -*-
import re

with open('app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Firebase Collections
js = js.replace("'residentes'", "'residentes_hptu'")
js = js.replace("'evaluaciones'", "'evaluaciones_hptu'")

# 2. Auth state -> go to step-main-menu
js = js.replace("showStep('step-residents-grid');\n        loadResidentsGrid();", "showStep('step-main-menu');")

# 3. Add year to admin resident logic
js = js.replace("const photoInput = document.getElementById('new-res-photo');", "const photoInput = document.getElementById('new-res-photo');\n    const yearInput = parseInt(document.getElementById('new-res-year').value);")
js = js.replace("nombre: nameInput,", "nombre: nameInput,\n            year: yearInput,")

# 4. In loadResidentsGrid, we need to pass the year to selectResidentForEval
js = js.replace("selectResidentForEval(doc.id, data.nombre, photo)", "selectResidentForEval(doc.id, data.nombre, photo, data.year)")
# also add the year to the UI so it looks nice
js = js.replace("<h4 style=\"margin: 0; color: #333; font-size: 0.95rem;\">${data.nombre}</h4>", "<h4 style=\"margin: 0; color: #333; font-size: 0.95rem;\">${data.nombre}</h4><p style=\"margin: 5px 0 0; font-size: 0.8rem; color: #666;\">Año ${data.year}</p>")

# 5. selectResidentForEval needs to handle the logic based on Year
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
    
    // Setup dropdown options
    const evalTypeSelect = document.getElementById('evaluation-type');
    evalTypeSelect.value = 'ronda';
    
    const optTema = document.getElementById('opt-tema-central');
    const optMinicex = document.getElementById('opt-minicex');
    const optRevistas = document.getElementById('opt-club-revistas');
    const optEdu = document.getElementById('opt-actividad-educativa');
    const optRonda = evalTypeSelect.querySelector('option[value="ronda"]');
    const optSeminario = evalTypeSelect.querySelector('option[value="seminario"]');
    
    if (selectedResidentYear === 3) {
        optMinicex.classList.add('hidden');
        optTema.classList.remove('hidden');
        optRevistas.classList.remove('hidden');
        optEdu.classList.remove('hidden');
        
        if(optRonda) optRonda.innerText = 'Práctica / Ronda (40%)';
        if(optSeminario) optSeminario.innerText = 'Evaluación Oral / Seminario (30%)';
    } else {
        optMinicex.classList.remove('hidden');
        optTema.classList.add('hidden');
        optRevistas.classList.add('hidden');
        optEdu.classList.add('hidden');
        
        if(optRonda) optRonda.innerText = 'Ronda Médica (50%)';
        if(optSeminario) optSeminario.innerText = 'Seminario (30%)';
    }
    
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

js = re.sub(r'async function selectResidentForEval[\s\S]*?loadTeachers\(subject\);\n\}', new_select_resident, js)
# Wait, handleRotationChange was injected in previous step, so let's remove it because it's no longer needed
js = re.sub(r'async function handleRotationChange\(\) \{[\s\S]*?loadTeachers\(subject\);\n\}', '', js)
# Remove old selectResidentForEval block completely
js = re.sub(r'async function selectResidentForEval[\s\S]*?showStep\(\'step-form\'\);\n\}', new_select_resident, js)

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("app.js logic updated.")
