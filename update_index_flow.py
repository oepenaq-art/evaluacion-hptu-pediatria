# -*- coding: utf-8 -*-
import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Main menu
main_menu = """
            <!-- Step: Menú Principal -->
            <div id="step-main-menu" class="step hidden">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h2>Menú Principal</h2>
                    <p>Seleccione una opción para continuar</p>
                </div>
                <div style="display:flex; flex-direction:column; gap:15px; max-width:400px; margin:0 auto;">
                    <button class="option-btn" onclick="showStep('step-residents-grid'); loadResidentsGrid();">👨‍⚕️ Evaluar Residente</button>
                    <button class="option-btn report-btn" onclick="openCoordinatorSection()">📊 Generar Informes (Word)</button>
                    <button class="option-btn secondary" onclick="openAdminResidents()">⚙️ Administrar Residentes</button>
                    <button class="option-btn" style="background:#e0e0e0; color:#333; margin-top:20px;" onclick="auth.signOut()">Cerrar Sesión</button>
                </div>
            </div>
"""

# Find where to insert step-main-menu (after step-login)
html = re.sub(r'(<div id="step-login" class="step.*?</form>\s*</div>)', r'\1\n' + main_menu, html, flags=re.DOTALL)

# 2. Modify step-residents-grid to add a back button to main menu
html = re.sub(
    r'<div id="step-residents-grid".*?<h2>Seleccione el Residente</h2>',
    '''<div id="step-residents-grid" class="step hidden">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h2>Seleccione el Residente</h2>
                    <button class="option-btn secondary" style="width:auto; padding:5px 15px;" onclick="showStep('step-main-menu')">Volver</button>
                </div>''',
    html, flags=re.DOTALL
)

# 3. Remove Coord section buttons from step-residents-grid
html = re.sub(r'<hr id="coord-hr".*?</div>\s*<!-- Step 3: Eval Form -->', '<!-- Step 3: Eval Form -->', html, flags=re.DOTALL)

# 4. In Admin residents, change "Volver" to go to step-main-menu
html = html.replace("goBack('step-residents-grid')", "showStep('step-main-menu')")

# 5. In Admin residents form, add Year selection
year_select = """
                        <div class="form-group">
                            <label>Año de Residencia:</label>
                            <select id="new-res-year" required>
                                <option value="1">Año 1</option>
                                <option value="2">Año 2</option>
                                <option value="3">Año 3</option>
                            </select>
                        </div>
"""
html = html.replace('<button type="submit" class="submit-btn" id="btn-add-res">Guardar Residente</button>', year_select + '\n                        <button type="submit" class="submit-btn" id="btn-add-res">Guardar Residente</button>')

# 6. Remove Rotation Select from Eval Form
html = re.sub(r'<div class="form-group" style="width: 100%;">\s*<label for="rotation-select">Rotación / Materia:</label>\s*<select id="rotation-select".*?</select>\s*</div>', '', html, flags=re.DOTALL)

# 7. Add the new evaluation types to evaluation-type dropdown (hidden by default)
new_options = """
    <option value="ronda" id="opt-ronda">Ronda Médica / Práctica (50%)</option>
    <option value="seminario" id="opt-seminario">Seminario / Oral (30%)</option>
    <option value="minicex" id="opt-minicex" class="hidden">MiniCEX (20%)</option>
    <option value="tema_central" id="opt-tema-central" class="hidden">Tema Central (10%)</option>
    <option value="club_revistas" id="opt-club-revistas" class="hidden">Club de Revistas (10%)</option>
    <option value="actividad_educativa" id="opt-actividad-educativa" class="hidden">Actividad Educativa (10%)</option>
"""
html = re.sub(r'<select id="evaluation-type" required onchange="handleEvaluationTypeChange()">.*?</select>', '<select id="evaluation-type" required onchange="handleEvaluationTypeChange()">\n' + new_options + '</select>', html, flags=re.DOTALL)

# 8. Report Form: We need to know which resident we are evaluating. 
# In step-report, we already have a select for resident. We can keep it or load them dynamically.
# We also need to remove Rotation select from the report form, as it's implicit to the resident's year!
html = re.sub(r'<div class="form-group">\s*<label for="report-rotation">Rotación.*?</select>\s*</div>', '', html, flags=re.DOTALL)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("index.html successfully updated for new flow.")
