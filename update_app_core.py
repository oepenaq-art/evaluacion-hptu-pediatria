# -*- coding: utf-8 -*-
import re

with open('app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Add Storage
if 'firebase.storage()' not in js:
    js = js.replace('const functions = firebase.functions();', 'const functions = firebase.functions();\nconst storage = firebase.storage();')

# 2. Update Auth (Everyone is a coordinator)
auth_old = r"if \(userDoc\.exists\) \{[\s\S]*?\} else \{[\s\S]*?\}"
js = re.sub(auth_old, "currentUser.nombre = userDoc.exists ? (userDoc.data().nombre || user.email) : user.email;\n                userRole = 'coordinador';", js)
js = js.replace("showStep('step-year');", "showStep('step-residents-grid');\n        loadResidentsGrid();")
js = js.replace("document.getElementById('admin-residents-btn')?.classList.remove('hidden');", "") # cleanup if any
js = js.replace("document.getElementById('coord-btn')?.classList.remove('hidden');", "document.getElementById('coord-btn')?.classList.remove('hidden');\n            document.getElementById('admin-residents-btn')?.classList.remove('hidden');")

# 3. Add handleRotationChange to fill dynamic dropdowns
new_funcs = """
async function handleRotationChange() {
    const subject = document.getElementById('rotation-select').value;
    selectedSubjectName = subject;
    Object.keys(itemSelections).forEach(k => delete itemSelections[k]);
    document.querySelectorAll('.score-btn').forEach(b => b.classList.remove('selected'));
    document.querySelectorAll('.score-input-row').forEach(r => { r.classList.add('hidden'); r.style.display = 'none'; });
    
    const evalTypeSelect = document.getElementById('evaluation-type');
    evalTypeSelect.value = 'ronda';
    
    const optTema = document.getElementById('opt-tema-central');
    const optMinicex = document.getElementById('opt-minicex');
    const optRonda = evalTypeSelect.querySelector('option[value="ronda"]');
    const optSeminario = evalTypeSelect.querySelector('option[value="seminario"]');
    
    if (subject.includes("Urgencias") || subject.includes("Hospitalizaci")) {
        optMinicex.classList.remove('hidden');
        optTema.classList.add('hidden');
        if(optRonda) optRonda.innerText = 'Ronda Médica (50%)';
        if(optSeminario) optSeminario.innerText = 'Seminario (30%)';
    } else {
        optTema.classList.add('hidden');
        optMinicex.classList.add('hidden');
        if(optRonda) optRonda.innerText = 'Ronda Médica (60%)';
        if(optSeminario) optSeminario.innerText = 'Seminario (40%)';
    }
    
    handleEvaluationTypeChange();
    await loadTeachers(subject);
}
"""
if 'handleRotationChange()' not in js:
    js = js + new_funcs

# 4. Remove old selectSubject and loadResidents, replace with new logic
# We'll just replace the whole block by finding function selectYear
js = re.sub(r'function selectYear\(year\) \{[\s\S]*?function renderSubjects\(\) \{[\s\S]*?async function selectSubject\(subject\) \{[\s\S]*?showStep\(\'step-form\'\);\n\}', '', js)
js = re.sub(r'async function loadResidents\(\) \{[\s\S]*?sel\.add.*?\} catch.*?\n\}', '', js)

grid_logic = """
let selectedResidentId = null;

async function loadResidentsGrid() {
    const grid = document.getElementById('residents-grid');
    grid.innerHTML = '<p>Cargando residentes...</p>';
    try {
        const snapshot = await db.collection('residentes').where('activo', '==', true).get();
        grid.innerHTML = '';
        if (snapshot.empty) {
            grid.innerHTML = '<p>No hay residentes activos.</p>';
            return;
        }
        snapshot.forEach(doc => {
            const data = doc.data();
            const photo = data.fotoUrl || 'https://via.placeholder.com/150?text=Sin+Foto';
            const card = document.createElement('div');
            card.className = 'resident-card';
            card.style.cssText = 'background: white; padding: 15px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center; cursor: pointer; transition: transform 0.2s;';
            card.innerHTML = `
                <img src="${photo}" style="width: 80px; height: 80px; border-radius: 50%; object-fit: cover; margin-bottom: 10px;">
                <h4 style="margin: 0; color: #333; font-size: 0.95rem;">${data.nombre}</h4>
            `;
            card.onmouseover = () => card.style.transform = 'translateY(-3px)';
            card.onmouseout = () => card.style.transform = 'translateY(0)';
            card.onclick = () => selectResidentForEval(doc.id, data.nombre, photo);
            grid.appendChild(card);
        });
    } catch (e) {
        console.error(e);
        grid.innerHTML = '<p>Error cargando residentes.</p>';
    }
}

async function selectResidentForEval(resId, resName, resPhoto) {
    selectedResidentId = resId;
    
    // Configurar header
    const photoEl = document.getElementById('form-resident-photo');
    if (resPhoto) {
        photoEl.src = resPhoto;
        photoEl.style.display = 'block';
    } else {
        photoEl.style.display = 'none';
    }
    document.getElementById('form-resident-name').innerText = resName;
    
    // Llenar rotaciones
    const rotSel = document.getElementById('rotation-select');
    rotSel.innerHTML = '<option value="">Seleccione rotación...</option>';
    subjectsYear1.forEach(sub => {
        rotSel.add(new Option(sub, sub));
    });
    
    // Limpiar formulario
    document.getElementById('eval-date').value = new Date().toISOString().split('T')[0];
    document.getElementById('eval-teacher').value = '';
    document.getElementById('eval-fortalezas').value = '';
    document.getElementById('eval-mejoras').value = '';
    
    showStep('step-form');
}
"""
js = js + grid_logic

# 5. Fix form submission (use selectedResidentId instead of select element)
# Find submitEvaluation and replace the reading of resident ID
js = js.replace("const residentId = document.getElementById('resident-select').value;", "const residentId = selectedResidentId;")
js = js.replace("const rotation = selectedSubjectName;", "const rotation = document.getElementById('rotation-select').value;")

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("app.js updated core logic.")
