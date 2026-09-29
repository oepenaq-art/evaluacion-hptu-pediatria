/* ========================================================
   CONFIGURACIÓN DE FIREBASE
   ======================================================== */
const firebaseConfig = {
  apiKey: "AIzaSyDaIlDaCWrRw-scE0fXchQ8PY-IdpCeUwE",
  authDomain: "evaluacion-pediatria-eia.firebaseapp.com",
  projectId: "evaluacion-pediatria-eia",
  storageBucket: "evaluacion-pediatria-eia.firebasestorage.app",
  messagingSenderId: "629594470240",
  appId: "1:629594470240:web:21aa9efe16fe9efd23d005"
};

firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();
const db = firebase.firestore();
const functions = firebase.functions();
const storage = firebase.storage();

// Forzar persistencia local para navegadores móviles restrictivos
auth.setPersistence(firebase.auth.Auth.Persistence.LOCAL).catch(e => console.error("Persistence error:", e));

let currentUser = null;
let userRole = 'docente'; // 'docente' o 'coordinador'

/* ========================================================
   AUTENTICACIÓN Y OBSERVADOR DE SESIÓN
   ======================================================== */
auth.onAuthStateChanged(async (user) => {
    if (user) {
        currentUser = user;
        currentUser.nombre = user.email;
        userRole = 'coordinador';

        document.getElementById('user-bar').classList.remove('hidden');
        document.getElementById('user-info-text').innerText = `👤 ${currentUser.nombre} (${userRole.toUpperCase()})`;

        if (userRole === 'coordinador') {
            var el_coord_hr = document.getElementById('coord-hr'); if (el_coord_hr) el_coord_hr.classList.remove('hidden');
            var el_coord_title = document.getElementById('coord-title'); if (el_coord_title) el_coord_title.classList.remove('hidden');
            var el_coord_btn = document.getElementById('coord-btn'); if (el_coord_btn) el_coord_btn.classList.remove('hidden');
        } else {
            var el_coord_hr = document.getElementById('coord-hr'); if (el_coord_hr) el_coord_hr.classList.add('hidden');
            var el_coord_title = document.getElementById('coord-title'); if (el_coord_title) el_coord_title.classList.add('hidden');
            var el_coord_btn = document.getElementById('coord-btn'); if (el_coord_btn) el_coord_btn.classList.add('hidden');
        }

        showStep('step-main-menu');
    } else {
        currentUser = null;
        var el_user_bar = document.getElementById('user-bar'); if (el_user_bar) el_user_bar.classList.add('hidden');
        showStep('step-login');
    }
});

async function handleLogin() {
    const email = document.getElementById('login-email').value.trim().toLowerCase();
    const password = document.getElementById('login-password').value;
    const errorEl = document.getElementById('login-error');
    errorEl.classList.add('hidden');
    showLoading('Iniciando sesión en Firebase...');

    try {
        await auth.signInWithEmailAndPassword(email, password);
        hideLoading();
    } catch (e) {
        hideLoading();
        let msg = 'Error al iniciar sesión. Verifique sus datos.';
        if (e.code === 'auth/user-not-found' || e.code === 'auth/wrong-password' || e.code === 'auth/invalid-credential') {
            msg = 'Correo o contraseña incorrectos.';
        } else if (e.code === 'auth/invalid-email') {
            msg = 'Formato de correo inválido.';
        }
        errorEl.innerText = msg;
        errorEl.classList.remove('hidden');
    }
}

async function handleResetPassword() {
    const email = document.getElementById('login-email').value.trim();
    const errorEl = document.getElementById('login-error');
    errorEl.classList.add('hidden');

    if (!email) {
        errorEl.innerText = 'Por favor, escribe tu correo electrónico arriba antes de hacer clic aquí.';
        errorEl.classList.remove('hidden');
        return;
    }

    showLoading('Enviando enlace...');
    try {
        await auth.sendPasswordResetEmail(email);
        hideLoading();
        alert('Te hemos enviado un correo con un enlace seguro. Ábrelo para crear o cambiar tu contraseña (revisa también tu carpeta de Spam).');
    } catch (e) {
        hideLoading();
        let msg = 'Error al enviar el correo.';
        if (e.code === 'auth/user-not-found') msg = 'No existe una cuenta con este correo. Habla con el coordinador.';
        if (e.code === 'auth/invalid-email') msg = 'Formato de correo inválido.';
        errorEl.innerText = msg;
        errorEl.classList.remove('hidden');
    }
}

function handleLogout() {
    auth.signOut();
}

function openCoordinatorSection() {
    if (userRole !== 'coordinador') {
        alert('Acceso restringido exclusivamente a coordinadores.');
        return;
    }
    loadReportSelects();
    loadApiKey();
    showStep('step-report');
}

function saveApiKey() {
    const key = document.getElementById('gemini-api-key').value.trim();
    if (key) {
        localStorage.setItem('geminiApiKey', key);
        alert('Clave de Gemini guardada de forma segura en este navegador.');
    } else {
        localStorage.removeItem('geminiApiKey');
        alert('Clave eliminada del navegador.');
    }
}

function loadApiKey() {
    const key = localStorage.getItem('geminiApiKey');
    if (key) {
        document.getElementById('gemini-api-key').value = key;
    }
}

/* ========================================================
   NIVELES DE CALIFICACIÓN
   ======================================================== */
const SCORE_LEVELS = [
    { key: 'insuficiente',  label: 'Insuficiente',  range: '0.0 – 2.9', cls: 'insuficiente'  },
    { key: 'aceptable',     label: 'Aceptable',     range: '3.0 – 3.5', cls: 'aceptable'     },
    { key: 'bueno',         label: 'Bueno',         range: '3.6 – 4.5', cls: 'bueno'         },
    { key: 'sobresaliente', label: 'Sobresaliente', range: '4.6 – 5.0', cls: 'sobresaliente'  },
    { key: 'na',            label: 'No aplica',     range: '',           cls: 'no-aplica'     }
];

const LEVEL_RANGES = {
    insuficiente:  { min: 0.0, max: 2.9, step: 0.1, default: 2.0 },
    aceptable:     { min: 3.0, max: 3.5, step: 0.1, default: 3.0 },
    bueno:         { min: 3.6, max: 4.5, step: 0.1, default: 4.0 },
    sobresaliente: { min: 4.6, max: 5.0, step: 0.1, default: 5.0 },
    na:            { min: 0,   max: 0,   step: 0,   default: null }
};

const itemSelections = {};

/* ========================================================
   ASIGNATURAS Y RÚBRICA
   ======================================================== */
const subjectsYear1 = [
    "Atención del parto y cuidados básicos del recién nacido",
    "Seguimiento del niño y el adolescente sano y en riesgo",
    "Psiquiatría pediátrica",
    "Hospitalización pediátrica tercer nivel fundamentación",
    "Neumología y alergología pediátrica",
    "Neurología y rehabilitación pediátrica",
    "Urgencias pediátricas III nivel de fundamentación"
, "Infectología pediátrica"];


const rubricStructureYear3 = [
    {
        category: "Conocimientos académicos",
        items: [
            { id: "rm_c_academico_y3", title: "Conocimientos y aprendizaje", desc: "Demuestra dominio experto de la literatura reciente, guías de manejo y aplica pensamiento crítico para resolver casos complejos.", weight: 0.25 }
        ]
    },
    {
        category: "Competencias clínicas",
        items: [
            { id: "rm_c_anamnesis_y3", title: "Anamnesis", desc: "Realiza anamnesis exhaustiva, identificando sutiles determinantes sociales y correlacionando hallazgos complejos con la fisiopatología.", weight: 0.10 },
            { id: "rm_c_fisico_y3", title: "Examen físico", desc: "Dirige el examen físico a hallazgos avanzados, reconociendo signos clínicos atípicos y sutilezas semiológicas.", weight: 0.10 },
            { id: "rm_c_analisis_y3", title: "Análisis y síntesis", desc: "Elabora diagnósticos diferenciales complejos, justificando cada uno con evidencia sólida y un raciocinio fisiopatológico impecable.", weight: 0.15 },
            { id: "rm_c_plan_y3", title: "Plan de manejo", desc: "Diseña planes de manejo integrales y costo-efectivos, liderando al equipo multidisciplinario y anticipando complicaciones.", weight: 0.15 }
        ]
    },
    {
        category: "Habilidades de comunicación y Profesionalismo",
        items: [
            { id: "rm_c_comunicacion_y3", title: "Comunicación y trabajo en equipo", desc: "Se comunica de forma asertiva y empática en situaciones difíciles, transmitiendo información compleja con claridad y liderando el equipo.", weight: 0.10 },
            { id: "rm_c_profesionalismo_y3", title: "Profesionalismo", desc: "Lidera con el ejemplo ético, asumiendo responsabilidad absoluta sobre sus pacientes y orientando a los residentes de menor año.", weight: 0.15 }
        ]
    }
];

const rubricSeminarioYear3 = [
    {
        category: "Seminario / Actividad Académica (Nivel Profundización)",
        items: [
            { id: "sem_dominio_y3", title: "Dominio del tema y evidencia", desc: "Dominio absoluto del tema, integrando conceptos moleculares, fisiopatológicos y clínicos avanzados con evidencia actual.", weight: 0.40 },
            { id: "sem_analisis_y3", title: "Análisis crítico", desc: "Critica constructivamente la literatura existente, proponiendo nuevas perspectivas o áreas de incertidumbre clínica.", weight: 0.30 },
            { id: "sem_pedagogia_y3", title: "Habilidades pedagógicas", desc: "Lidera la discusión académica estimulando el razonamiento crítico en el auditorio y respondiendo preguntas complejas con solvencia.", weight: 0.20 },
            { id: "sem_tiempo_y3", title: "Manejo del tiempo y síntesis", desc: "Logra una síntesis perfecta, optimizando el tiempo para favorecer el debate de alto nivel.", weight: 0.10 }
        ]
    }
];

