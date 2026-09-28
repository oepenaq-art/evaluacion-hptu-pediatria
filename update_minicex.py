# -*- coding: utf-8 -*-
with open('app.js', 'r', encoding='utf-8') as f:
    js = f.read()
import re

new_minicex = """const rubricMiniCex = [
    {
        category: "Mini-CEX (Escala de 1 a 9)",
        items: [
            { id: "mc_anamnesis", title: "1. Anamnesis del paciente y/o acudiente", desc: "Facilita la narración del paciente y/o acudiente. Utiliza preguntas adecuadas de manera eficaz. Realiza un interrogatorio completo del motivo de consulta, enfermedad actual y antecedentes (patológicos, quirúrgicos, alérgicos, inmunizaciones, familiares). Responde adecuadamente a mensajes claves verbales y no verbales.", weight: 1/8 },
            { id: "mc_examen", title: "2. Examen físico del paciente", desc: "Sigue una secuencia lógica y eficiente céfalo caudal. Exploración centrada en el problema clínico. Informa al paciente. Respeta la comodidad del paciente.", weight: 1/8 },
            { id: "mc_juicio", title: "3. Juicio clínico, análisis y diagnósticos diferenciales", desc: "Realiza un diagnóstico apropiado y tiene en cuenta los diagnósticos diferenciales. Analiza de forma apropiada y crítica los diagnósticos.", weight: 1/8 },
            { id: "mc_plan", title: "4. Plan de manejo (tratamiento y ayudas diagnósticas)", desc: "Establece un plan terapéutico acorde al diagnóstico. Propone ayudas diagnósticas pertinentes y completas, considerando los riesgos y beneficios.", weight: 1/8 },
            { id: "mc_comunicacion", title: "5. Habilidades comunicativas", desc: "Utiliza un lenguaje claro para el paciente. Es empático. Es honesto y pertinente. Explica al paciente el diagnóstico y el plan. Educa al paciente y a su familia.", weight: 1/8 },
            { id: "mc_organizacion", title: "6. Organización / eficiencia", desc: "Prioriza. Se ajusta al tiempo. Es concreto.", weight: 1/8 },
            { id: "mc_profesionalismo", title: "7. Profesionalismo", desc: "Muestra respeto por el paciente y su familia. Establece confianza y una buena relación. Guarda la confidencialidad de la historia clínica. Considera los aspectos legales relevantes.", weight: 1/8 },
            { id: "mc_evaluacion", title: "8. Evaluación clínica global", desc: "Demuestra de forma satisfactoria el juicio clínico, síntesis y efectividad. Utiliza adecuadamente los recursos. Es consciente de sus propias limitaciones.", weight: 1/8 }
        ]
    }
];"""

js = re.sub(r'const rubricMiniCex = \[[\s\S]*?\];', new_minicex, js)

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("MiniCex text updated.")
