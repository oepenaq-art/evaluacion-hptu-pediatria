import re

with open('app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = next(i for i, l in enumerate(lines) if 'async function generateFinalReport' in l)

top_half = "".join(lines[:start_idx])

rest_of_code = """async function generateFinalReport() {
    if (reportEvaluations.length === 0) { alert('No hay evaluaciones para generar el informe.'); return; }

    const resName = document.getElementById('report-resident').options[document.getElementById('report-resident').selectedIndex].text;
    const rotation = document.getElementById('report-rotation').value;
    const dateFrom = document.getElementById('report-date-from').value;
    const dateTo = document.getElementById('report-date-to').value;

    showLoading('Consultando puntajes individuales...');

    const evalIds = reportEvaluations.map(e => e.id);
    let allItems = [];
    try {
        if (evalIds.length > 0) {
            const chunks = [];
            for (let i = 0; i < evalIds.length; i += 10) chunks.push(evalIds.slice(i, i + 10));
            for (const chunk of chunks) {
                const snapshot = await db.collection('evaluacion_items').where('evaluacion_id', 'in', chunk).get();
                snapshot.forEach(doc => allItems.push(doc.data()));
            }
        }
    } catch (e) { console.warn('No se pudieron obtener items:', e); }

    const evalRonda = reportEvaluations.filter(e => e.tipo_evaluacion === 'ronda' || !e.tipo_evaluacion);
    const evalSeminario = reportEvaluations.filter(e => e.tipo_evaluacion === 'seminario');
    const evalTemaCentral = reportEvaluations.filter(e => e.tipo_evaluacion === 'tema_central' || e.tipo_evaluacion === 'minicex');

    let avgRonda = 0, avgSeminario = 0, avgTema = 0;
    if(evalRonda.length > 0) avgRonda = evalRonda.reduce((s, e) => s + parseFloat(e.nota_final), 0) / evalRonda.length;
    if(evalSeminario.length > 0) avgSeminario = evalSeminario.reduce((s, e) => s + parseFloat(e.nota_final), 0) / evalSeminario.length;
    if(evalTemaCentral.length > 0) avgTema = evalTemaCentral.reduce((s, e) => s + parseFloat(e.nota_final), 0) / evalTemaCentral.length;

    let avgFinalNum = 0;
    let distribucionNotas = "";

    if (rotation === "Urgencias pediátricas III nivel de fundamentación" || rotation === "Hospitalización pediátrica tercer nivel fundamentación") {
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
    }
    
    const avgFinal = avgFinalNum.toFixed(2);

    const calcItemAverages = (evalList, rubricDef) => {
        const itemAverages = {};
        const listIds = evalList.map(e => e.id);
        const relevantItems = allItems.filter(ai => listIds.includes(ai.evaluacion_id));
        const rubricItems = rubricDef.flatMap(c => c.items.map(i => ({ ...i, category: c.category })));
        
        rubricItems.forEach(ri => {
            const scores = relevantItems.filter(ai => ai.item_id === ri.id).map(ai => parseFloat(ai.nota));
            if (scores.length > 0) {
                itemAverages[ri.id] = {
                    title: ri.title, category: ri.category, weight: ri.weight,
                    avg: (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1),
                    count: scores.length, min: Math.min(...scores).toFixed(1), max: Math.max(...scores).toFixed(1)
                };
            }
        });
        return itemAverages;
    };

    const itemAveragesRonda = calcItemAverages(evalRonda, rubricStructure);
    const itemAveragesSeminario = calcItemAverages(evalSeminario, rubricSeminario);
    const itemAveragesTema = calcItemAverages(evalTemaCentral, rubricTemaCentral);

    const allFortalezas = reportEvaluations.filter(e => e.fortalezas).map(e => (e.docente_nombre || 'Docente') + ': ' + e.fortalezas);
    const allMejoras = reportEvaluations.filter(e => e.por_mejorar).map(e => (e.docente_nombre || 'Docente') + ': ' + e.por_mejorar);
    const teachers = [...new Set(reportEvaluations.map(e => e.docente_nombre || 'Docente'))];

    showLoading('Generando análisis cualitativo (IA)...');
    let aiAnalysis = '';
    const apiKey = localStorage.getItem('geminiApiKey');
    
    if (apiKey) {
        try {
            aiAnalysis = await callGeminiForReport(apiKey, resName, rotation, avgFinal, itemAveragesRonda, allFortalezas, allMejoras, MICROCURRICULOS[rotation]);
        } catch (e) {
            console.warn('Error en Gemini, usando síntesis cualitativa local:', e);
            aiAnalysis = generateDescriptiveAnalysis(resName, rotation, avgFinal, itemAveragesRonda, allFortalezas, allMejoras) + '\n\n(Nota: ' + e.message + ')';
        }
    } else {
        aiAnalysis = generateDescriptiveAnalysis(resName, rotation, avgFinal, itemAveragesRonda, allFortalezas, allMejoras);
    }

    showLoading('Construyendo documento Word...');
    try {
        await buildWordReport(resName, rotation, dateFrom, dateTo, teachers, reportEvaluations, itemAveragesRonda, itemAveragesSeminario, itemAveragesTema, avgRonda, avgSeminario, avgTema, avgFinal, distribucionNotas, aiAnalysis, allFortalezas, allMejoras);
    } catch (e) {
        console.error('Error generando Word:', e);
        alert('Error al generar el documento: ' + e.message);
    }

    hideLoading();
}

async function callGeminiForReport(apiKey, resName, rotation, avgFinal, itemAverages, fort, mej, microcurriculo) {
    const url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=' + apiKey;
    
    const prompt = `Actúa como el Coordinador del Programa de Especialización en Pediatría. Redacta la SÍNTESIS CUALITATIVA DEL DESEMPEÑO para el informe final de rotación del residente.
Residente: ${resName}
Rotación: ${rotation}
Nota Promedio Final: ${avgFinal} / 5.0
Microcurrículo de la rotación (Competencias esperadas): ${microcurriculo || 'No especificado.'}
Resumen de notas por ítem: ${Object.values(itemAverages).map(i => '- ' + i.title + ': ' + i.avg).join('\\n')}
Comentarios de Fortalezas (debatidos por los docentes): ${fort.join(' | ')}
Comentarios por Mejorar (debatidos por los docentes): ${mej.join(' | ')}
Instrucciones estrictas:
1. Redacta en tercera persona de forma muy formal y profesional.
2. NO menciones los nombres de los docentes evaluadores bajo ninguna circunstancia.
3. El informe debe constar de 2 a 3 párrafos bien estructurados.
4. Conecta el desempeño real del residente (notas y comentarios) explícitamente con las competencias esperadas en el Microcurrículo.
5. Si el promedio es menor a 3.6, enfatiza en un tono constructivo pero firme las áreas críticas a mejorar según el microcurrículo.
6. NO incluyas saludos ni despedidas, ve directo al texto del informe.`;

    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            contents: [{ parts: [{ text: prompt }] }],
            generationConfig: { temperature: 0.3 }
        })
    });

    if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error?.message || 'Error en la API de Gemini');
    }

    const data = await response.json();
    if (data.candidates && data.candidates.length > 0) {
        return data.candidates[0].content.parts[0].text.trim();
    }
    throw new Error('Respuesta vacía de Gemini');
}

function generateDescriptiveAnalysis(resName, rotation, avg, items, fort, mej) {
    let q = avg >= 4.6 ? 'sobresaliente' : avg >= 3.6 ? 'bueno' : avg >= 3.0 ? 'aceptable' : 'insuficiente';
    const cleanFort = fort.map(f => f.replace(/^[^:]+:\s*/, ''));
    const cleanMej = mej.map(m => m.replace(/^[^:]+:\s*/, ''));

    return `Durante el período evaluado en la rotación de ${rotation}, el/la residente ${resName} ha demostrado un desempeño general calificado como ${q.toUpperCase()}, obteniendo una nota promedio final de ${avg}/5.0 a partir de las evaluaciones consolidadas en este período.\n\n` +
        (cleanFort.length > 0 ? `Entre las fortalezas destacadas por los docentes evaluadores se encuentran: ${cleanFort.join('. ')}.\n\n` : '') +
        (cleanMej.length > 0 ? `Las áreas identificadas como oportunidades de mejora y recomendaciones incluyen: ${cleanMej.join('. ')}.\n\n` : '') +
        `Se sugiere continuar con el fortalecimiento de las habilidades clínicas y académicas delineadas en el microcurrículo, fomentando un aprendizaje continuo en su especialización médica.`;
}

async function buildWordReport(resName, rotation, dateFrom, dateTo, teachers, evaluations, itemAveragesRonda, itemAveragesSeminario, itemAveragesTema, avgRonda, avgSeminario, avgTema, avgFinal, distribucionNotas, aiAnalysis, fortalezas, mejoras) {
    const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, HeadingLevel, AlignmentType, WidthType, BorderStyle, ShadingType } = docx;

    const qualitative = avgFinal >= 4.6 ? 'SOBRESALIENTE' : avgFinal >= 3.6 ? 'BUENO' : avgFinal >= 3.0 ? 'ACEPTABLE' : 'INSUFICIENTE';

    const createTableRows = (title, avgValue, itemAverages) => {
        const rows = [
            new TableRow({
                children: [
                    new TableCell({
                        columnSpan: 6,
                        shading: { type: ShadingType.CLEAR, fill: "F0F4F8" },
                        children: [new Paragraph({ children: [new TextRun({ text: title + ' - Promedio: ' + (avgValue>0 ? avgValue.toFixed(2) : 'N/A'), bold: true, size: 20 })], alignment: AlignmentType.CENTER })]
                    })
                ]
            }),
            new TableRow({
                tableHeader: true,
                children: ['Competencia', 'Peso', 'Promedio', 'Mín', 'Máx', 'Evaluaciones'].map(text =>
                    new TableCell({
                        shading: { type: ShadingType.CLEAR, fill: "005A9C" },
                        children: [new Paragraph({ children: [new TextRun({ text, color: 'FFFFFF', bold: true })], alignment: AlignmentType.CENTER })],
                        margins: { top: 100, bottom: 100, left: 100, right: 100 }
                    })
                )
            })
        ];

        Object.values(itemAverages).forEach(item => {
            rows.push(new TableRow({
                children: [
                    new TableCell({ children: [new Paragraph({ text: item.title, alignment: AlignmentType.LEFT })], margins: { top: 80, bottom: 80, left: 100, right: 100 } }),
                    new TableCell({ children: [new Paragraph({ text: (item.weight * 100) + '%', alignment: AlignmentType.CENTER })] }),
                    new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.avg, bold: true })], alignment: AlignmentType.CENTER })] }),
                    new TableCell({ children: [new Paragraph({ text: item.min, alignment: AlignmentType.CENTER })] }),
                    new TableCell({ text: item.max }),
                    new TableCell({ children: [new Paragraph({ text: item.count.toString(), alignment: AlignmentType.CENTER })] })
                ]
            }));
        });
        return rows;
    };

    const allTableRows = [];
    if (Object.keys(itemAveragesRonda).length > 0) allTableRows.push(...createTableRows('Ronda Médica', avgRonda, itemAveragesRonda));
    if (Object.keys(itemAveragesSeminario).length > 0) allTableRows.push(...createTableRows('Seminarios', avgSeminario, itemAveragesSeminario));
    if (Object.keys(itemAveragesTema).length > 0) allTableRows.push(...createTableRows('Tema Central / MiniCEX', avgTema, itemAveragesTema));

    const paragraphs = [
        new Paragraph({ children: [new TextRun({ text: 'INFORME FINAL DE ROTACIÓN', bold: true, size: 32, color: '005A9C' })], alignment: AlignmentType.CENTER, spacing: { after: 400 } }),
        new Paragraph({ children: [new TextRun({ text: 'Residente: ', bold: true, size: 22 }), new TextRun({ text: resName, size: 22 })] }),
        new Paragraph({ children: [new TextRun({ text: 'Rotación: ', bold: true, size: 22 }), new TextRun({ text: rotation, size: 22 })] }),
        new Paragraph({ children: [new TextRun({ text: 'Período evaluado: ', bold: true, size: 22 }), new TextRun({ text: dateFrom + ' a ' + dateTo, size: 22 })] }),
        new Paragraph({ children: [new TextRun({ text: 'Total de evaluaciones: ', bold: true, size: 22 }), new TextRun({ text: evaluations.length.toString(), size: 22 })] }),
        new Paragraph({ spacing: { before: 60, after: 60 }, children: [new TextRun({ text: 'Distribución de Notas: ', bold: true, size: 22 }), new TextRun({ text: distribucionNotas, size: 22, italics: true })] }),
        new Paragraph({ spacing: { after: 200 }, children: [new TextRun({ text: 'Docentes evaluadores: ', bold: true, size: 22 }), new TextRun({ text: teachers.join(', '), size: 22 })] }),

        new Paragraph({ spacing: { before: 300, after: 200 }, children: [new TextRun({ text: 'CALIFICACIÓN PROMEDIO POR COMPETENCIAS', bold: true, size: 26, color: '005A9C' })] })
    ];

    if (allTableRows.length > 0) {
        paragraphs.push(new Table({ rows: allTableRows, width: { size: 100, type: WidthType.PERCENTAGE } }));
    }

    paragraphs.push(
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 300, after: 100 }, children: [
            new TextRun({ text: 'NOTA DEFINITIVA: ', bold: true, size: 28 }),
            new TextRun({ text: avgFinal + ' / 5.0', bold: true, size: 36, color: avgFinal < 3.0 ? 'E74C3C' : avgFinal < 3.6 ? 'F39C12' : avgFinal < 4.6 ? '2980B9' : '27AE60' })
        ]}),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 300 }, children: [new TextRun({ text: 'Desempeño: ' + qualitative, bold: true, size: 24, color: '666666' })] }),

        new Paragraph({ spacing: { before: 200, after: 100 }, children: [new TextRun({ text: 'SÍNTESIS CUALITATIVA DEL DESEMPEÑO', bold: true, size: 24, color: '005A9C' })] }),
        new Paragraph({ spacing: { after: 200 }, children: [new TextRun({ text: aiAnalysis, size: 22 })] }),

        new Paragraph({ spacing: { before: 200, after: 100 }, children: [new TextRun({ text: 'OBSERVACIONES - FORTALEZAS', bold: true, size: 24, color: '27AE60' })] })
    );

    fortalezas.forEach(f => paragraphs.push(new Paragraph({ text: '• ' + f, size: 22, spacing: { after: 60 } })));

    paragraphs.push(new Paragraph({ spacing: { before: 200, after: 100 }, children: [new TextRun({ text: 'OBSERVACIONES - POR MEJORAR', bold: true, size: 24, color: 'E74C3C' })] }));

    mejoras.forEach(m => paragraphs.push(new Paragraph({ text: '• ' + m, size: 22, spacing: { after: 60 } })));

    const doc = new Document({ sections: [{ properties: {}, children: paragraphs }] });

    const blob = await Packer.toBlob(doc);
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'Informe_Final_' + resName.replace(/ /g, '_') + '_' + rotation.substring(0, 20).replace(/ /g, '_') + '.docx';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function showLoading(text) {
    document.getElementById('loading-text').innerText = text || 'Procesando...';
    document.getElementById('loading-overlay').classList.remove('hidden');
}
function hideLoading() { document.getElementById('loading-overlay').classList.add('hidden'); }
"""

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(top_half + rest_of_code)

import os
brain_dir = r'C:\Users\LENOVO\.gemini\antigravity\brain\11705742-ddec-4e19-bc0b-e0e230680f05'
with open(os.path.join(brain_dir, 'codigo_app.md'), 'w', encoding='utf-8') as f:
    f.write('# Archivo `app.js`\n\n```javascript\n' + top_half + rest_of_code + '\n```\n')

print("Fixed syntax totally using python single quoted string.")