const rubricSeminario = [
    {
        category: "Contenido Científico (100%)",
        items: [
            {
                id: "sem_dominio", title: "Dominio del tema",
                desc: "Demuestra conocimiento, responde preguntas y usa terminología.",
                weight: 0.35,
                details: {
                    insuficiente: "Conocimiento insuficiente, explicaciones confusas, no responde preguntas.",
                    aceptable: "Conocimiento aceptable, áreas de confusión. Responde de manera limitada.",
                    bueno: "Buen conocimiento, algunas áreas requieren mayor claridad. Responde adecuadamente.",
                    sobresaliente: "Excelente conocimiento, explicaciones claras, precisas, responde correctamente todo."
                }
            },
            {
                id: "sem_correlacion", title: "Correlación básico-clínica",
                desc: "Integra conceptos básicos con la clínica y ejemplos.",
                weight: 0.30,
                details: {
                    insuficiente: "No logra correlacionar conceptos básicos con la clínica o lo hace erróneamente.",
                    aceptable: "Correlación básica aceptable, ejemplos limitados o poco precisos.",
                    bueno: "Buena correlación, aunque faltan ejemplos o están mal explicados.",
                    sobresaliente: "Integra de manera excelente, ejemplos claros y bien contextualizados."
                }
            },
            {
                id: "sem_argumentacion", title: "Capacidad de argumentación",
                desc: "Sustenta ideas con evidencia científica y lógica.",
                weight: 0.20,
                details: {
                    insuficiente: "Sin argumentación coherente o clara, ideas mal organizadas, sin evidencia.",
                    aceptable: "Argumentación básica, ideas mal desarrolladas, falta evidencia o incoherencias.",
                    bueno: "Argumentación adecuada, falta profundidad en evidencia.",
                    sobresaliente: "Argumentación sólida, coherente, basada en evidencia, defiende ideas."
                }
            },
            {
                id: "sem_claridad", title: "Claridad y organización",
                desc: "Estructura, orden lógico y comprensión del tema.",
                weight: 0.15,
                details: {
                    insuficiente: "Exposición caótica, sin orden lógico, impide comprensión.",
                    aceptable: "Comprensible pero falta estructura o hay momentos confusos.",
                    bueno: "Exposición adecuada, algunos momentos de desorganización.",
                    sobresaliente: "Clara, bien estructurada, orden lógico, facilita comprensión."
                }
            }
        ]
    }
];


const rubricMiniCex = [
    {
        category: "Mini-CEX (Escala de 1 a 9)",
        items: [
            { id: "mc1", weight: 0.125, title: "Anamnesis del paciente y/o acudiente", desc: "Facilita la narración del paciente y/o acudiente. Utiliza preguntas adecuadas de manera eficaz. Realiza un interrogatorio completo del motivo de consulta, enfermedad actual y antecedentes (patológicos, quirúrgicos, alérgicos, inmunizaciones, familiares). Responde adecuadamente a mensajes claves verbales y no verbales." },
            { id: "mc2", weight: 0.125, title: "Examen físico del paciente", desc: "Sigue una secuencia lógica y eficiente céfalo caudal. Exploración centrada en el problema clínico. Informa al paciente. Respeta la comodidad del paciente." },
            { id: "mc3", weight: 0.125, title: "Juicio clínico, análisis y diagnósticos diferenciales", desc: "Realiza un diagnóstico apropiado y tiene en cuenta los diagnósticos diferenciales. Analiza de forma apropiada y crítica los diagnósticos." },
            { id: "mc4", weight: 0.125, title: "Plan de manejo (tratamiento y ayudas diagnósticas)", desc: "Establece un plan terapéutico acorde al diagnóstico. Propone ayudas diagnósticas pertinentes y completas, considerando los riesgos y beneficios." },
            { id: "mc5", weight: 0.125, title: "Habilidades comunicativas", desc: "Utiliza un lenguaje claro para el paciente. Es empático. Es honesto y pertinente. Explica al paciente el diagnóstico y el plan. Educa al paciente y a su familia." },
            { id: "mc6", weight: 0.125, title: "Organización / eficiencia", desc: "Prioriza. Se ajusta al tiempo. Es concreto." },
            { id: "mc7", weight: 0.125, title: "Profesionalismo", desc: "Muestra respeto por el paciente y su familia. Establece confianza y una buena relación. Guarda la confidencialidad de la historia clínica. Considera los aspectos legales relevantes." },
            { id: "mc8", weight: 0.125, title: "Evaluación clínica global", desc: "Demuestra de forma satisfactoria el juicio clínico, síntesis y efectividad. Utiliza adecuadamente los recursos. Es consciente de sus propias limitaciones." }
        ]
    }
];
const rubricTemaCentral = [
    {
        category: "Contenido Científico y Presentación (100%)",
        items: [
            {
                id: "tc_dominio", title: "Dominio del tema",
                desc: "Conocimiento, explicaciones y terminología.",
                weight: 0.25,
                details: {
                    insuficiente: "No demuestra conocimiento, explicaciones incorrectas/confusas.",
                    aceptable: "Conocimiento básico, explicaciones confusas, uso incorrecto de terminología.",
                    bueno: "Conoce bien, algunas explicaciones confusas, errores menores.",
                    sobresaliente: "Conocimiento profundo, mayormente claras, imprecisiones menores.",
                    excelente: "Dominio completo, explicaciones claras, sin errores, responde a todas las preguntas."
                }
            },
            {
                id: "tc_correlacion", title: "Correlación básico-clínica",
                desc: "Integración de conceptos y ejemplos relevantes.",
                weight: 0.20,
                details: {
                    insuficiente: "No hay correlación clara, sin ejemplos o mal aplicados.",
                    aceptable: "Correlación limitada, ejemplos inadecuados, dificulta comprensión.",
                    bueno: "Correlación básica, ejemplos no siempre claros.",
                    sobresaliente: "Integra bien, ejemplos pertinentes, falta algo de profundidad.",
                    excelente: "Integra conceptos con gran precisión, ejemplos relevantes y aplicados."
                }
            },
            {
                id: "tc_argumentacion", title: "Capacidad de argumentación",
                desc: "Argumentos estructurados y basados en evidencia.",
                weight: 0.20,
                details: {
                    insuficiente: "No desarrolla argumentos coherentes ni base científica.",
                    aceptable: "Argumentación débil, razonamientos poco claros, evidencia insuficiente.",
                    bueno: "Argumentación coherente, evidencia suficiente pero no robusta.",
                    sobresaliente: "Argumenta claro y fundamentado, falta profundidad en detalles.",
                    excelente: "Argumentos coherentes, estructurados, fundamentados y defiende bien puntos."
                }
            },
            {
                id: "tc_claridad", title: "Claridad y organización",
                desc: "Estructura, orden y fluidez de la exposición.",
                weight: 0.15,
                details: {
                    insuficiente: "Presentación caótica, confusa, sin orden lógico.",
                    aceptable: "Presentación desorganizada, interrupciones o falta de coherencia.",
                    bueno: "Presentación comprensible, fluidez intermitente, partes confusas.",
                    sobresaliente: "Mayormente clara y estructurada, exposición fluida en su mayoría.",
                    excelente: "Clara, bien estructurada, orden lógico, fluida sin interrupciones."
                }
            },
            {
                id: "tc_ayudas", title: "Ayudas didácticas",
                desc: "Calidad e integración de recursos visuales.",
                weight: 0.10,
                details: {
                    insuficiente: "Sin recursos visuales o de muy baja calidad, no aportan.",
                    aceptable: "Recursos insuficientes o mal utilizados, no aportan significativamente.",
                    bueno: "Recursos funcionales, no siempre bien integrados, aportan algo.",
                    sobresaliente: "Recursos adecuados y bien utilizados, podrían mejorarse.",
                    excelente: "Recursos visuales de alta calidad, bien integrados, facilitan comprensión."
                }
            },
            {
                id: "tc_entorno", title: "Adaptación a entorno virtual",
                desc: "Manejo de plataforma, audio/video e interacción.",
                weight: 0.10,
                details: {
                    insuficiente: "No maneja bien plataforma, problemas graves, sin interacción.",
                    aceptable: "Problemas técnicos frecuentes, interacción insuficiente.",
                    bueno: "Maneja plataforma con problemas menores, interacción limitada.",
                    sobresaliente: "Maneja bien, pequeños problemas técnicos, interacción adecuada.",
                    excelente: "Maneja plataforma con destreza, excelente audio/video, interacción fluida."
                }
            }
        ]
    }
];

const rubricStructure = [
    {
        category: "Conocimientos académicos (25%)",
        items: [{
            id: "c_acad", title: "Conocimientos académicos",
            desc: "Nivel de actualización, organización y lectura crítica de la evidencia.",
            weight: 0.25,
            details: {
                insuficiente:  "Conocimientos desactualizados, desorganizados o inconsistentes para su nivel; no aplica ni contrasta con evidencia científica.",
                aceptable:     "Conocimientos básicos para su nivel, con aplicabilidad limitada; lectura crítica ocasional de la evidencia.",
                bueno:         "Según su nivel son adecuados, organizados, consistentes y sólidos; tienen aplicabilidad y están actualizados; hace lectura crítica de la mejor evidencia.",
                sobresaliente: "Conocimientos que superan lo esperado para su nivel; integra evidencia de vanguardia y la aplica con criterio propio."
            }
        }]
    },
    {
        category: "Habilidad práctica (25%)",
        items: [
            {
                id: "h_historia", title: "Abordaje historia clínica",
                desc: "Metódica, profunda, íntegra, veraz y oportuna.", weight: 0.12,
                details: { insuficiente: "Historia clínica incompleta, desorganizada, omite datos críticos.", aceptable: "Historia clínica básica, a veces omite detalles relevantes.", bueno: "Historia metódica, profunda e íntegra.", sobresaliente: "Historia clínica excepcional, veraz, oportuna y enfocada al contexto del paciente." }
            },
            {
                id: "h_tecnico", title: "Desempeño técnico",
                desc: "Disposición, oportunidad, ingenio, recursividad, eficiencia.", weight: 0.13,
                details: { insuficiente: "Dificultad evidente en habilidades técnicas básicas.", aceptable: "Desempeño técnico aceptable pero requiere supervisión constante.", bueno: "Buen desempeño técnico, recursivo y eficiente.", sobresaliente: "Altamente ingenioso, eficiente y seguro en su desempeño técnico." }
            }
        ]
    },
    {
        category: "Criterio clínico (25%)",
        items: [
            {
                id: "cr_anamnesis", title: "Anamnesis y examen clínico",
                desc: "Ordenado, completo, con énfasis en la situación clínica.", weight: 0.05,
                details: { insuficiente: "Examen físico incompleto o sin correlación clínica.", aceptable: "Examen físico estándar, le falta énfasis en el problema actual.", bueno: "Examen ordenado y completo, dirigido a la situación.", sobresaliente: "Examen físico exhaustivo, preciso y con excelente razonamiento." }
            },
            {
                id: "cr_examenes", title: "Solicitud e interpretación de exámenes",
                desc: "Racionalidad, oportunidad, utilidad y articulación.", weight: 0.10,
                details: { insuficiente: "Solicita exámenes sin justificación o interpreta erróneamente.", aceptable: "Solicitud adecuada pero le cuesta articular los resultados.", bueno: "Uso racional y oportuno de ayudas diagnósticas.", sobresaliente: "Excelente utilidad, racionalidad y articulación clínica de los exámenes." }
            },
            {
                id: "cr_diagnostico", title: "Impresión diagnóstica y conducta terapéutica",
                desc: "Precisión, claridad, consistencia, responsabilidad.", weight: 0.10,
                details: { insuficiente: "Impresión diagnóstica errada y plan terapéutico inseguro.", aceptable: "Diagnósticos básicos correctos, plan terapéutico requiere ajustes.", bueno: "Diagnósticos precisos y conducta terapéutica consistente.", sobresaliente: "Alta precisión diagnóstica y responsabilidad en terapias complejas." }
            }
        ]
    },
    {
        category: "Compromiso (25%)",
        items: [
            {
                id: "co_seguridad", title: "Con la seguridad del paciente y su familia",
                desc: "Calidez, consideración, respeto, interés, paciencia.", weight: 0.08,
                details: { insuficiente: "Falta de empatía, irrespeta normas de seguridad.", aceptable: "Trato cordial, cumple normas básicas de seguridad.", bueno: "Trato cálido, considerado e interés genuino por el paciente.", sobresaliente: "Modelo a seguir en paciencia, respeto y seguridad del paciente." }
            },
            {
                id: "co_equipo", title: "Con el equipo de trabajo",
                desc: "Colaboración, solidaridad, respeto y lealtad.", weight: 0.08,
                details: { insuficiente: "Conflictivo, no colabora con el equipo.", aceptable: "Relación funcional con el equipo, participación pasiva.", bueno: "Colaborador, solidario y respetuoso con sus pares y superiores.", sobresaliente: "Líder positivo, fomenta la lealtad y el trabajo en equipo." }
            },
            {
                id: "co_academico", title: "Con actividades académicas e investigación",
                desc: "Interés, constancia, creatividad, puntualidad.", weight: 0.09,
                details: { insuficiente: "Impuntual, falta de interés en actividades académicas.", aceptable: "Asiste a actividades académicas pero participa poco.", bueno: "Interés constante, puntual y participativo.", sobresaliente: "Aporta creativamente, excelente nivel investigativo y académico." }
            }
        ]
    }
];

