# -*- coding: utf-8 -*-
with open('app.js', 'r', encoding='utf-8') as f:
    js = f.read()

admin_funcs = """
function openAdminResidents() {
    showStep('step-admin-residents');
    loadAdminResidentsList();
}

async function loadAdminResidentsList() {
    const list = document.getElementById('admin-residents-list');
    list.innerHTML = '<p>Cargando...</p>';
    try {
        const snapshot = await db.collection('residentes').orderBy('nombre').get();
        list.innerHTML = '';
        snapshot.forEach(doc => {
            const data = doc.data();
            const isActive = data.activo !== false; // por defecto true
            const item = document.createElement('div');
            item.style.cssText = 'display:flex; justify-content:space-between; align-items:center; background:#f9f9f9; padding:10px; border-radius:8px; border-left:4px solid ' + (isActive ? 'var(--primary-color)' : '#999');
            
            const btnText = isActive ? 'Retirar' : 'Activar';
            const btnColor = isActive ? 'var(--danger)' : 'var(--primary-color)';
            
            item.innerHTML = `
                <div style="display:flex; align-items:center; gap:15px;">
                    <img src="${data.fotoUrl || 'https://via.placeholder.com/50?text=Foto'}" style="width:40px; height:40px; border-radius:50%; object-fit:cover;">
                    <span style="font-weight:600; color:${isActive ? '#333' : '#999'}">${data.nombre}</span>
                </div>
                <button class="option-btn" style="width:auto; padding:5px 15px; font-size:0.85rem; background:${btnColor}" onclick="toggleResidentStatus('${doc.id}', ${isActive})">${btnText}</button>
            `;
            list.appendChild(item);
        });
    } catch (e) {
        console.error(e);
        list.innerHTML = '<p>Error cargando lista.</p>';
    }
}

async function handleAddResident() {
    const nameInput = document.getElementById('new-res-name').value.trim();
    const photoInput = document.getElementById('new-res-photo');
    const btn = document.getElementById('btn-add-res');
    
    if (!nameInput) return;
    
    btn.disabled = true;
    btn.innerText = 'Guardando...';
    
    try {
        let photoUrl = null;
        if (photoInput.files.length > 0) {
            const file = photoInput.files[0];
            const ref = storage.ref().child(`residents-photos/${Date.now()}_${file.name}`);
            await ref.put(file);
            photoUrl = await ref.getDownloadURL();
        }
        
        await db.collection('residentes').add({
            nombre: nameInput,
            fotoUrl: photoUrl,
            activo: true,
            createdAt: firebase.firestore.FieldValue.serverTimestamp()
        });
        
        document.getElementById('add-resident-form').reset();
        await loadAdminResidentsList();
        alert('Residente guardado exitosamente.');
    } catch (e) {
        console.error(e);
        alert('Error al guardar residente: ' + e.message);
    } finally {
        btn.disabled = false;
        btn.innerText = 'Guardar Residente';
    }
}

async function toggleResidentStatus(id, currentStatus) {
    if (!confirm(`¿Está seguro de querer ${currentStatus ? 'retirar' : 'activar'} a este residente?`)) return;
    try {
        await db.collection('residentes').doc(id).update({ activo: !currentStatus });
        loadAdminResidentsList();
    } catch (e) {
        console.error(e);
        alert('Error cambiando estado.');
    }
}
"""

if 'openAdminResidents' not in js:
    js += admin_funcs

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("app.js updated with admin funcs.")
