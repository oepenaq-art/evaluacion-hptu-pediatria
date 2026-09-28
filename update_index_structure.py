# -*- coding: utf-8 -*-
import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add Firebase Storage
if 'firebase-storage-compat.js' not in html:
    html = html.replace(
        '<script src="https://www.gstatic.com/firebasejs/10.8.0/firebase-functions-compat.js"></script>',
        '<script src="https://www.gstatic.com/firebasejs/10.8.0/firebase-functions-compat.js"></script>\n    <script src="https://www.gstatic.com/firebasejs/10.8.0/firebase-storage-compat.js"></script>'
    )

# 2. Modify step-year to become step-residents-grid
html = re.sub(
    r'<div id="step-year".*?<!-- Step 2: Materia -->',
    '''<!-- Step: Grid de Residentes -->
            <div id="step-residents-grid" class="step hidden">
                <h2>Seleccione el Residente</h2>
                <div id="residents-grid" class="options-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-top: 20px;">
                    <!-- Las tarjetas fotográficas se insertarán aquí dinámicamente -->
                </div>
                <hr id="coord-hr" class="hidden" style="margin: 30px 0; border: none; border-top: 2px solid #e0e0e0;">
                <h3 id="coord-title" class="hidden" style="color: var(--primary-color); margin-bottom: 15px;">Área de Coordinación</h3>
                <div style="display:flex; gap:10px; flex-wrap:wrap;">
                    <button id="coord-btn" class="option-btn report-btn hidden" onclick="openCoordinatorSection()">Generar Informes (Word)</button>
                    <button id="admin-residents-btn" class="option-btn report-btn hidden" onclick="openAdminResidents()">Administrar Residentes</button>
                </div>
            </div>

            <!-- Step 2: Materia -->''',
    html,
    flags=re.DOTALL
)

# 3. Remove Step 2 (Materia) as we skip it
html = re.sub(
    r'<!-- Step 2: Materia -->.*?<!-- Step 3: Eval Form -->',
    '<!-- Step 3: Eval Form -->',
    html,
    flags=re.DOTALL
)

# 4. Modify Eval Form (remove resident dropdown, add rotation dropdown)
form_match = re.search(r'<div class="form-group".*?<label for="resident-select">Residente a evaluar:</label>.*?</select>\s*</div>', html, re.DOTALL)
if form_match:
    new_form_group = '''<div class="form-group" style="width: 100%;">
                            <label for="rotation-select">Rotación / Materia:</label>
                            <select id="rotation-select" required onchange="handleRotationChange()">
                                <option value="">Seleccione rotación...</option>
                            </select>
                        </div>'''
    html = html.replace(form_match.group(0), new_form_group)

# 5. Modify title of Eval Form to show resident photo + name dynamically
title_match = re.search(r'<h2 id="form-subject-title" style="margin-bottom: 20px; color: var\(--primary-color\);"></h2>', html)
if title_match:
    html = html.replace(title_match.group(0), '''
        <div id="form-resident-header" style="display:flex; align-items:center; gap:15px; margin-bottom:20px;">
            <img id="form-resident-photo" src="" style="width:60px; height:60px; border-radius:50%; object-fit:cover; display:none;">
            <h2 id="form-resident-name" style="color: var(--primary-color); margin:0;"></h2>
        </div>''')

# 6. Add Admin Residents Section at the end before </div><!-- app-container -->
admin_section = '''
            <!-- Sección Administración de Residentes -->
            <div id="step-admin-residents" class="step hidden">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <h2>Administrar Residentes</h2>
                    <button class="option-btn secondary" style="width: auto; padding: 8px 15px;" onclick="goBack('step-residents-grid')">Volver</button>
                </div>
                
                <div class="card" style="margin-bottom: 20px;">
                    <h3>Agregar Nuevo Residente</h3>
                    <form id="add-resident-form" onsubmit="event.preventDefault(); handleAddResident();">
                        <div class="form-group">
                            <label>Nombres Completos:</label>
                            <input type="text" id="new-res-name" required>
                        </div>
                        <div class="form-group">
                            <label>Foto (opcional pero recomendada):</label>
                            <input type="file" id="new-res-photo" accept="image/*">
                        </div>
                        <button type="submit" class="submit-btn" id="btn-add-res">Guardar Residente</button>
                    </form>
                </div>

                <div class="card">
                    <h3>Lista de Residentes (Activar / Retirar)</h3>
                    <div id="admin-residents-list" style="display:flex; flex-direction:column; gap:10px; margin-top:15px;">
                        <!-- Cargado dinámicamente -->
                    </div>
                </div>
            </div>
'''
html = html.replace('</div> <!-- .app-container -->', admin_section + '\n    </div> <!-- .app-container -->')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("index.html structure updated.")