/* ========================================================
   MICROCURRÍCULOS (contexto para Gemini IA)
   ======================================================== */
const MICROCURRICULOS = {

    "Hospitalización pediátrica III nivel profundización": "1. Conoce la fisiopatología, abordaje diagnóstico y terapéutico de patologías intrahospitalarias complejas.\n2. Establece un plan de manejo de líquidos y electrolitos evitando la sobrecarga.\n3. Maneja las diferentes formas de administración de oxígeno suplementario.\n4. Conoce indicaciones y complicaciones de transfusiones de hemoderivados.\n5. Establece planes de egreso hospitalario.\n6. Aplica estrategias de manejo en paciente con descompensación aguda (código sepsis, alerta temprana, etc.).",
    "Infectología pediátrica": "1. Reconoce la epidemiología, historia natural y fisiopatología de infecciones.\n2. Describe herramientas diagnósticas.\n3. Conoce principios de manejo farmacológico y uso de antibiograma.\n4. Conoce el uso racional de antibióticos y desescalonamiento.\n5. Conoce principios de resistencia antimicrobiana.\n6. Realiza educación sobre el uso responsable de antibióticos.",

    "Atención del parto y cuidados básicos del recién nacido": `ASIGNATURA: Atención del parto y cuidados básicos del recién nacido.
JUSTIFICACIÓN: Los pediatras deben anticipar y manejar las necesidades médicas del recién nacido a término normal y prematuro tardío en sala de partos, manejar condiciones que no requieren UCI, hacer seguimiento en alojamiento conjunto y dar manejo a condiciones del período neonatal.
COMPETENCIAS ESPECÍFICAS: Identificar y aplicar pautas basadas en evidencia para atención del recién nacido. Proporcionar atención de rutina y abordar problemas en los primeros 28 días. Asesoría en lactancia materna, uso de sucedáneos y puericultura neonatal. Juicio clínico para problemas comunes del recién nacido en el hogar. Generar confianza en padres. Direccionar tamizajes neonatales. Fisiología normal y patológica del recién nacido. Habilidades de adaptación neonatal y reanimación. Preparación del niño que requiere traslado.
SABERES ESENCIALES: Evaluación y organización del cuidado neonatal; niveles asistenciales. Hijo de madre con infección perinatal. Hijo de madre consumidora de sustancias. Embarazos múltiples. Crecimiento fetal y RCIU. Enfermedades crónicas maternas y repercusión fetal. RN con ictericia, sepsis, enterocolitis, hipoalimentación. Diagnóstico prenatal. Atención y estabilización inicial del RN. Resucitación cardiopulmonar neonatal. Examen general y valoración neurológica del neonato. Cuidados del RN normal a término y postérmino. Lactancia materna y leche de fórmula. Tamizaje y vacunación neonatal. Evaluación en alojamiento conjunto. Transporte neonatal (STABLE).
DESENLACES: Criterios de ingreso/alta en unidad de cuidado básico neonatal. Embriología y desarrollo fetal. Cambios fisiológicos del RN hasta día 28. Adaptación neonatal en sala de partos. Identificar paciente que requiere reanimación neonatal. Patologías y riesgos maternos que afectan al RN. Examen físico para variaciones normales y anomalías congénitas. Patologías en primeros 28 días. Puericultura del RN. Tamizajes necesarios. Lactancia materna. Transporte neonatal.`,

    "Seguimiento del niño y el adolescente sano y en riesgo": `ASIGNATURA: Seguimiento del niño y el adolescente sano y en riesgo.
JUSTIFICACIÓN: El cuidado ambulatorio requiere un abordaje empático e integrado entre paciente, familia y atención primaria. El pediatra debe ser facilitador clave de la atención centrada en el paciente, proporcionar cuidado ambulatorio para niños de todas las edades, identificar necesidades en el contexto comunitario y coordinar la atención integral.
COMPETENCIAS ESPECÍFICAS: Conocimiento de fisiología normal, epidemiología y estándares de práctica para todos los grupos de edad. Relación terapéutica altamente efectiva con pacientes y familias. Evaluación integral del paciente ambulatorio. Identificación de recursos y coordinación de atención. Atención primaria, seguimiento del niño sano y detección temprana de patologías. Programas de detección temprana (PAI, AIEPI, tamizaje ocular, detección temprana de cáncer). Reconocer límites de atención ambulatoria y momento de remisión. Educación en puericultura.
SABERES ESENCIALES: Patrones normales de crecimiento. Nutrición y transiciones dietéticas. Hitos del desarrollo motor, lingüístico y cognitivo. Salud socioemocional normal. Calendario de vacunación. Tamizaje apropiado para la edad. Puericultura. Orientación anticipatoria. TEA. Retraso del neurodesarrollo. Parálisis cerebral. Detección temprana de cáncer. Sospechas reumatológicas y endocrinológicas. Anomalías congénitas. Seguimiento de patologías GI, hematológica, pulmonar y nefro-urológica ambulatoria.
DESENLACES: Historia clínica completa enfocada en seguimiento del niño sano. Esquema de vacunación colombiano. Valoración nutricional completa. Estrategia AIEPI. Fisiopatología y abordaje de patologías ambulatorias. Comunicación efectiva y educativa con familias.`,

    "Psiquiatría pediátrica": `ASIGNATURA: Psiquiatría pediátrica.
JUSTIFICACIÓN: Prevalencia de trastornos mentales infantiles del 13-20%, con 4-6% graves y 10% con deterioro funcional. El 75% de los niños no recibe atención adecuada. La AAP emitió en 2019 competencias de salud mental para la práctica pediátrica. El pediatra debe hacer abordaje inicial, exploración y orientación familiar.
COMPETENCIAS ESPECÍFICAS: Identificar estrategias de valoración en salud mental (entrevista clínica, valoración sociofamiliar, escalas validadas). Abordaje sintomático inicial de dificultades de salud mental y conductuales. Habilidades de comunicación fundamentales. Herramientas de salud mental en promoción y prevención primaria/secundaria. Terapias psicofarmacológicas según guías actuales. Trabajo en equipo multidisciplinario (hospitalario y ambulatorio).
SABERES ESENCIALES: Entrevista clínica y uso de escalas. Diagnósticos sindromáticos de salud mental en pediatría. Guías para trastornos mentales más frecuentes. Enfoque de factores comunes HELP (AAP).
DESENLACES: Promoción del desarrollo emocional saludable y prevención primaria. Abordaje rutinario de historial biopsicosocial según edad. Identificar factores de riesgo y síntomas emergentes. Reconocer límites de atención y necesidad de remisión. Emergencias de salud mental (suicidio, psicosis, riesgo auto/heteroagresivo). Diagnósticos más comunes (depresión, ansiedad, TDAH). Habilidades de comunicación para acceso a servicios. Abordaje farmacológico inicial.`,

    "Hospitalización pediátrica tercer nivel fundamentación": `ASIGNATURA: Hospitalización pediátrica III nivel fundamentación.
JUSTIFICACIÓN: El pediatra debe dominar el manejo de patologías que requieren hospitalización, establecer plan de manejo con fecha de egreso, seguimiento frecuente, identificación de deterioro y necesidad de transferencia, así como plan de egreso y manejo en casa. Implica conocimiento de fisiopatología, cambios de la hospitalización y farmacología.
COMPETENCIAS ESPECÍFICAS: Atención centrada en el paciente hospitalizado en tercer nivel. Historia clínica, examen físico completo y diagnóstico diferencial. Epidemiología, fisiopatología e historia natural de patologías de tercer nivel. Abordaje diagnóstico y terapéutico intrahospitalario diario. Principios de investigación clínica y MBE. Plan farmacológico y no farmacológico basado en farmacocinética y farmacodinamia. Anticipar complicaciones de terapia médica. Manejo multidisciplinario. Reconocimiento temprano de cambios agudos y transferencia. Procedimientos básicos (canalización venosa, sonda vesical, sonda gástrica, punción lumbar). Compromiso con calidad, compasión y respeto. Integración de mejor evidencia a práctica clínica.
SABERES ESENCIALES: Líquidos y electrolitos pediátricos. Enfermedades respiratorias (neumonía, asma, bronquiolitis, sistemas de oxigenación). Enfermedades infecciosas (ITU, osteomusculares, fiebre sin foco, piel y tejidos blandos). Patología crónica descompensada. Manejo posoperatorio pediátrico. Paciente con parálisis cerebral. Paciente con síndrome de Down. Manejo del dolor. Enfermedades exantemáticas.
DESENLACES: Cálculo de líquidos y electrolitos. Fisiopatología de principales enfermedades, abordaje diagnóstico y terapéutico. Evaluación y manejo del dolor. Sistemas de oxigenación. Evaluación nutricional y tamizaje de desnutrición. Parámetros diferenciales en condiciones patológicas. Manejo posoperatorio sistematizado. Interpretación de estudios paraclínicos e imagenológicos. Puericultura y cuidado al egreso.`,

    "Neumología y alergología pediátrica": `ASIGNATURA: Neumología y alergología pediátrica.
JUSTIFICACIÓN: El pediatra EIA debe tener competencias en abordaje, sospecha diagnóstica, detección y manejo del niño con patología del tracto respiratorio superior e inferior, desde atención primaria hasta cuidado crítico, en todas las edades desde recién nacido hasta adolescente. Debe conocer estrategias de tamizaje y educación.
COMPETENCIAS ESPECÍFICAS: Embriología, anatomía y fisiología respiratoria en diferentes etapas de la vida. Factores biológicos y ambientales de enfermedades respiratorias. Epidemiología, etiología e historia natural. Pruebas diagnósticas, indicaciones y limitaciones. Intervenciones terapéuticas farmacológicas y no farmacológicas. Historia clínica y examen físico completo. Diagnóstico diferencial de problemas respiratorios agudos y crónicos. Herramientas estandarizadas de seguimiento. Prescripción e interpretación de laboratorio e imágenes. Sospecha diagnóstica e indicaciones de remisión a neumología. Tratamiento adecuado a la edad. Plan de tratamiento a largo plazo de enfermedades crónicas. Trabajo colaborativo. Educación a pacientes y familias. Autoevaluación de pacientes con enfermedades crónicas. Análisis crítico de evidencia.
SABERES ESENCIALES: Epidemiología de enfermedad respiratoria pediátrica. Fisiología y embriología respiratoria normal. Patofisiología de bronquiolitis, asma, fibrosis quística, neumonía, tuberculosis. Procedimientos (fibrobroncoscopia, polisomnografía). Ayudas diagnósticas (radiografía, tomografía, electrolitos en sudor). Escalas de clasificación de riesgo y severidad.
DESENLACES: Identificar paciente que requiere abordaje dirigido y remisión a neumología. Detectar riesgos de enfermedad pulmonar y prevenir complicaciones. Educar en adherencia farmacológica y no farmacológica. Identificar problemas respiratorios y aproximación terapéutica. Interpretar ayudas diagnósticas. Dispositivos de oxígeno. Evaluación secuencial de radiografía de tórax. Indicaciones de pruebas diagnósticas. Farmacocinética y farmacodinamia de fármacos respiratorios. Programas de detección de riesgos.`,

    "Neurología y rehabilitación pediátrica": `ASIGNATURA: Neurología y rehabilitación pediátrica.
JUSTIFICACIÓN: El pediatra EIA debe tener competencias en seguimiento del neurodesarrollo del niño sano, tamizaje de riesgo neurológico, abordaje diagnóstico y manejo del niño con patología neurológica aguda y crónica, desde atención primaria hasta intrahospitalaria. Debe conocer estrategias de tamizaje y educación.
COMPETENCIAS ESPECÍFICAS: Embriología, anatomía y semiología del SNC en etapas de desarrollo. Hitos normales del neurodesarrollo y semiología de la entrevista y examen neurológico. Factores de riesgo biológicos y ambientales para enfermedades neurológicas. Epidemiología, etiología e historia natural. Herramientas de laboratorio e imagenología. Intervenciones terapéuticas farmacológicas y no farmacológicas. Diagnóstico diferencial de patologías neurológicas agudas. Bases fisiopatológicas de enfermedad neurológica aguda y crónica. Abordaje estructurado por problemas. Factores importantes en seguimiento de patología crónica. Herramientas de tamizaje. Prescripción e interpretación de pruebas. Trabajo multidisciplinario. Educación a familias. Análisis crítico de evidencia. Interpretación de pruebas diagnósticas. Manejo integral del paciente neurológico.
SABERES ESENCIALES: Semiología neurológica pediátrica. Neurodesarrollo normal. Niño con hipotonía. Abordaje de primera convulsión. Síndromes epilépticos en la infancia. Retardo en neurodesarrollo (motor, fino, lenguaje). Parálisis cerebral. Infecciones del SNC. Enfermedades autoinmunes del SNC. Alteración del sensorio. Cefalea y migraña. Hipertensión intracraneal. Parálisis flácidas agudas. Compromiso de médula espinal. Alteraciones del movimiento. Síndrome de Down y TEA. ACV y malformaciones arteriovenosas. Facomatosis.
DESENLACES: Anamnesis y examen físico enfocado en enfermedad neurológica. Evaluación de hitos del neurodesarrollo y desviaciones. Identificar factores de riesgo. Interpretar pruebas diagnósticas. Fisiopatología de enfermedades neurológicas. Principios de neurofármacos. Pruebas de tamizaje. Comunicación asertiva con padres. Rol docente activo con estudiantes de pregrado.`,

    "Urgencias pediátricas III nivel de fundamentación": `ASIGNATURA: Urgencias pediátricas III nivel de fundamentación.
JUSTIFICACIÓN: El pediatra egresado de la Universidad requiere tener conocimientos robustos en la atención de emergencias pediátricas en los niños que se presenten en los diferentes niveles de complejidad. Al enfrentarse al paciente con enfermedad aguda que asiste a un tercer nivel de atención, se hace necesario integrar la fisiología del niño sano y del que se presenta con una condición aguda que requiere priorización, estabilización y en muchas ocasiones manejo interdisciplinario y uso adecuado de la tecnología y los recursos disponibles.
COMPETENCIAS ESPECÍFICAS: Identifica el niño que requiere atención prioritaria al presentarse al servicio de emergencias de un tercer nivel de complejidad. Mediante el uso del abordaje primario y secundario, realiza una aproximación y manejo inicial y systematizado basado en la etiología y a su vez estabilización del niño que consulta al servicio de urgencias del tercer nivel de atención. Integra la fisiología y fisiopatología de la agudización con la epidemiología local como datos relevantes para realizar diagnósticos diferenciales en el niño que ingresa al servicio de urgencias. Conoce, utiliza e interpreta en forma racional las ayudas diagnósticas a partir de la historia clínica realizada. Conoce las principales medidas terapéuticas farmacológicas y no farmacológicas para el manejo de las patologías más frecuentes en urgencias de tercer nivel de atención. Participa de forma activa en la estabilización inicial del paciente que ingresa por descompensación aguda al servicio de urgencias. Conoce y desarrolla procedimientos en la sala de emergencia, de manera supervisada como lo son la punción lumbar, manejo básico y avanzado de la vía aérea, acceso intraóseo. Utiliza el abordaje ecográfico al lado de cama del paciente de forma racional para la aproximación de la patología del niño que consulta a urgencias de tercer nivel de atención. Comunica la información pertinente e interactúa en forma asertiva con pacientes, familia y los demás miembros del equipo de salud. Realiza adecuadamente el soporte vital básico y avanzado pediátrico de manera supervisada. Comprende la importancia de los procesos encaminados a la seguridad del paciente, como la prescripción de medicamentos las órdenes verbales y la identificación de riesgos. Selecciona, analiza críticamente y resume la información científica actualizada para preparar y presentar clubes de revistas, seminarios y exposiciones. Realiza actividades educativas a padres, familiares, colegas y estudiantes en relación a la detección temprana de condiciones críticas del niño.
SABERES ESENCIALES: Interpretación de gases arteriales. Abordaje primario (ABCDE) y secundario del niño que ingresa a urgencias. Insuficiencia respiratoria aguda. Choque y sus diferentes tipos: hipovolémico, distributivo, obstructivo y cardiogénico. Paciente con compromiso del sensorio. Paciente con convulsiones y estado convulsivo. Abordaje del paciente quemado. El niño con BRUE. Paciente politraumatizado. Cetoacidosis diabética y estado hiperosmolar hiperglicemico. El niño con cáncer que ingresa al servicio de urgencias. Trauma no accidental y abuso. Trauma craneoencefalico grave. Intoxicaciones frecuentes. Transporte del paciente crítico.
DESENLACES: Realizar una aproximación inicial a través del triángulo de aproximación pediátrica y el ABCDE y secundaria mediante la historia clínica y examen físico completo que permita priorizar y hacer un abordaje oportuno del niño que ingresa al servicio de urgencias. Reconoce y clasifica el niño que requiere atención inmediata en el servicio de urgencias. Reconoce los signos y síntomas específicos de las enfermedades pediátricas más frecuentes que se presentan en el servicio de urgencias de tercer nivel de complejidad y hace su estabilización inicial. Usa e integra el conocimiento de las ciencias básicas y la epidemiología para comprender e interpretar las enfermedades a la luz de los enfoques actuales. Identifica los estudios diagnósticos apropiados y racionales para cada patología. Realizar procedimientos acordes a su nivel de competencia en el servicio de urgencias: intubación orotraqueal, colocación de aguja intraósea, punción lumbar, paso de sonda orogástrica. Hace uso apropiado de la ecografía al pie de la cama, teniendo un estudio previo de sus variables físicas para la aproximación de paciente con enfermedad aguda. Demuestra un comportamiento ético y establecer una comunicación compasiva, respetuosa y asertiva con pacientes y familiares, así como con pares y equipo de salud, favoreciendo el trabajo en equipo. Identifica el niño en falla respiratoria y diferencia los tipos fisiopatológicos de falla respiratoria para su abordaje. Identifica el niño en choque y sus diferentes tipos para hacer un abordaje secuencial y una búsqueda etiológica activa. Establece un manejo estandarizado del niño con compromiso neurológico, infeccioso, hemato-oncológico basado en su fisiopatología y buscando una detección temprana de complicaciones que mejore resultados.`
};

