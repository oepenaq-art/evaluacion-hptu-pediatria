import re

with open('app.js', 'r', encoding='utf-8', errors='ignore') as f:
    js = f.read()

# I will completely replace selectSubject using regex
select_subj_match = re.search(r'async function selectSubject\(subject\).*?\}\n', js, re.DOTALL)
if select_subj_match:
    old_func = select_subj_match.group(0)
    
    new_func = """async function selectSubject(subject) {
    selectedSubjectName = subject;
    document.getElementById('form-subject-title').innerText = subject;
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
        optRonda.innerText = 'Ronda Médica (50%)';
        optSeminario.innerText = 'Seminario (30%)';
    } else {
        optTema.classList.add('hidden');
        optMinicex.classList.add('hidden');
        optRonda.innerText = 'Ronda Médica (60%)';
        optSeminario.innerText = 'Seminario (40%)';
    }

    // Restore UI state
    document.getElementById('subject-list-view').classList.add('hidden');
    document.getElementById('evaluation-view').classList.remove('hidden');
    document.getElementById('eval-history').innerHTML = '';
    
    // Clear fields
    document.getElementById('eval-date').value = new Date().toISOString().split('T')[0];
    document.getElementById('eval-teacher').value = '';
    document.getElementById('eval-resident').value = '';
    document.getElementById('eval-fortalezas').value = '';
    document.getElementById('eval-mejoras').value = '';
    
    handleEvaluationTypeChange(); // Call this to set the right rubric
}
"""
    js = js.replace(old_func, new_func)
    
    with open('app.js', 'w', encoding='utf-8') as f:
        f.write(js)
    print("selectSubject updated successfully.")
else:
    print("Could not find selectSubject.")
