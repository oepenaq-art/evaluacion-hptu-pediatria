import re

with open('app.js', 'r', encoding='utf-8', errors='ignore') as f:
    js = f.read()

match = re.search(r'async function selectSubject\(subject\).*?showStep\(\'step-form\'\);\n\}', js, re.DOTALL)
if match:
    old_func = match.group(0)
    
    new_func = """async function selectSubject(subject) {
    selectedSubjectName = subject;
    document.getElementById('form-subject-title').innerText = subject;
    Object.keys(itemSelections).forEach(k => delete itemSelections[k]);
    document.querySelectorAll('.score-btn').forEach(b => b.classList.remove('selected'));
    document.querySelectorAll('.score-input-row').forEach(r => { r.classList.add('hidden'); r.style.display = 'none'; });
    
    const evalTypeSelect = document.getElementById('evaluation-type');
    evalTypeSelect.value = 'ronda'; // default
    
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

    await loadResidents();
    await loadTeachers(subject);
    showStep('step-form');
}"""
    js = js.replace(old_func, new_func)
    
    with open('app.js', 'w', encoding='utf-8') as f:
        f.write(js)
    print("selectSubject updated successfully.")
else:
    print("Could not find selectSubject.")