let selectedSubjectName = "";
let reportEvaluations = []; // Evaluaciones encontradas para el informe

/* ========================================================
   INICIALIZACIÓN
   ======================================================== */
document.addEventListener('DOMContentLoaded', () => {
    renderSubjects();
    renderRubric();
    generateFullRubricTable();
});

function showStep(stepId) {
    document.querySelectorAll('.step').forEach(el => el.classList.add('hidden'));
    const stepEl = document.getElementById(stepId);
    if (!stepEl) {
        alert("ERROR: Tu navegador cargó una versión vieja de la página (caché). Presiona Ctrl + F5 o entra al enlace con ?v=3 al final.");
        console.error("No se encontró el elemento:", stepId);
        return;
    }
    stepEl.classList.remove('hidden');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}
function goBack(stepId) { showStep(stepId); }


function handleEvaluationTypeChange() {
    const evalType = document.getElementById('evaluation-type').value;
    const btnRubrica = document.querySelector('button[onclick="openFullRubric()"]');
    if (btnRubrica) {
        btnRubrica.style.display = (evalType === 'minicex') ? 'none' : 'inline-block';
    }
    const seminarNameContainer = document.getElementById('seminar-name-container');
    const seminarNameInput = document.getElementById('seminar-name');
    
    if (evalType === 'seminario' || evalType === 'tema_central' || evalType === 'minicex') {
        seminarNameContainer.classList.remove('hidden');
        seminarNameInput.required = true;
    } else {
        seminarNameContainer.classList.add('hidden');
        seminarNameInput.required = false;
        seminarNameInput.value = '';
    }

    renderRubric(); // Re-render rubric when type changes
}

