import re
with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

target = r"const previewDiv = document.getElementById\('report-preview'\);\s*\} catch \(e\) \{"
replacement = """const previewDiv = document.getElementById('report-preview');
        const contentDiv = document.getElementById('report-preview-content');
        const resName = document.getElementById('report-resident').options[document.getElementById('report-resident').selectedIndex].text;
        const teachers = [...new Set(evals.map(e => e.docente_nombre || 'Docente'))];
        const avgScore = (evals.reduce((s, e) => s + parseFloat(e.nota_final), 0) / evals.length).toFixed(2);

        let html = `
            <p><span class="report-stat">${evals.length} evaluaciones</span>
               <span class="report-stat">${teachers.length} docente(s)</span>
               <span class="report-stat">Promedio simple: ${avgScore} (El ponderado se calcula en el Word)</span></p>
            <p style="margin:10px 0;"><strong>Residente:</strong> ${resName} &nbsp;|&nbsp; <strong>Rotación:</strong> ${rotation}</p>
            <p style="margin-bottom:15px;"><strong>Período:</strong> ${dateFrom} a ${dateTo}</p>
            <h4 style="margin-bottom:10px; color:var(--primary-color);">Detalle de evaluaciones:</h4>`;

        evals.forEach((ev, i) => {
            const fecha = ev.created_at && ev.created_at.toDate ? ev.created_at.toDate().toLocaleDateString('es-CO') : new Date().toLocaleDateString('es-CO');
            const docName = ev.docente_nombre || 'Docente';
            let tipoTag = ev.tipo_evaluacion ? ev.tipo_evaluacion.toUpperCase() : 'RONDA MÉDICA';
            if (ev.tipo_evaluacion === 'tema_central') tipoTag = 'TEMA CENTRAL';
            if (ev.tipo_evaluacion === 'minicex') tipoTag = 'MINICEX';

            html += `<div class="report-eval-card">
                <strong>#${i+1}</strong> — ${fecha} — <strong>${docName}</strong> — Nota: <strong>${ev.nota_final}</strong>
                <br><span style="font-size: 0.85rem; font-weight: 600; color: #555;">[${tipoTag}] ${ev.nombre_actividad ? ev.nombre_actividad : ''}</span>
                ${ev.fortalezas ? `<br><em style="color:var(--success);">👍 ${ev.fortalezas}</em>` : ''}
                ${ev.por_mejorar ? `<br><em style="color:var(--warning);">🎯 ${ev.por_mejorar}</em>` : ''}
            </div>`;
        });

        contentDiv.innerHTML = html;
        previewDiv.classList.remove('hidden');

    } catch (e) {"""

new_content = re.sub(target, replacement, content)
with open('app.js', 'w', encoding='utf-8') as f:
    f.write(new_content)
