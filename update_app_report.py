# -*- coding: utf-8 -*-
with open('app.js', 'r', encoding='utf-8') as f:
    js = f.read()

import re

match = re.search(r'async function generateFinalReport\(\) \{[\s\S]*?a\.click\(\);[\s\S]*?\}', js)
if match:
    old_func = match.group(0)
    
    new_func = """async function generateFinalReport() {
    if (reportEvaluations.length === 0) { alert('No hay evaluaciones para generar el informe.'); return; }

    const resName = document.getElementById('report-resident').options[document.getElementById('report-resident').selectedIndex].text;
    const rotation = document.getElementById('report-rotation').value;
    const dateFrom = document.getElementById('report-date-from').value;
    const dateTo = document.getElementById('report-date-to').value;

    showLoading('Generando documento Word...');

    try {
        let aiText = "El informe generado por IA va aquí...";
        if (document.getElementById('report-generated-text')) {
            aiText = document.getElementById('report-generated-text').innerText || aiText;
        }

        const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, HeadingLevel, WidthType, BorderStyle } = docx;

        let paragraphs = [];
        paragraphs.push(new Paragraph({ children: [new TextRun({ text: 'HOSPITAL PABLO TOBÓN URIBE', bold: true, size: 28 })], alignment: 'center' }));
        paragraphs.push(new Paragraph({ children: [new TextRun({ text: 'INFORME FINAL DE ROTACIÓN', bold: true, size: 24 })], alignment: 'center', spacing: { after: 400 } }));

        paragraphs.push(new Paragraph({ children: [new TextRun({ text: 'Nombre del Residente: ', bold: true }), new TextRun({ text: resName })], spacing: { after: 120 } }));
        paragraphs.push(new Paragraph({ children: [new TextRun({ text: 'Rotación Evaluada: ', bold: true }), new TextRun({ text: rotation })], spacing: { after: 120 } }));
        paragraphs.push(new Paragraph({ children: [new TextRun({ text: 'Período: ', bold: true }), new TextRun({ text: `${dateFrom} a ${dateTo}` })], spacing: { after: 300 } }));

        paragraphs.push(new Paragraph({ text: '1. Desglose de Evaluaciones Individuales', heading: HeadingLevel.HEADING_2, spacing: { before: 200, after: 120 } }));

        // Create table for individual evaluations
        const rows = [];
        // Header
        rows.push(new TableRow({
            children: [
                new TableCell({ children: [new Paragraph({ text: "Fecha", bold: true })] }),
                new TableCell({ children: [new Paragraph({ text: "Docente", bold: true })] }),
                new TableCell({ children: [new Paragraph({ text: "Tipo Actividad", bold: true })] }),
                new TableCell({ children: [new Paragraph({ text: "Nota", bold: true })] })
            ],
            tableHeader: true
        }));

        reportEvaluations.forEach(ev => {
            const fecha = ev.created_at && ev.created_at.toDate ? ev.created_at.toDate().toLocaleDateString('es-CO') : '-';
            let tipo = ev.tipo_evaluacion || 'ronda';
            if (ev.nombre_actividad) tipo += ` (${ev.nombre_actividad})`;
            
            rows.push(new TableRow({
                children: [
                    new TableCell({ children: [new Paragraph({ text: fecha })] }),
                    new TableCell({ children: [new Paragraph({ text: ev.docente_nombre || 'Docente' })] }),
                    new TableCell({ children: [new Paragraph({ text: tipo })] }),
                    new TableCell({ children: [new Paragraph({ text: ev.nota_final || '-' })] })
                ]
            }));
        });

        paragraphs.push(new Table({
            rows: rows,
            width: { size: 100, type: WidthType.PERCENTAGE },
        }));

        paragraphs.push(new Paragraph({ text: '2. Informe Consolidado Cualitativo', heading: HeadingLevel.HEADING_2, spacing: { before: 400, after: 200 } }));

        const blocks = aiText.split('\\n').filter(b => b.trim().length > 0);
        blocks.forEach(m => paragraphs.push(new Paragraph({ text: ' ' + m, size: 22, spacing: { after: 120 } })));

        const doc = new Document({ sections: [{ properties: {}, children: paragraphs }] });

        const blob = await Packer.toBlob(doc);
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'Informe_Final_' + resName.replace(/ /g, '_') + '_' + rotation.substring(0, 20).replace(/ /g, '_') + '.docx';
        document.body.appendChild(a);
        a.click();
        
        hideLoading();
    } catch (e) {
        hideLoading();
        console.error(e);
        alert('Error generando Word: ' + e.message);
    }
}"""
    js = js.replace(old_func, new_func)
    
    with open('app.js', 'w', encoding='utf-8') as f:
        f.write(js)
    print("generateFinalReport updated!")
else:
    print("generateFinalReport not found.")