const rubricRondaYear3 = [
    {
        category: "Evaluación de R3 (100%)",
        items: [
            {
                id: "r3_1", title: "Evaluación Clínica, Integración y Diagnóstico",
                desc: "Abordaje diagnóstico e integración fisiopatológica.",
                weight: 0.1666,
                details: {
                    insuficiente: "Diagnósticos superficiales. No integra la fisiopatología, patogénesis ni la historia natural de patologías complejas de tercer nivel.",
                    aceptable: "Plantea diagnósticos correctos, pero le cuesta integrar imágenes diagnósticas avanzadas o correlacionar múltiples comorbilidades.",
                    bueno: "Realiza un abordaje integrativo. Interpreta imágenes y paraclínicos complejos, estableciendo planes diagnósticos avanzados con gran autonomía clínica.",
                    sobresaliente: "Agudeza diagnóstica. Resuelve o propone estrategias para dilemas clínicos complejos, integrando literatura reciente para cuestionar y/o refinar los diagnósticos del equipo."
                }
            },
            {
                id: "r3_2", title: "Terapéutica, Fluidos y Uso Racional de ATB",
                desc: "Manejo farmacológico, hídrico y antibiótico.",
                weight: 0.1666,
                details: {
                    insuficiente: "Prescribe antibióticos sin justificación microbiológica. Errores en líquidos o manejo deficiente del dolor.",
                    aceptable: "Conoce las dosis, pero falla en la escalada/desescalada racional de antibióticos o en la individualización del manejo del dolor pediátrico.",
                    bueno: "Aplica un uso estrictamente racional de antibióticos. Maneja con maestría trastornos hidroelectrolíticos. Individualiza de manera brillante líquidos y analgesia multimodal.",
                    sobresaliente: "Adicionalmente, manejo de dolor, y transfusión de hemoderivados de manera personalizada."
                }
            },
            {
                id: "r3_3", title: "Alertamiento Temprano y Códigos de Emergencia",
                desc: "Respuesta al deterioro y urgencias.",
                weight: 0.1666,
                details: {
                    insuficiente: "Ignora signos de inestabilidad. No activa protocolos de emergencia frente al deterioro clínico evidente.",
                    aceptable: "Detecta el deterioro, pero depende del especialista para la activación y liderazgo de los códigos de respuesta rápida o sepsis.",
                    bueno: "Anticipa complicaciones y utiliza proactivamente escalas de alerta temprana. Manejo del código de sepsis, código lila y EVAT.",
                    sobresaliente: "Liderazgo excepcional en las tareas anteriores, además coordinando a todo el equipo antes del traslado a UCI o con dolor y cuidado paliativo."
                }
            },
            {
                id: "r3_4", title: "Liderazgo Clínico y Rol Docente",
                desc: "Liderazgo de equipo y educación.",
                weight: 0.1666,
                details: {
                    insuficiente: "Evita liderar la ronda clínica. No demuestra interés en enseñar a los médicos internos o residentes de menor año.",
                    aceptable: "Enseña ocasionalmente, pero sin una mediación pedagógica clara. No asume completamente su rol como líder del equipo de hospitalización.",
                    bueno: "Lidera las rondas y actividades de educación interprofesional. Orienta, corrige y apoya eficazmente a internos y R1/R2 durante los turnos.",
                    sobresaliente: "Es un educador clínico por iniciativa. Diseña escenarios de aprendizaje basado en casos que inspiran al equipo de trabajo."
                }
            },
            {
                id: "r3_5", title: "Gestión Multidisciplinaria y Medicina Basada en Evidencia",
                desc: "Trabajo en equipo interconsulta y lectura crítica.",
                weight: 0.1666,
                details: {
                    insuficiente: "Abordaje fragmentado. No lee ni aporta artículos científicos recientes para soportar sus decisiones en el Staff.",
                    aceptable: "Pide interconsultas sin un enfoque claro. Lee literatura básica pero le falta análisis crítico de la evidencia actual.",
                    bueno: "Articula de forma integral el manejo con las distintas subespecialidades. Realiza lectura crítica y aporta evidencia científica sólida en clubes de revista y Staffs.",
                    sobresaliente: "Integra a todas las disciplinas de manera magistral. Conoce los ensayos clínicos recientes de sus pacientes y los aplica para cambiar conductas terapéuticas en el servicio."
                }
            },
            {
                id: "r3_6", title: "Profesionalismo, Plan de Egreso y Malas Noticias",
                desc: "Comunicación empática y egreso seguro.",
                weight: 0.1670,
                details: {
                    insuficiente: "No sabe comunicar malas noticias. Delega el plan de egreso a los residentes menores sin supervisar la educación a la familia.",
                    aceptable: "Comunica diagnósticos difíciles, pero con falta de empatía o usando jerga excesiva. El plan de egreso carece de integralidad para el manejo en casa.",
                    bueno: "Aborda la comunicación de malas noticias con compasión, empatía y claridad. Prepara planes de egreso robustos, asegurando el seguimiento ambulatorio adecuado.",
                    sobresaliente: "Nivel superior de humanismo ('Hospital con Alma'). Contiene emocionalmente a las familias ante diagnósticos devastadores y asegura redes de apoyo interdisciplinarias para el egreso."
                }
            }
        ]
    }
];

function getCurrentRubric() {
    const evalType = document.getElementById('evaluation-type') ? document.getElementById('evaluation-type').value : 'ronda';
    if (evalType === 'seminario') return rubricSeminario;
    if (evalType === 'minicex') return rubricMiniCex;
    if (evalType === 'tema_central') return rubricTemaCentral;
    if (Number(selectedResidentYear) === 3) return rubricRondaYear3;
    return rubricStructure; // default Ronda Médica
}

/* ========================================================
   RÚBRICA – BOTONES + INPUT EXACTO
   ======================================================== */
function renderRubric() {
    const container = document.getElementById('rubric-table-container');
    container.innerHTML = '';
    const activeRubric = getCurrentRubric(document.getElementById('evaluation-type').value);
    
    // Initialize minicex slider defaults
    if (activeRubric === rubricMiniCex) {
        activeRubric.forEach(cat => cat.items.forEach(item => {
            itemSelections[item.id] = { level: 'minicex', value: (5/9)*5, raw: 5 };
        }));
    }

    activeRubric.forEach(cat => {
        const catDiv = document.createElement('div');
        catDiv.className = 'rubric-category';
        let legendHtml = '';
        if (activeRubric === rubricMiniCex) {
             legendHtml = '<p style="font-size: 0.85rem; font-weight: normal; margin-top: 5px; color: #555;">Califique de 1 a 9 de acuerdo al desempeño de él o la residente, siendo 9 el puntaje más alto.</p>';
        }
        catDiv.innerHTML = cat.category + legendHtml;
        container.appendChild(catDiv);

        cat.items.forEach(item => {
            if (activeRubric === rubricMiniCex) {
                itemSelections[item.id] = { level: 'minicex', value: (5/9)*5, raw: 5 };
            }
            const block = document.createElement('div');
            block.className = 'rubric-item-block';
            block.innerHTML = `
                <div class="rubric-item-header">
                    <div>
                        <span class="rubric-item-title">${item.title} <span class="rubric-item-weight">Peso: ${(item.weight * 100)}%</span></span>
                        <span class="rubric-item-desc">${item.desc}</span>
                    </div>
                </div>
                <div class="score-buttons" id="btns-${item.id}">
                    ${activeRubric === rubricMiniCex ? `
                        <div style="display:flex; align-items:center; width: 100%; margin-top: 15px; padding: 0 10px; justify-content: space-between;">
                            <span style="font-weight:bold; font-size:1.2rem; color: #d32f2f; margin-right:15px;">1</span>
                            <input type="range" min="1" max="9" value="5" class="minicex-slider" id="slider-${item.id}"
                                oninput="document.getElementById('slider-val-${item.id}').innerText = this.value; selectScoreMiniCex('${item.id}', this.value)"
                                style="flex-grow:1; cursor:pointer; height: 8px; border-radius: 4px; background: #ddd; outline: none;">
                            <span style="font-weight:bold; font-size:1.2rem; color: #43a047; margin-left:15px;">9</span>
                            <div style="background:var(--primary-color); color:white; border-radius:50%; width:40px; height:40px; display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:1.3rem; margin-left:10px;" id="slider-val-${item.id}">5</div>
                        </div>` 
                        :
                        SCORE_LEVELS.map(l => `
                        <button type="button" class="score-btn ${l.cls}" id="btn-${item.id}-${l.key}"
                            onclick="selectScore('${item.id}','${l.key}',this)">
                            <strong>${l.label}</strong><br><span style="font-weight:400;font-size:0.72rem;">${l.range}</span>
                        </button>`).join('')
                    }
                </div>
                <div class="score-input-row hidden" id="input-row-${item.id}"
                     style="padding:10px 15px;background:#f9fbfd;display:flex;align-items:center;gap:12px;border-top:1px solid #eee; ${activeRubric === rubricMiniCex ? 'display:none!important;' : ''}">
                    <label style="margin:0;font-size:0.88rem;white-space:nowrap;" for="exact-${item.id}">Nota (0.0 - 5.0):</label>
                    <input type="text" id="exact-${item.id}" inputmode="decimal"
                           style="width:110px;padding:8px 12px;font-size:1.1rem;font-weight:700;text-align:center;border:2px solid var(--primary-color);border-radius:8px;color:var(--primary-color);"
                           oninput="updateExactScore('${item.id}')"
                           onblur="clampScore('${item.id}')">
                    <span id="range-hint-${item.id}" style="font-size:0.82rem;color:#666;"></span>
                </div>
                ${item.details ? `<div class="item-guide">
                    <strong>Guía:</strong>
                    <span style="color:var(--danger);"> Insuf.: </span>${item.details.insuficiente} |
                    <span style="color:#9a6f00;"> Acep.: </span>${item.details.aceptable} |
                    <span style="color:var(--info);"> Bueno: </span>${item.details.bueno} |
                    <span style="color:#1a6b2e;"> Sobr.: </span>${item.details.sobresaliente}
                </div>` : ''}`;
            container.appendChild(block);
        });
    });
}


function selectScoreMiniCex(itemId, val) {
    const score9 = parseFloat(val);
    const score5 = (score9 / 9.0) * 5.0; // Convierte a escala de 5.0
    itemSelections[itemId] = { level: 'minicex', value: score5, raw: score9 };
}

function selectScore(itemId, levelKey, btnEl) {
    document.getElementById(`btns-${itemId}`).querySelectorAll('.score-btn').forEach(b => b.classList.remove('selected'));
    btnEl.classList.add('selected');

    const inputRow = document.getElementById(`input-row-${itemId}`);
    const exactInput = document.getElementById(`exact-${itemId}`);
    const rangeHint = document.getElementById(`range-hint-${itemId}`);

    if (levelKey === 'na') {
        inputRow.classList.add('hidden'); inputRow.style.display = 'none';
        itemSelections[itemId] = { level: 'na', value: null };
        return;
    }

    const range = LEVEL_RANGES[levelKey];
    exactInput.inputMode = "decimal";
    
    // Si no había nada o cambia de nivel, colocamos la nota sugerida por defecto
    if (!itemSelections[itemId] || itemSelections[itemId].level === 'na' || itemSelections[itemId].level !== levelKey) {
        exactInput.value = range.default.toString().replace('.', ',');
    }
    
    rangeHint.innerText = `(Ref. ${range.min}–${range.max} | libre 0.0 a 5.0)`;
    inputRow.classList.remove('hidden'); inputRow.style.display = 'flex';
    
    let parsedVal = parseFloat(exactInput.value.replace(',', '.'));
    itemSelections[itemId] = { level: levelKey, value: isNaN(parsedVal) ? range.default : parsedVal };
}

function updateExactScore(itemId) {
    const sel = itemSelections[itemId];
    if (!sel || sel.level === 'na') return;
    const exactInput = document.getElementById(`exact-${itemId}`);
    let val = parseFloat(exactInput.value.replace(',', '.'));
    if (!isNaN(val)) {
        itemSelections[itemId].value = val;
    }
}

function clampScore(itemId) {
    const sel = itemSelections[itemId];
    if (!sel || sel.level === 'na') return;
    const exactInput = document.getElementById(`exact-${itemId}`);
    let val = parseFloat(exactInput.value.replace(',', '.'));
    if (isNaN(val)) val = 0.0;
    if (val < 0) val = 0.0;
    if (val > 5) val = 5.0;
    val = Math.round(val * 10) / 10;
    exactInput.value = val.toString().replace('.', ',');
    itemSelections[itemId].value = val;
}

/* ========================================================
   MODAL RÚBRICA COMPLETA
   ======================================================== */
function openFullRubric() { 
    generateFullRubricTable();
    document.getElementById('full-rubric-modal').classList.remove('hidden'); 
}
function closeFullRubric() { document.getElementById('full-rubric-modal').classList.add('hidden'); }

function generateFullRubricTable() {
    const c = document.getElementById('full-rubric-content');
    const activeRubric = getCurrentRubric();
    let h = `<table style="width:100%;border-collapse:collapse;font-size:0.82rem;">
        <thead><tr>
            <th style="padding:10px;border:1px solid #ddd;background:#005A9C;color:white;">Ítem</th>
            <th style="padding:10px;border:1px solid #ddd;background:#dc3545;color:white;">Insuficiente 0.0–2.9</th>
            <th style="padding:10px;border:1px solid #ddd;background:#e6a817;color:white;">Aceptable 3.0–3.5</th>
            <th style="padding:10px;border:1px solid #ddd;background:#17a2b8;color:white;">Bueno 3.6–4.5</th>
            <th style="padding:10px;border:1px solid #ddd;background:#28a745;color:white;">Sobresaliente 4.6–5.0</th>
        </tr></thead><tbody>`;
    activeRubric.forEach(cat => {
        h += `<tr style="background:#f0f4f8;"><td colspan="5" style="padding:8px;font-weight:bold;text-align:center;color:#005A9C;">${cat.category}</td></tr>`;
        cat.items.forEach(item => {
            if (activeRubric === rubricMiniCex) {
                itemSelections[item.id] = { level: 'minicex', value: (5/9)*5, raw: 5 };
            }
            h += `<tr><td style="padding:10px;border:1px solid #ddd;font-weight:500;">${item.title}<br><span style="font-size:0.72rem;color:#666;">${item.desc}</span></td>
                <td style="padding:10px;border:1px solid #ddd;">${item.details.insuficiente}</td>
                <td style="padding:10px;border:1px solid #ddd;">${item.details.aceptable}</td>
                <td style="padding:10px;border:1px solid #ddd;">${item.details.bueno}</td>
                <td style="padding:10px;border:1px solid #ddd;">${item.details.sobresaliente}</td></tr>`;
        });
    });
    h += `</tbody></table>`;
    c.innerHTML = h;
}

/* ========================================================
   BASE DE DATOS FIRESTORE: RESIDENTES Y DOCENTES
   ======================================================== */
async function loadResidents() {
    const sel = document.getElementById('resident-select');
    sel.innerHTML = '<option value="">Seleccione residente...</option>';
    try {
        const snapshot = await db.collection('residentes_hptu').where('año', '==', 1).get();
        if (!snapshot.empty) {
            snapshot.forEach(doc => {
                const data = doc.data();
                sel.add(new Option(data.nombre, doc.id));
            });
            return;
        }
    } catch (e) { console.warn("Error cargando residentes:", e); }

    // Si la base de datos está vacía, sembramos los residentes iniciales automáticamente
    const defaultResidents = [
        { nombre: 'Maria Alejandra Echavarria', año: 1 },
        { nombre: 'Sara Jaramillo', año: 1 },
        { nombre: 'Valeria Naranjo', año: 1 }
    ];
    for (const r of defaultResidents) {
        const ref = await db.collection('residentes_hptu').add(r);
        sel.add(new Option(r.nombre, ref.id));
    }
}

async function loadTeachers(rot) {
    const sel = document.getElementById('teacher-select');
    sel.innerHTML = '';
    if (currentUser) {
        sel.add(new Option(`${currentUser.nombre} (Docente Autenticado)`, currentUser.uid));
    } else {
        sel.add(new Option('Docente no autenticado', 'anon'));
    }
}

/* ========================================================
   CÁLCULO Y GUARDADO EN FIRESTORE
   ======================================================== */
async function calculateResults() {
    const activeRubric = getCurrentRubric();
    const allItems = activeRubric.flatMap(cat => cat.items);
    const unselected = allItems.filter(item => !itemSelections[item.id]);
    if (unselected.length > 0) {
        alert(`Faltan ítems por calificar:\n${unselected.map(i => '• ' + i.title).join('\n')}`);
        return;
    }

    const applicable = allItems.filter(item => itemSelections[item.id] && itemSelections[item.id].level !== 'na' && itemSelections[item.id].value !== null);
    let totalWeight = applicable.reduce((s, i) => s + i.weight, 0);
    let finalScore = 0;
    if (totalWeight > 0) applicable.forEach(i => { finalScore += itemSelections[i.id].value * (i.weight / totalWeight); });
    finalScore = finalScore.toFixed(2);

    const eticosNode = document.querySelector('input[name="eticos"]:checked');
    const eticosVal = eticosNode ? eticosNode.value : 'NO';
    const fortalezas = document.getElementById('fortalezas').value;
    const mejoras = document.getElementById('mejoras').value;
    const residentName = document.getElementById('form-resident-name').innerText;
    const teacherName = currentUser ? currentUser.nombre : 'Docente';

    let qualitative = finalScore >= 4.6 ? "Sobresaliente" : finalScore >= 3.6 ? "Bueno" : finalScore >= 3.0 ? "Aceptable" : "Insuficiente";

    document.getElementById('final-score-value').innerText = finalScore;
    document.getElementById('result-resident-info').innerHTML = `
        <p><strong>Residente:</strong> ${residentName}</p>
        <p><strong>Docente:</strong> ${teacherName}</p>
        <p><strong>Rotación:</strong> ${selectedSubjectName}</p>
        <p><strong>Ítems evaluados:</strong> ${applicable.length} de ${allItems.length}</p>`;

    let feedback = `<p>Desempeño clasificado como <strong>${qualitative.toUpperCase()}</strong> con nota de <strong>${finalScore} / 5.0</strong>.</p>`;
    if (applicable.length < allItems.length) feedback += `<p style="color:#757575;">ℹ️ ${allItems.length - applicable.length} ítem(s) "No aplica" excluidos del cálculo.</p>`;
    if (eticosVal === 'NO') feedback += `<p style="color:var(--danger);font-weight:bold;">⚠️ Incumplimiento ético reportado. Requiere análisis del comité.</p>`;
    if (fortalezas) feedback += `<p><strong>Fortalezas:</strong> ${fortalezas}</p>`;
    if (mejoras) feedback += `<p><strong>Por mejorar:</strong> ${mejoras}</p>`;
    document.getElementById('generated-feedback').innerHTML = feedback;

    const scoreUI = document.getElementById('final-score-value');
    scoreUI.style.color = finalScore < 3.0 ? 'var(--danger)' : finalScore < 3.6 ? 'var(--warning)' : finalScore < 4.6 ? 'var(--info)' : 'var(--success)';

    // Guardar en Firestore
    try {
        showLoading('Guardando evaluación en Firebase...');
        const evalType = document.getElementById('evaluation-type').value;
        const actName = document.getElementById('seminar-name').value;

        const evalRef = await db.collection('evaluaciones_hptu').add({
            residente_id: selectedResidentId,
            residente_nombre: residentName,
            docente_id: currentUser ? currentUser.uid : 'anon',
            docente_nombre: teacherName,
            rotacion: selectedSubjectName,
            tipo_evaluacion: evalType,
            nombre_actividad: actName || null,
            nota_final: parseFloat(finalScore),
            aspectos_eticos: (eticosVal === 'SI'),
            fortalezas,
            por_mejorar: mejoras,
            created_at: firebase.firestore.FieldValue.serverTimestamp()
        });

        // Guardar ítems individuales
        const batch = db.batch();
        activeRubric.forEach(cat => {
            cat.items.forEach(item => {
                const sel = itemSelections[item.id];
                if (sel && sel.level !== 'na' && sel.value !== null) {
                    const itemRef = db.collection('evaluacion_items').doc();
                    batch.set(itemRef, {
                        evaluacion_id: evalRef.id,
                        item_id: item.id,
                        item_titulo: item.title,
                        categoria: cat.category,
                        peso: item.weight,
                        nota: sel.value,
                        nivel: sel.level
                    });
                }
            });
        });
        await batch.commit();
        hideLoading();
    } catch (e) {
        console.error("Error guardando en Firestore:", e);
        hideLoading();
    }

    showStep('step-results');
}

function resetApp() {
    Object.keys(itemSelections).forEach(k => delete itemSelections[k]);
    document.getElementById('evaluation-form').reset();
    showStep('step-residents-grid');
}

/* ========================================================
   COORDINADOR — FIRESTORE REPORTE
   ======================================================== */
async function loadReportSelects() {
    const resSel = document.getElementById('report-resident');
    resSel.innerHTML = '<option value="">Seleccione residente...</option>';
    try {
        const snapshot = await db.collection('residentes_hptu').get();
        snapshot.forEach(doc => resSel.add(new Option(doc.data().nombre, doc.id)));
    } catch (e) { console.warn(e); }

    const rotSel = document.getElementById('report-rotation');
    rotSel.innerHTML = '<option value="">Seleccione rotación...</option>';
    rotSel.add(new Option("Hospitalización pediátrica III nivel fundamentación", "Hospitalización pediátrica III nivel fundamentación"));
    rotSel.add(new Option("Hospitalización pediátrica III nivel profundización", "Hospitalización pediátrica III nivel profundización"));

    const today = new Date();
    const monthAgo = new Date(today); monthAgo.setMonth(monthAgo.getMonth() - 2);
    document.getElementById('report-date-to').value = today.toISOString().split('T')[0];
    document.getElementById('report-date-from').value = monthAgo.toISOString().split('T')[0];
    document.getElementById('report-preview').classList.add('hidden');
}

async function searchEvaluations() {
    const residentId = document.getElementById('report-resident').value;
    const rotation = document.getElementById('report-rotation').value;
    const dateFrom = document.getElementById('report-date-from').value;
    const dateTo = document.getElementById('report-date-to').value;

    if (!residentId || !rotation || !dateFrom || !dateTo) {
        alert('Por favor complete todos los campos.');
        return;
    }

    showLoading('Buscando evaluaciones en Firebase...');
    try {
        const snapshot = await db.collection('evaluaciones_hptu')
            .where('residente_id', '==', residentId)
            .where('rotacion', '==', rotation)
            .get();

        hideLoading();

        let evals = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
        const fromDate = new Date(dateFrom + 'T00:00:00');
        const toDate = new Date(dateTo + 'T23:59:59');

        evals = evals.filter(e => {
            if (!e.created_at) return true;
            const d = e.created_at.toDate ? e.created_at.toDate() : new Date(e.created_at);
            return d >= fromDate && d <= toDate;
        });

        if (evals.length === 0) {
            alert('No se encontraron evaluaciones para este residente en esa rotación y período.');
            return;
        }

        reportEvaluations = evals;

        const previewDiv = document.getElementById('report-preview');
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

    } catch (e) {
        hideLoading();
        alert('Error: ' + e.message);
    }
}

/* ========================================================
   INFORME FINAL — GENERAR WORD CON IA
   ======================================================== */
async function callGeminiForReport(apiKey, resName, rotation, avgFinal, evalLists, microcurriculo) {
    const fetchGemini = async (modelName) => {
        return fetch(`https://generativelanguage.googleapis.com/v1beta/models/${modelName}:generateContent?key=${apiKey}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                contents: [{ parts: [{ text: prompt }] }],
                generationConfig: { temperature: 0.3 }
            })
        });
    };
    
    let resumen = '';
    ['ronda', 'seminario', 'minicex'].forEach(tipo => {
        if (evalLists[tipo] && evalLists[tipo].length > 0) {
            resumen += `\n--- ${tipo.toUpperCase()} ---\n`;
            evalLists[tipo].forEach(e => {
                resumen += `Nota: ${e.nota_final}\nFortalezas: ${e.fortalezas || 'N/A'}\nPor Mejorar: ${e.por_mejorar || 'N/A'}\n`;
            });
        }
    });

    const prompt = `Actúa como el Coordinador del Programa de Especialización en Pediatría. Redacta la SÍNTESIS CUALITATIVA DEL DESEMPEÑO para el informe final de rotación del residente.
Residente: ${resName}
Rotación: ${rotation}
Nota Promedio Final: ${avgFinal} / 5.0
Microcurrículo de la rotación (Competencias esperadas): ${microcurriculo || 'No especificado.'}
Resumen de evaluaciones y comentarios de los docentes: ${resumen}

Instrucciones estrictas:
1. Redacta en tercera persona de forma muy formal y profesional.
2. NO menciones los nombres de los docentes evaluadores.
3. El informe debe constar de 2 a 3 párrafos bien estructurados.
4. Conecta el desempeño real del residente (notas y comentarios) explícitamente con las competencias esperadas en el Microcurrículo.
5. Si el promedio es menor a 3.6, enfatiza en un tono constructivo pero firme las áreas críticas a mejorar.
6. NO incluyas saludos ni despedidas, ve directo al texto del informe.`;

    let availableModel = 'gemini-3.8-flash';
    let debugModels = "";
    try {
        const listRes = await fetch(`https://generativelanguage.googleapis.com/v1beta/models?key=${apiKey}`);
        if (listRes.ok) {
            const listData = await listRes.json();
            const models = listData.models || [];
            debugModels = " Modelos en tu llave: " + models.map(m => m.name.split('/')[1]).join(', ');
            
            // Crear una cola de modelos de mayor a menor prioridad
            const targetModels = [
                'gemini-3.8-flash',
                'gemini-3.5-flash-lite',
                'gemini-flash-lite-latest',
                'gemini-3.1-flash-lite',
                'gemini-flash-latest'
            ];
            
            const validNames = models.map(m => m.name.split('/')[1]);
            const intersect = targetModels.filter(m => validNames.includes(m));
            if (intersect.length > 0) {
                availableModel = intersect; // Guardar como arreglo
            } else {
                availableModel = [validNames.find(m => m.includes('gemini')) || 'gemini-3.8-flash'];
            }
        }
    } catch(e) { 
        console.warn("No se pudo listar modelos", e); 
        availableModel = ['gemini-3.8-flash', 'gemini-flash-lite-latest']; 
    }

    // Convertir a array si era string por seguridad
    if (!Array.isArray(availableModel)) availableModel = [availableModel];

    let response = null;
    let data = null;

    // Intentar en cascada si hay alta demanda
    for (const model of availableModel) {
        response = await fetchGemini(model);
        data = await response.json();
        
        if (response.ok) {
            break; // ¡Funcionó!
        } else {
            const msg = data.error ? data.error.message.toLowerCase() : '';
            if (msg.includes('high demand') || response.status === 503 || response.status === 429) {
                console.warn(`Modelo ${model} congestionado, intentando el siguiente...`);
                continue; // Probar el siguiente en la lista
            } else if (response.status === 404 || msg.includes('no longer available')) {
                continue; // Modelo obsoleto, probar siguiente
            } else {
                break; // Error fatal (ej. API Key inválida)
            }
        }
    }

    if (!response || !response.ok) {
        let msg = data.error ? data.error.message : 'Error desconocido de la API';
        if (msg.includes('API key not valid')) msg = 'La Clave API de Gemini es incorrecta o le faltan letras.';
        throw new Error(msg + debugModels);
    }

    if (data.candidates && data.candidates.length > 0) {
        return data.candidates[0].content.parts[0].text;
    }
    return 'No se pudo generar el texto.';
}

async function generateFinalReport() {
    if (reportEvaluations.length === 0) { alert('No hay evaluaciones para generar el informe.'); return; }

    const resName = document.getElementById('report-resident').options[document.getElementById('report-resident').selectedIndex].text;
    const rotation = document.getElementById('report-rotation').value;
    const dateFrom = document.getElementById('report-date-from').value;
    const dateTo = document.getElementById('report-date-to').value;
    const apiKey = document.getElementById('gemini-api-key').value.trim();

    showLoading('Generando documento Word y contactando IA...');

    try {
        let sumaRonda = 0, countRonda = 0;
        let sumaSeminario = 0, countSeminario = 0;
        let sumaMinicex = 0, countMinicex = 0;

        const evalLists = { ronda: [], seminario: [], minicex: [] };
        
        reportEvaluations.forEach(e => {
            const val = parseFloat(e.nota_final);
            if(isNaN(val)) return;
            
            const tipo = e.tipo_evaluacion || 'ronda';
            if (tipo === 'ronda') { sumaRonda += val; countRonda++; evalLists.ronda.push(e); }
            else if (tipo === 'seminario') { sumaSeminario += val; countSeminario++; evalLists.seminario.push(e); }
            else if (tipo === 'minicex') { sumaMinicex += val; countMinicex++; evalLists.minicex.push(e); }
        });
        
        const promRonda = countRonda > 0 ? sumaRonda / countRonda : 0;
        const promSeminario = countSeminario > 0 ? sumaSeminario / countSeminario : 0;
        const promMinicex = countMinicex > 0 ? sumaMinicex / countMinicex : 0;
        
        let final = 0;
        let totalWeights = 0;
        if (countRonda > 0) { final += promRonda * 0.5; totalWeights += 0.5; }
        if (countSeminario > 0) { final += promSeminario * 0.3; totalWeights += 0.3; }
        if (countMinicex > 0) { final += promMinicex * 0.2; totalWeights += 0.2; }
        
        let notaFinalPonderada = totalWeights > 0 ? (final / totalWeights).toFixed(2) : 'N/A';

        // 1. Llamar a la IA
        let aiText = "El informe generado por IA no está disponible porque no se configuró la clave de Gemini.";
        if (apiKey) {
            try {
                // Obtener el microcurriculo (contexto)
                let micro = "Hospitalización Pediátrica III Nivel";

                aiText = await callGeminiForReport(apiKey, resName, rotation, notaFinalPonderada, evalLists, micro);
            } catch (iaErr) {
                console.error(iaErr);
                aiText = "Hubo un error al generar el informe con IA: " + iaErr.message;
            }
        } else if (document.getElementById('report-generated-text')) {
            // Fallback si ya había texto
            aiText = document.getElementById('report-generated-text').innerText || aiText;
        }

        // 2. Intentar cargar el logo
        const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, HeadingLevel, WidthType, BorderStyle, ImageRun, AlignmentType } = docx;
        
        let logoImage = null;
        try {
            const logoRes = await fetch('logo-hptu.png');
            if (logoRes.ok) {
                const logoBlob = await logoRes.blob();
                logoImage = await logoBlob.arrayBuffer();
            }
        } catch(e) { console.warn("No se pudo cargar el logo:", e); }

        // 3. Construir el documento
        let paragraphs = [];
        
        if (logoImage) {
            paragraphs.push(new Paragraph({
                children: [new ImageRun({ data: logoImage, transformation: { width: 200, height: 80 } })],
                alignment: AlignmentType.CENTER,
                spacing: { after: 200 }
            }));
        } else {
            paragraphs.push(new Paragraph({ children: [new TextRun({ text: 'HOSPITAL PABLO TOBÓN URIBE', bold: true, size: 28, color: "005A9C" })], alignment: 'center' }));
        }

        paragraphs.push(new Paragraph({ children: [new TextRun({ text: 'INFORME FINAL DE ROTACIÓN', bold: true, size: 24 })], alignment: 'center', spacing: { after: 400 } }));

        paragraphs.push(new Paragraph({ children: [new TextRun({ text: 'Nombre del Residente: ', bold: true, size: 22 }), new TextRun({ text: resName, size: 22 })], spacing: { after: 120 } }));
        paragraphs.push(new Paragraph({ children: [new TextRun({ text: 'Rotación Evaluada: ', bold: true, size: 22 }), new TextRun({ text: rotation, size: 22 })], spacing: { after: 120 } }));
        paragraphs.push(new Paragraph({ children: [new TextRun({ text: 'Período: ', bold: true, size: 22 }), new TextRun({ text: `${dateFrom} a ${dateTo}`, size: 22 })], spacing: { after: 400 } }));

        // Función auxiliar para crear tablas por actividad
        const createTableForType = (title, evals) => {
            paragraphs.push(new Paragraph({ text: title, heading: HeadingLevel.HEADING_3, spacing: { before: 300, after: 150 } }));
            if (evals.length === 0) {
                paragraphs.push(new Paragraph({ text: "No hay evaluaciones registradas para esta actividad.", italics: true }));
                return;
            }

            const rows = [];
            rows.push(new TableRow({
                children: [
                    new TableCell({ children: [new Paragraph({ text: "Fecha", bold: true, alignment: AlignmentType.CENTER })], shading: { fill: "D9EAD3" } }),
                    new TableCell({ children: [new Paragraph({ text: "Docente", bold: true, alignment: AlignmentType.CENTER })], shading: { fill: "D9EAD3" } }),
                    new TableCell({ children: [new Paragraph({ text: "Nota", bold: true, alignment: AlignmentType.CENTER })], shading: { fill: "D9EAD3" } })
                ],
                tableHeader: true
            }));

            evals.forEach(ev => {
                const fecha = ev.created_at && ev.created_at.toDate ? ev.created_at.toDate().toLocaleDateString('es-CO') : '-';
                rows.push(new TableRow({
                    children: [
                        new TableCell({ children: [new Paragraph({ text: fecha })] }),
                        new TableCell({ children: [new Paragraph({ text: ev.docente_nombre || 'Docente' })] }),
                        new TableCell({ children: [new Paragraph({ text: String(ev.nota_final || '-') })] })
                    ]
                }));
            });

            paragraphs.push(new Table({
                rows: rows,
                width: { size: 100, type: WidthType.PERCENTAGE },
            }));

            // Comentarios de esta actividad
            paragraphs.push(new Paragraph({ text: "Comentarios (Fortalezas y Aspectos por mejorar):", bold: true, spacing: { before: 150, after: 100 } }));
            evals.forEach(ev => {
                if (ev.fortalezas || ev.por_mejorar) {
                    let txt = `[${ev.created_at && ev.created_at.toDate ? ev.created_at.toDate().toLocaleDateString('es-CO') : '-'}] `;
                    if (ev.fortalezas) txt += `FORTALEZAS: ${ev.fortalezas}. `;
                    if (ev.por_mejorar) txt += `POR MEJORAR: ${ev.por_mejorar}.`;
                    paragraphs.push(new Paragraph({ text: txt, spacing: { after: 100 }, bullet: { level: 0 } }));
                }
            });
        };

        // Tablas desglosadas
        paragraphs.push(new Paragraph({ text: '1. Desglose de Evaluaciones Individuales', heading: HeadingLevel.HEADING_2, spacing: { before: 200, after: 150 } }));
        
        createTableForType("Ronda Médica (Ponderación 50%)", evalLists.ronda);
        createTableForType("Seminarios (Ponderación 30%)", evalLists.seminario);
        createTableForType("Mini-CEX (Ponderación 20%)", evalLists.minicex);

        // Nota final
        paragraphs.push(new Paragraph({ 
            children: [new TextRun({ text: `Nota Definitiva Ponderada: ${notaFinalPonderada}`, bold: true, size: 28, color: "0B5345" })], 
            alignment: AlignmentType.CENTER,
            spacing: { before: 400, after: 400 } 
        }));

        // Informe IA
        paragraphs.push(new Paragraph({ text: '2. Informe Consolidado Cualitativo (Generado por IA)', heading: HeadingLevel.HEADING_2, spacing: { before: 200, after: 200 } }));

        const blocks = aiText.split('\n').filter(b => b.trim().length > 0);
        blocks.forEach(m => paragraphs.push(new Paragraph({ text: m.replace(/\*\*/g, ''), size: 22, spacing: { after: 120 }, alignment: AlignmentType.JUSTIFIED })));

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
}


function showLoading(text) {
    document.getElementById('loading-text').innerText = text || 'Procesando...';
    document.getElementById('loading-overlay').classList.remove('hidden');
}
function hideLoading() { document.getElementById('loading-overlay').classList.add('hidden'); }



let selectedResidentId = null;

async function loadResidentsGrid() {
    const grid = document.getElementById('residents-grid');
    grid.innerHTML = '<p>Cargando residentes...</p>';
    try {
        const snapshot = await db.collection('residentes_hptu').where('activo', '==', true).get();
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
                <h4 style="margin: 0; color: #333; font-size: 0.95rem;">${data.nombre}</h4><p style="margin: 5px 0 0; font-size: 0.8rem; color: #666;">Año ${data.year}</p>
            `;
            card.onmouseover = () => card.style.transform = 'translateY(-3px)';
            card.onmouseout = () => card.style.transform = 'translateY(0)';
            card.onclick = () => selectResidentForEval(doc.id, data.nombre, photo, data.year);
            grid.appendChild(card);
        });
    } catch (e) {
        console.error(e);
        grid.innerHTML = '<p>Error cargando residentes.</p>';
    }
}



let selectedResidentYear = 1;

async function selectResidentForEval(resId, resName, resPhoto, resYear) {
    selectedResidentId = resId;
    selectedResidentYear = resYear || 1;
    
    const photoEl = document.getElementById('form-resident-photo');
    if (resPhoto) {
        photoEl.src = resPhoto;
        photoEl.style.display = 'block';
    } else {
        photoEl.style.display = 'none';
    }
    document.getElementById('form-resident-name').innerText = resName;
    
    // Set explicit subject based on year
    if (selectedResidentYear === 3) {
        selectedSubjectName = "Hospitalización pediátrica III nivel profundización";
    } else {
        selectedSubjectName = "Hospitalización pediátrica III nivel fundamentación";
    }
    
    // Setup dropdown options (Todos con 50/30/20)
    const evalTypeSelect = document.getElementById('evaluation-type');
    evalTypeSelect.value = 'ronda';
    
    const optTema = document.getElementById('opt-tema-central');
    const optMinicex = document.getElementById('opt-minicex');
    const optRevistas = document.getElementById('opt-club-revistas');
    const optEdu = document.getElementById('opt-actividad-educativa');
    const optRonda = evalTypeSelect.querySelector('option[value="ronda"]');
    const optSeminario = evalTypeSelect.querySelector('option[value="seminario"]');
    
    optMinicex.classList.remove('hidden');
    if(optTema) optTema.classList.add('hidden');
    if(optRevistas) optRevistas.classList.add('hidden');
    if(optEdu) optEdu.classList.add('hidden');
    
    if(optRonda) optRonda.innerText = 'Ronda Médica (50%)';
    if(optSeminario) optSeminario.innerText = 'Seminario (30%)';
    
    Object.keys(itemSelections).forEach(k => delete itemSelections[k]);
    document.querySelectorAll('.score-btn').forEach(b => b.classList.remove('selected'));
    document.querySelectorAll('.score-input-row').forEach(r => { r.classList.add('hidden'); r.style.display = 'none'; });
    
    handleEvaluationTypeChange();
    
    document.getElementById('fortalezas').value = '';
    document.getElementById('mejoras').value = '';
    
    showStep('step-form');
    await loadTeachers(selectedSubjectName);
}



function openAdminResidents() {
    showStep('step-admin-residents');
    loadAdminResidentsList();
}

async function loadAdminResidentsList() {
    const list = document.getElementById('admin-residents-list');
    list.innerHTML = '<p>Cargando...</p>';
    try {
        const snapshot = await db.collection('residentes_hptu').orderBy('nombre').get();
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
        list.innerHTML = `<p style="color:red">Error cargando lista: ${e.message}</p>`;
        alert("Error Firestore: " + e.message);
    }
}

async function handleAddResident() {
    const nameInput = document.getElementById('new-res-name').value.trim();
    const photoInput = document.getElementById('new-res-photo');
    const yearInput = parseInt(document.getElementById('new-res-year').value);
    const btn = document.getElementById('btn-add-res');
    
    if (!nameInput) return;
    
    btn.disabled = true;
    btn.innerText = 'Guardando...';
    
    try {
        let photoUrl = null;
        if (photoInput.files.length > 0) {
            const file = photoInput.files[0];
            const ref = storage.ref().child(`residents-photos/${Date.now()}_${file.name}`);
            
            // Add a timeout to catch hanging storage uploads (e.g. uninitialized bucket)
            const uploadTask = ref.put(file);
            const timeoutPromise = new Promise((_, reject) => setTimeout(() => reject(new Error("Timeout: Storage no responde. ¿Activaste Firebase Storage en la consola?")), 10000));
            
            await Promise.race([uploadTask, timeoutPromise]);
            photoUrl = await ref.getDownloadURL();
        }
        
        await db.collection('residentes_hptu').add({
            nombre: nameInput,
            year: yearInput,
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
        await db.collection('residentes_hptu').doc(id).update({ activo: !currentStatus });
        loadAdminResidentsList();
    } catch (e) {
        console.error(e);
        alert('Error cambiando estado.');
    }
}
