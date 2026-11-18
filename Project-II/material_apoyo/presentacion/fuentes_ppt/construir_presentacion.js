const fs = require("fs");
const path = require("path");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const pptxgen = require("pptxgenjs");
const Fa = require("react-icons/fa6");

const HERE = __dirname;
const PRESENTATION_DIR = path.resolve(HERE, "..");
const FIGURES = path.resolve(HERE, "..", "..", "informe", "figuras");
const IMG = path.join(HERE, "img");
const OUT_PPTX = path.resolve(HERE, "..", "..", "..", "entregable", "Presentacion_Proyecto2_Grupo7.pptx");
const OUT_MD = path.join(PRESENTATION_DIR, "guion_exposicion.md");
const APPLY_THEME = process.env.PPTX_APPLY_THEME;

const THEME = {
  name: "Retratos Grupo 7",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1B1F24",
    lt1: "FFFFFF",
    dk2: "2E3A46",
    lt2: "EEF1F4",
    accent1: "C2703D",
    accent2: "2F6F6A",
    accent3: "7A8B98",
    accent4: "E0B05A",
    accent5: "B4473C",
    accent6: "3E7C4F",
    hlink: "2F6F6A",
    folHlink: "6B4E71",
  },
};

const REPO_URL = "https://github.com/KarTaGo124/Planning-Decision-Making-AI";
const SPEAKERS = { J: "José", M: "Matías", A: "Alejandro" };

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Retratos profesionales con IA, decididos por el usuario";
pres.author = "Grupo 7 - CS5363 UTEC";
pres.subject = "Proyecto 2 - Sistema generativo interactivo con feedback humano";
const C = pres.SchemeColor;

const W = 13.333;
const MARGIN = 0.6;
const CONTENT_W = W - 2 * MARGIN;

const FOOTER_TEXT = "Grupo 7 · CS5363 Planificación y Toma de Decisiones en IA · UTEC 2026-2";

pres.defineSlideMaster({
  title: "PORTADA",
  background: { color: C.text1 },
  objects: [
    {
      placeholder: {
        options: { name: "title", type: "title", x: MARGIN, y: 1.85, w: 7.1, h: 2.0, fontSize: 40, bold: true, color: C.background1, valign: "top", align: "left", margin: 0 },
        text: "",
      },
    },
    {
      placeholder: {
        options: { name: "body", type: "body", x: MARGIN, y: 3.95, w: 6.6, h: 1.1, fontSize: 18, color: C.background2, valign: "top", margin: 0 },
        text: "",
      },
    },
  ],
});

pres.defineSlideMaster({
  title: "CONTENIDO",
  background: { color: C.background1 },
  margin: [0.5, 0.6, 0.6, 0.6],
  objects: [
    {
      placeholder: {
        options: { name: "title", type: "title", x: MARGIN, y: 0.35, w: CONTENT_W, h: 0.85, fontSize: 30, bold: true, color: C.text1, valign: "middle", align: "left", margin: 0 },
        text: "",
      },
    },
    { text: { text: FOOTER_TEXT, options: { x: MARGIN, y: 7.02, w: 9, h: 0.3, fontSize: 10, color: C.accent3, margin: 0 } } },
  ],
  slideNumber: { x: 12.25, y: 7.02, w: 0.5, h: 0.3, fontSize: 10, color: C.accent3, align: "right" },
});

pres.defineSlideMaster({
  title: "OSCURO",
  background: { color: C.text1 },
  objects: [
    {
      placeholder: {
        options: { name: "title", type: "title", x: MARGIN, y: 0.55, w: CONTENT_W, h: 1.0, fontSize: 40, bold: true, color: C.background1, valign: "middle", align: "left", margin: 0 },
        text: "",
      },
    },
    { text: { text: FOOTER_TEXT, options: { x: MARGIN, y: 7.02, w: 9, h: 0.3, fontSize: 10, color: C.accent3, margin: 0 } } },
  ],
  slideNumber: { x: 12.25, y: 7.02, w: 0.5, h: 0.3, fontSize: 10, color: C.accent3, align: "right" },
});

const iconCache = new Map();

async function icon(name, hex = "#FFFFFF") {
  const key = `${name}-${hex}`;
  if (iconCache.has(key)) return iconCache.get(key);
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Fa[name], { color: hex, size: 256 }));
  const png = await sharp(Buffer.from(svg)).png().toBuffer();
  const data = "image/png;base64," + png.toString("base64");
  iconCache.set(key, data);
  return data;
}

async function iconCircle(slide, x, y, d, name, fill = C.accent1, objectName = "icono") {
  slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill, width: 0 }, objectName: `${objectName}-circulo` });
  const pad = d * 0.25;
  slide.addImage({ data: await icon(name), x: x + pad, y: y + pad, w: d - 2 * pad, h: d - 2 * pad, objectName: `${objectName}-glifo` });
}

function numberCircle(slide, x, y, d, label, fill = C.accent1) {
  slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill, width: 0 }, objectName: `numero-${label}` });
  slide.addText(String(label), { x, y, w: d, h: d, fontSize: Math.round(d * 26), bold: true, color: C.background1, align: "center", valign: "middle", margin: 0, isTextBox: true, fontFace: THEME.headFontFace });
}

function card(slide, x, y, w, h, fill = C.background2, objectName = "tarjeta") {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.12, fill: { color: fill }, line: { color: fill, width: 0 }, objectName });
}

function frame(slide, x, y, w, h, objectName = "marco") {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: x - 0.06, y: y - 0.06, w: w + 0.12, h: h + 0.12, rectRadius: 0.08,
    fill: { color: C.background1 }, line: { color: "D3DAE0", width: 0.75 },
    shadow: { type: "outer", color: "000000", opacity: 0.12, blur: 6, offset: 2, angle: 90 }, objectName,
  });
}

function text(slide, value, opts) {
  slide.addText(value, Object.assign({ isTextBox: true, margin: 0, color: C.text1, fontSize: 15, valign: "top" }, opts));
}

async function iconRow(slide, x, y, w, iconName, title, body, opts = {}) {
  const d = opts.d || 0.6;
  await iconCircle(slide, x, y, d, iconName, opts.fill || C.accent1, opts.name || title);
  const runs = [{ text: title, options: { bold: true, fontSize: opts.titleSize || 16, color: opts.titleColor || C.text1, breakLine: Boolean(body) } }];
  if (body) runs.push({ text: body, options: { fontSize: opts.bodySize || 14, color: opts.bodyColor || C.text2 } });
  text(slide, runs, { x: x + d + 0.25, y: y - 0.02, w: w - d - 0.25, h: opts.h || 1.0, paraSpaceAfter: 2 });
}

const img = (name) => path.join(IMG, name);
const fig = (name) => path.join(FIGURES, name);

const SLIDES = [];

function register(slide, meta) {
  slide.addNotes(`[${SPEAKERS[meta.speaker]}] ${meta.notes}`);
  SLIDES.push(meta);
}

async function slidePortada() {
  pres.addSection({ title: "Introducción" });
  const s = pres.addSlide({ masterName: "PORTADA", sectionTitle: "Introducción" });
  text(s, "PROYECTO 2 · CS5363 PLANIFICACIÓN Y TOMA DE DECISIONES EN IA", { x: MARGIN, y: 1.3, w: 7.2, h: 0.35, fontSize: 12, bold: true, color: C.accent4, charSpacing: 1 });
  s.addText("Retratos profesionales con IA, decididos por el usuario", { placeholder: "title" });
  s.addText("Sistema generativo interactivo con Stable Diffusion, ControlNet, feedback humano y un agente explicador LLM", { placeholder: "body" });
  text(s, [
    { text: "Grupo 7: ", options: { bold: true, color: C.background1, breakLine: false } },
    { text: "José Guillermo Gálvez Pacori · Matías Alonso Meneses Roncal · Alejandro Joel Ore García", options: { color: C.background2, breakLine: true } },
    { text: "Docentes: ", options: { bold: true, color: C.background1, breakLine: false } },
    { text: "Dra. Aurea Soriano-Vargas · Mg. Robert Junior Buleje Del Carpio", options: { color: C.background2, breakLine: true } },
    { text: "Universidad de Ingeniería y Tecnología (UTEC) · 2026-2", options: { color: C.accent3 } },
  ], { x: MARGIN, y: 5.35, w: 7.4, h: 1.3, fontSize: 13, paraSpaceAfter: 4 });

  const portraits = [
    { file: "intermedio_0.png", x: 7.95, y: 2.05, d: 2.9, label: "Foto de entrada" },
    { file: "intermedio_2.png", x: 10.85, y: 1.0, d: 1.95, label: "Intermedio · Business Casual" },
    { file: "basico_2.png", x: 10.85, y: 3.85, d: 1.95, label: "Básico · Business Casual" },
  ];
  for (const p of portraits) {
    s.addShape(pres.shapes.OVAL, { x: p.x - 0.07, y: p.y - 0.07, w: p.d + 0.14, h: p.d + 0.14, fill: { color: C.text1 }, line: { color: C.accent1, width: 2.5 }, objectName: `anillo-${p.file}` });
    s.addImage({ path: img(p.file), x: p.x, y: p.y, w: p.d, h: p.d, rounding: true, altText: p.label, objectName: `retrato-${p.file}` });
    text(s, p.label, { x: p.x - 0.4, y: p.y + p.d + 0.12, w: p.d + 0.8, h: 0.3, fontSize: 11, color: C.background2, align: "center" });
  }
  register(s, {
    title: "Retratos profesionales con IA, decididos por el usuario",
    speaker: "J",
    time: 45,
    notes: "Buenos días. Somos el Grupo 7: Matías Meneses, Alejandro Ore y yo, José Gálvez. Les presentamos un sistema que genera retratos profesionales a partir de una foto cotidiana. La idea central es que la inteligencia artificial propone y la persona decide: el sistema genera cinco variaciones, el usuario acepta o rechaza cada una, y un agente basado en un modelo de lenguaje explica esas decisiones. En la imagen ven una foto de entrada y dos variaciones generadas en una GPU de Google Colab.",
  });
}

async function slideProblema() {
  const s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Introducción" });
  s.addText("Un retrato profesional sigue siendo caro o poco fiable", { placeholder: "title" });
  card(s, MARGIN, 1.55, 4.2, 4.6, C.text2, "tarjeta-costo");
  await iconCircle(s, MARGIN + 0.4, 1.95, 0.75, "FaCameraRetro", C.accent1, "icono-costo");
  text(s, "50–150 USD", { x: MARGIN + 0.4, y: 2.95, w: 3.5, h: 0.9, fontSize: 44, bold: true, color: C.background1, fontFace: THEME.headFontFace });
  text(s, "costo típico de una sesión de fotos en estudio", { x: MARGIN + 0.4, y: 3.9, w: 3.4, h: 0.8, fontSize: 16, color: C.background2 });
  text(s, "A eso se suman traslados, citas y postproducción: un gasto difícil para un estudiante.", { x: MARGIN + 0.4, y: 4.8, w: 3.4, h: 1.1, fontSize: 14, color: C.accent4 });

  const rows = [
    ["FaIdCard", "Pérdida de identidad", "Los generadores de imágenes no controlados no preservan los rasgos reales de la persona."],
    ["FaLayerGroup", "Sin contexto", "No distinguen lo que pide LinkedIn formal, un WhatsApp corporativo o un perfil de GitHub."],
    ["FaEye", "Sin transparencia", "La persona no sabe por qué el sistema propone cada opción ni cómo cuentan sus decisiones."],
  ];
  let y = 1.65;
  for (const [iconName, title, body] of rows) {
    await iconRow(s, 5.35, y, 7.38, iconName, title, body, { d: 0.7, titleSize: 18, bodySize: 15, h: 1.2 });
    y += 1.5;
  }
  card(s, 5.35, 6.05, 7.38, 0.7, C.background2, "tarjeta-respuesta");
  text(s, "Nuestra respuesta: 5 variaciones por foto, elegidas por la persona y explicadas por un agente.", { x: 5.55, y: 6.05, w: 7.0, h: 0.7, fontSize: 15, italic: true, color: C.accent2, valign: "middle" });
  register(s, {
    title: "Un retrato profesional sigue siendo caro o poco fiable",
    speaker: "J",
    time: 60,
    notes: "Empecemos por el problema. Una foto profesional de estudio cuesta, en promedio, entre 50 y 150 dólares, sin contar traslados ni postproducción, y para un estudiante es un gasto difícil. La alternativa obvia son los generadores de imágenes, pero tienen tres problemas. Primero, no preservan la identidad: la persona del resultado puede no parecerse a la de la foto. Segundo, no distinguen contexto: no es lo mismo una foto para LinkedIn formal que para un WhatsApp corporativo o para GitHub. Y tercero, no son transparentes: el usuario no sabe por qué el sistema le propone cada opción. Nuestra respuesta es generar cinco variaciones por foto, dejar que la persona elija y explicar sus elecciones.",
  });
}

async function slideDesignThinking() {
  const s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Introducción" });
  s.addText("Design Thinking: del reto a la propuesta de valor", { placeholder: "title" });
  card(s, MARGIN, 1.45, CONTENT_W, 1.3, C.background2, "tarjeta-pregunta");
  text(s, "PREGUNTA GUÍA · TALLER DE LA SEMANA 13", { x: MARGIN + 0.35, y: 1.6, w: 8, h: 0.3, fontSize: 12, bold: true, color: C.accent1, charSpacing: 1 });
  text(s, "¿Cómo podríamos facilitar la generación accesible y controlada de retratos profesionales para estudiantes y jóvenes egresados?", { x: MARGIN + 0.35, y: 1.95, w: CONTENT_W - 0.7, h: 0.7, fontSize: 20, italic: true, color: C.text1, fontFace: THEME.headFontFace });

  card(s, MARGIN, 3.0, 4.55, 3.75, C.text2, "tarjeta-perfil");
  await iconCircle(s, MARGIN + 0.35, 3.3, 0.6, "FaUserGraduate", C.accent1, "icono-perfil");
  text(s, "Perfil de usuario", { x: MARGIN + 1.15, y: 3.38, w: 3.2, h: 0.45, fontSize: 18, bold: true, color: C.background1 });
  const perfil = [
    "Estudiante de ciclos avanzados o egresado reciente",
    "Presupuesto limitado para una sesión de estudio",
    "Teme que la IA le deforme el rostro",
    "Necesita una foto distinta para cada red",
  ];
  text(s, perfil.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < perfil.length - 1 } })), { x: MARGIN + 0.35, y: 4.15, w: 3.95, h: 2.45, fontSize: 15, color: C.background2, paraSpaceAfter: 8 });

  text(s, "Propuesta de valor", { x: 5.45, y: 3.0, w: 7, h: 0.35, fontSize: 15, bold: true, color: C.accent2 });
  const values = [
    ["FaWandMagicSparkles", "Funcional", "Retratos adaptados a cada red con presets y un prompt libre, en segundos."],
    ["FaUserTie", "Social", "Una imagen creíble y profesional ante reclutadores y clientes."],
    ["FaHeart", "Emocional", "Confianza: el sistema busca no distorsionar el rostro y la persona tiene la última palabra."],
  ];
  const cw = (12.73 - 5.45 - 0.5) / 3;
  for (let i = 0; i < values.length; i++) {
    const x = 5.45 + i * (cw + 0.25);
    card(s, x, 3.45, cw, 3.3, C.background2, `tarjeta-valor-${i}`);
    await iconCircle(s, x + 0.3, 3.7, 0.6, values[i][0], C.accent2, `icono-valor-${i}`);
    text(s, values[i][1], { x: x + 0.3, y: 4.45, w: cw - 0.6, h: 0.4, fontSize: 18, bold: true });
    text(s, values[i][2], { x: x + 0.3, y: 4.95, w: cw - 0.6, h: 1.7, fontSize: 14, color: C.text2 });
  }
  register(s, {
    title: "Design Thinking: del reto a la propuesta de valor",
    speaker: "J",
    time: 60,
    notes: "Para llegar a la propuesta seguimos el taller de Design Thinking de la semana 13. Formulamos la pregunta guía que ven arriba: cómo facilitar la generación accesible y controlada de retratos profesionales para estudiantes y jóvenes egresados. El perfil de usuario es un estudiante de ciclos avanzados o un egresado reciente, con poco presupuesto, que teme que la IA le deforme la cara y que necesita una foto distinta para cada red. La propuesta de valor tiene tres dimensiones: funcional, porque adapta el retrato a cada red con presets y un prompt libre; social, porque proyecta una imagen creíble ante reclutadores y clientes; y emocional, porque la persona siempre tiene la última palabra.",
  });
}

async function slideJourney() {
  const s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Introducción" });
  s.addText("Journey map: el usuario decide en cada paso", { placeholder: "title" });
  const steps = [
    ["FaCamera", "Selfie", "Sube una foto cotidiana y elige un paquete de 5 estilos."],
    ["FaVectorSquare", "Transparencia", "Ve el recorte de su cara y los bordes Canny que guían al modelo."],
    ["FaImages", "Exploración", "Recibe 5 variaciones, todas en estado Pendiente."],
    ["FaHandPointer", "Decisión", "Acepta o rechaza cada imagen, la califica y comenta."],
    ["FaRobot", "Explicación", "El agente resume qué aceptó, qué rechazó y por qué."],
  ];
  const colW = 2.25;
  const gap = (CONTENT_W - 5 * colW) / 4;
  const d = 0.95;
  const circleY = 1.75;
  s.addShape(pres.shapes.LINE, { x: MARGIN + colW / 2, y: circleY + d / 2, w: CONTENT_W - colW, h: 0, line: { color: "C9D1D8", width: 2 }, objectName: "linea-recorrido" });
  for (let i = 0; i < steps.length; i++) {
    const x = MARGIN + i * (colW + gap);
    await iconCircle(s, x + (colW - d) / 2, circleY, d, steps[i][0], C.accent1, `paso-${i + 1}`);
    text(s, `PASO ${i + 1}`, { x, y: 2.95, w: colW, h: 0.3, fontSize: 12, bold: true, color: C.accent1, align: "center", charSpacing: 1 });
    text(s, steps[i][1], { x, y: 3.3, w: colW, h: 0.45, fontSize: 19, bold: true, align: "center", fontFace: THEME.headFontFace });
    text(s, steps[i][2], { x: x + 0.05, y: 3.85, w: colW - 0.1, h: 1.4, fontSize: 15, color: C.text2, align: "center" });
  }
  card(s, MARGIN, 5.6, CONTENT_W, 0.95, C.background2, "tarjeta-pendiente");
  await iconCircle(s, MARGIN + 0.3, 5.775, 0.6, "FaClock", C.accent2, "icono-pendiente");
  text(s, "El estado Pendiente deja claro que nada se da por aceptado hasta que la persona vota.", { x: MARGIN + 1.15, y: 5.6, w: CONTENT_W - 1.4, h: 0.95, fontSize: 17, italic: true, color: C.text1, valign: "middle" });
  register(s, {
    title: "Journey map: el usuario decide en cada paso",
    speaker: "J",
    time: 55,
    notes: "Este es el recorrido del usuario, en cinco pasos. Sube una selfie y elige un paquete de cinco estilos. Luego ve el recorte de su cara y los bordes que usará el modelo, para que entienda qué se conserva. Recibe cinco variaciones, todas en estado Pendiente. Acepta o rechaza cada una, le pone una calificación y, si quiere, un comentario. Y al final el agente le resume qué aceptó, qué rechazó y por qué. El estado Pendiente es importante: nada se da por aceptado hasta que la persona vota. Ahora Matías les explica cómo está construido.",
  });
}

async function slideArquitectura() {
  pres.addSection({ title: "Sistema" });
  const s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Sistema" });
  s.addText("Arquitectura: de la foto a la explicación", { placeholder: "title" });
  const w = CONTENT_W;
  const h = w * 748 / 1745;
  s.addImage({ path: fig("fig1_arquitectura.png"), x: MARGIN, y: 1.4, w, h, altText: "Diagrama de arquitectura en ocho etapas", objectName: "diagrama-arquitectura" });
  register(s, {
    title: "Arquitectura: de la foto a la explicación",
    speaker: "M",
    time: 75,
    notes: "Gracias, José. La arquitectura tiene ocho etapas. Arriba, la entrada: la foto, el paquete de estilos y un prompt libre opcional. Antes de usar la GPU pasa por un filtro ético que bloquea pedidos inapropiados. Después viene el preprocesamiento: detectamos la cara, la recortamos a 512 por 512 y extraemos sus bordes. La imagen viaja codificada en base64 a un servidor FastAPI en Google Colab, con una GPU Tesla T4, que genera las cinco variaciones. Abajo, las imágenes vuelven a la interfaz en Streamlit, donde la persona decide. Cada decisión se registra en un archivo JSON, y el agente explicador lo lee para producir el resumen y medir su propia fidelidad contra esos datos.",
  });
}

async function slidePreproceso() {
  const s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Sistema" });
  s.addText("Preprocesamiento: detectar, recortar y describir", { placeholder: "title" });
  const h = 2.8;
  const items = [
    ["pre_original.png", h * 202 / 360, "Foto original"],
    ["pre_recorte.png", h, "Recorte 512 × 512"],
    ["pre_canny.png", h, "Bordes Canny (100 / 200)"],
  ];
  let x = MARGIN;
  for (const [file, w, label] of items) {
    frame(s, x, 1.6, w, h, `marco-${file}`);
    s.addImage({ path: img(file), x, y: 1.6, w, h, altText: label, objectName: `imagen-${file}` });
    text(s, label, { x: x - 0.1, y: 1.6 + h + 0.15, w: w + 0.2, h: 0.3, fontSize: 12, color: C.text2, align: "center" });
    x += w + 0.3;
  }
  const rows = [
    ["FaMagnifyingGlass", "Detección facial", "Dos cascadas Haar, con reducción de escala y ecualización."],
    ["FaCropSimple", "Recorte cuadrado", "512 px centrado en la cara, sin deformarla."],
    ["FaVectorSquare", "Bordes Canny", "La estructura que ControlNet conserva al generar."],
  ];
  let y = 1.6;
  for (const [iconName, title, body] of rows) {
    await iconRow(s, 8.85, y, 3.88, iconName, title, body, { d: 0.6, titleSize: 16, bodySize: 14, h: 1.0 });
    y += 1.05;
  }
  card(s, MARGIN, 5.25, CONTENT_W, 1.45, C.background2, "tarjeta-iteracion");
  await iconCircle(s, MARGIN + 0.3, 5.68, 0.6, "FaArrowsRotate", C.accent2, "icono-iteracion");
  text(s, [
    { text: "Iteración guiada por pruebas", options: { bold: true, fontSize: 15, color: C.accent2, breakLine: true } },
    { text: "Con una selfie muy cercana y en contrapicado, el detector no encontraba la cara y el recorte la achataba. Ahora el recorte siempre es cuadrado, nunca corta la cabeza y se corrige la rotación EXIF de las fotos de celular.", options: { fontSize: 15, color: C.text1 } },
  ], { x: MARGIN + 1.15, y: 5.37, w: CONTENT_W - 1.45, h: 1.25, valign: "middle", paraSpaceAfter: 3 });
  register(s, {
    title: "Preprocesamiento: detectar, recortar y describir",
    speaker: "M",
    time: 60,
    notes: "El preprocesamiento es más importante de lo que parece. Usamos dos detectores de rostro Haar de OpenCV, recortamos un cuadrado de 512 píxeles centrado en la cara y extraemos los bordes con Canny, con umbrales 100 y 200. Esos bordes son los que ControlNet intenta respetar. Esto lo corregimos gracias a las pruebas: con una selfie muy cercana y tomada desde abajo, el detector no encontraba la cara, y cuando la encontraba, el recorte no cabía y la cara salía achatada. Ahora reducimos la imagen y ecualizamos el contraste antes de detectar, el recorte siempre es cuadrado y corregimos la rotación de las fotos de celular.",
  });
}

async function slideGeneracion() {
  const s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Sistema" });
  s.addText("Dos formas de generar sobre una GPU T4", { placeholder: "title" });
  const cw = (CONTENT_W - 0.25) / 2;
  const methods = [
    { x: MARGIN, fill: C.text2, title: "Nivel Intermedio", sub: "Stable Diffusion 1.5 + ControlNet Canny (img2img)", lines: ["Los bordes de la cara condicionan la imagen (escala 0,85)", "Pensado para fijar la estructura al subir el strength"], stat: "2,61 s", dark: true },
    { x: MARGIN + cw + 0.25, fill: C.background2, title: "Nivel Básico", sub: "Stable Diffusion 1.5 img2img, sin ControlNet", lines: ["Solo la foto y el prompt guían el resultado", "Más rápido, con menos control de la estructura"], stat: "1,96 s", dark: false },
  ];
  for (const m of methods) {
    card(s, m.x, 1.45, cw, 2.85, m.fill, `tarjeta-${m.title}`);
    const main = m.dark ? C.background1 : C.text1;
    const sec = m.dark ? C.background2 : C.text2;
    text(s, m.title, { x: m.x + 0.35, y: 1.65, w: cw - 0.7, h: 0.45, fontSize: 22, bold: true, color: main, fontFace: THEME.headFontFace });
    text(s, m.sub, { x: m.x + 0.35, y: 2.12, w: cw - 0.7, h: 0.4, fontSize: 15, bold: true, color: m.dark ? C.accent4 : C.accent2 });
    text(s, m.lines.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < m.lines.length - 1 } })), { x: m.x + 0.35, y: 2.65, w: cw - 2.45, h: 1.5, fontSize: 14, color: sec, paraSpaceAfter: 6 });
    text(s, m.stat, { x: m.x + cw - 2.0, y: 2.75, w: 1.7, h: 0.7, fontSize: 32, bold: true, color: C.accent1, align: "right", fontFace: THEME.headFontFace });
    text(s, "por imagen en GPU", { x: m.x + cw - 2.2, y: 3.45, w: 1.9, h: 0.3, fontSize: 12, color: sec, align: "right" });
  }
  const bottom = [
    { w: 3.3, icon: "FaServer", title: "Servidor GPU", body: "FastAPI en Colab (Tesla T4), expuesto con un túnel de Cloudflare." },
    { w: 3.3, icon: "FaPlug", title: "Respaldo sin GPU", body: "Filtro OpenCV, no generativo: la interfaz sigue funcionando." },
    { w: CONTENT_W - 6.6 - 0.5, icon: "FaPuzzlePiece", title: "LoRA público: detail-tweaker (escala 0,6)", body: "En la primera corrida no cargó por un conflicto de versiones de torchao en Colab. El notebook lo desinstala y en la segunda corrida el LoRA cargó: +1 % de detalle con los estilos, +4,9 % con strength 0,60." },
  ];
  let x = MARGIN;
  for (let i = 0; i < bottom.length; i++) {
    const b = bottom[i];
    card(s, x, 4.55, b.w, 2.15, C.background2, `tarjeta-inferior-${i}`);
    await iconCircle(s, x + 0.3, 4.8, 0.55, b.icon, i === 2 ? C.accent1 : C.accent2, `icono-inferior-${i}`);
    text(s, b.title, { x: x + 1.05, y: 4.82, w: b.w - 1.3, h: 0.5, fontSize: 15, bold: true, valign: "middle" });
    text(s, b.body, { x: x + 0.3, y: 5.45, w: b.w - 0.55, h: 1.15, fontSize: 14, color: C.text2 });
    x += b.w + 0.25;
  }
  register(s, {
    title: "Dos formas de generar sobre una GPU T4",
    speaker: "M",
    time: 90,
    notes: "Implementamos dos formas de generar, como pide el enunciado. El nivel intermedio usa Stable Diffusion 1.5 con ControlNet Canny en modo img2img: los bordes de la cara condicionan la imagen con una escala de 0,85. El nivel básico usa el mismo modelo en img2img, pero sin ControlNet. En la GPU T4, sin LoRA, el intermedio tarda 2,61 segundos por imagen y el básico 1,96; con LoRA, 2,88 y 2,28. Si no hay GPU, la app tiene un respaldo con filtros de OpenCV, que no es generativo, solo para que la interfaz siga funcionando. Sobre personalización: usamos un LoRA público, detail-tweaker, con escala 0,6. En la primera corrida en Colab el LoRA no cargó por un conflicto de versiones de torchao: Colab trae la versión 0.10 y la librería peft exige una mayor a 0.16. El notebook ahora la desinstala, y en la segunda corrida el LoRA cargó y se aplicó a todas las variaciones. Su efecto es pequeño: aumenta el detalle entre 1 y 5 por ciento y suma unos 0,3 segundos por imagen, sin cambiar la identidad.",
  });
}

async function slideInterfaz() {
  const s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Sistema" });
  s.addText("Interfaz: cada imagen espera la decisión humana", { placeholder: "title" });
  const h = 5.2;
  const w = h * 1300 / 970;
  frame(s, MARGIN, 1.45, w, h, "marco-interfaz");
  s.addImage({ path: fig("fig6_interfaz_votacion.png"), x: MARGIN, y: 1.45, w, h, altText: "Interfaz con la foto de entrada y las variaciones con su decisión", objectName: "captura-interfaz" });
  const rows = [
    ["FaClock", "Estado Pendiente hasta que la persona vota"],
    ["FaCheck", "Aceptar o Rechazar en cada imagen"],
    ["FaStar", "Calificación de 1 a 5 y comentario"],
    ["FaFileArrowDown", "Registro en user_decisions.json, descargable"],
    ["FaUsers", "Sesión guardada por participante"],
    ["FaSliders", "8 presets, 3 paquetes y prompt libre"],
  ];
  let y = 1.55;
  const x = MARGIN + w + 0.45;
  for (const [iconName, label] of rows) {
    await iconCircle(s, x, y, 0.55, iconName, C.accent1, `icono-${label}`);
    text(s, label, { x: x + 0.8, y, w: 12.73 - x - 0.8, h: 0.55, fontSize: 16, valign: "middle" });
    y += 0.84;
  }
  register(s, {
    title: "Interfaz: cada imagen espera la decisión humana",
    speaker: "M",
    time: 45,
    notes: "La interfaz está pensada para que la decisión sea siempre humana. Cada imagen empieza en estado Pendiente. Debajo tiene los botones Aceptar y Rechazar, una calificación de 1 a 5 y un campo de comentario. Todo se guarda al instante en un archivo JSON que se puede descargar, y cada sesión se guarda por participante. Hay ocho estilos, agrupados en tres paquetes, y un prompt libre para pedir detalles como el color de la corbata. Ahora lo vemos funcionando.",
  });
}

async function slideDemo() {
  pres.addSection({ title: "Demo" });
  const s = pres.addSlide({ masterName: "OSCURO", sectionTitle: "Demo" });
  s.addText("Demo en vivo", { placeholder: "title" });
  text(s, "La app local conectada al servidor GPU de Colab", { x: MARGIN, y: 1.55, w: 8, h: 0.45, fontSize: 18, color: C.background2 });
  const steps = [
    "Conectar la app al servidor GPU de Colab",
    "Subir la foto y generar el paquete de 5",
    "Aceptar o rechazar las 5 variaciones y comentar",
    "Pedir la explicación a Gemini",
    "Probar el filtro ético con «sin ropa»",
  ];
  let y = 2.4;
  for (let i = 0; i < steps.length; i++) {
    numberCircle(s, MARGIN, y, 0.6, i + 1);
    text(s, steps[i], { x: MARGIN + 0.85, y, w: 7.2, h: 0.6, fontSize: 19, color: C.background1, valign: "middle" });
    y += 0.8;
  }
  text(s, "Plan B: modo Contingencia local e imágenes ya generadas en Colab", { x: MARGIN, y: 6.45, w: 8, h: 0.35, fontSize: 14, italic: true, color: C.accent4 });
  const h = 5.25;
  const w = h * 1600 / 2500;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 12.73 - w - 0.06, y: 1.39, w: w + 0.12, h: h + 0.12, rectRadius: 0.08, fill: { color: C.text2 }, line: { color: C.accent1, width: 1.5 }, objectName: "marco-demo" });
  s.addImage({ path: fig("anexo_interfaz_completa.png"), x: 12.73 - w, y: 1.45, w, h, altText: "Vista completa de la aplicación", objectName: "captura-demo" });
  register(s, {
    title: "Demo en vivo",
    speaker: "M",
    time: 210,
    notes: "Vamos a la demo. [Seguir los pasos de la sección «Demo en vivo» del guion.] Mientras se generan las imágenes: la app manda la foto al servidor de Colab; cada imagen tarda entre dos y tres segundos en la GPU, y con la red el lote completo toma de 25 a 35 segundos. [Votar las cinco en voz alta, diciendo por qué se acepta o se rechaza cada una.] [Pedir la explicación con Gemini y leer la lista de aceptadas y rechazadas, y la fidelidad.] [Escribir «sin ropa» en el prompt libre y mostrar el bloqueo.] Eso es el sistema completo. Alejandro les cuenta qué encontramos al evaluarlo.",
  });
}

async function slideResultados() {
  pres.addSection({ title: "Resultados" });
  const s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Resultados" });
  s.addText("Resultados: 5 variaciones por foto en segundos", { placeholder: "title" });
  const tile = 1.55;
  const gap = 0.12;
  const startX = 2.7;
  const rowsY = [1.45, 3.12];
  const labels = [["Nivel Intermedio", "ControlNet Canny"], ["Nivel Básico", "img2img"]];
  const prefixes = ["intermedio", "basico"];
  for (let r = 0; r < 2; r++) {
    text(s, [
      { text: labels[r][0], options: { bold: true, fontSize: 17, breakLine: true, fontFace: THEME.headFontFace } },
      { text: labels[r][1], options: { fontSize: 13, color: C.text2 } },
    ], { x: MARGIN, y: rowsY[r] + 0.45, w: 1.95, h: 0.8 });
    for (let i = 0; i < 6; i++) {
      const x = startX + i * (tile + gap);
      if (i === 0) s.addShape(pres.shapes.RECTANGLE, { x: x - 0.04, y: rowsY[r] - 0.04, w: tile + 0.08, h: tile + 0.08, fill: { color: C.accent1 }, line: { color: C.accent1, width: 0 }, objectName: `borde-entrada-${r}` });
      s.addImage({ path: img(`${prefixes[r]}_${i}.png`), x, y: rowsY[r], w: tile, h: tile, altText: `${labels[r][0]} ${i}`, objectName: `variacion-${prefixes[r]}-${i}` });
    }
  }
  const captions = ["Entrada", "Formal Clásico", "Business Casual", "Smart Casual", "WhatsApp Business", "WhatsApp Smart"];
  for (let i = 0; i < 6; i++) {
    text(s, captions[i], { x: startX + i * (tile + gap) - 0.05, y: 4.72, w: tile + 0.1, h: 0.3, fontSize: 11, color: i === 0 ? C.accent1 : C.text2, bold: i === 0, align: "center" });
  }
  const stats = [
    ["2,61 s", "por imagen · Nivel Intermedio (GPU)"],
    ["1,96 s", "por imagen · Nivel Básico (GPU)"],
    ["25 a 35 s", "por lote de 5 desde la app (5 a 7 s por imagen, incluye la red por el túnel de Cloudflare)"],
    ["0", "imágenes marcadas por el filtro de contenido de Stable Diffusion"],
  ];
  const sw = (CONTENT_W - 0.75) / 4;
  for (let i = 0; i < stats.length; i++) {
    const x = MARGIN + i * (sw + 0.25);
    card(s, x, 5.2, sw, 1.5, C.background2, `tarjeta-dato-${i}`);
    text(s, stats[i][0], { x: x + 0.25, y: 5.28, w: sw - 0.5, h: 0.6, fontSize: 28, bold: true, color: C.accent1, fontFace: THEME.headFontFace });
    text(s, stats[i][1], { x: x + 0.25, y: 5.88, w: sw - 0.45, h: 0.78, fontSize: 12, color: C.text2 });
  }
  register(s, {
    title: "Resultados: 5 variaciones por foto en segundos",
    speaker: "A",
    time: 60,
    notes: "Gracias, Matías. Estos son resultados reales de la GPU, con la misma foto y las mismas semillas para los dos métodos. Arriba, el nivel intermedio con ControlNet; abajo, el básico. En la GPU cada imagen tarda 2,61 y 1,96 segundos sin LoRA, y unos 0,3 segundos más con LoRA. Desde la app, el lote de cinco toma de 25 a 35 segundos, entre 5 y 7 segundos por imagen, porque incluye la red por el túnel de Cloudflare. El filtro de contenido de Stable Diffusion no marcó ninguna imagen. Pero si miran la ropa, casi no cambia: la polera sigue ahí en casi todas. Eso nos llevó al hallazgo principal.",
  });
}

async function slideIdentidad() {
  const s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Resultados" });
  s.addText("Hallazgo: más cambio de ropa, menos identidad", { placeholder: "title" });
  const tile = 1.85;
  const gap = 0.15;
  const captions = ["Entrada", "strength 0,45", "strength 0,60", "strength 0,75"];
  for (let i = 0; i < 4; i++) {
    const x = MARGIN + i * (tile + gap);
    if (i === 0) s.addShape(pres.shapes.RECTANGLE, { x: x - 0.04, y: 1.46, w: tile + 0.08, h: tile + 0.08, fill: { color: C.accent1 }, line: { color: C.accent1, width: 0 }, objectName: "borde-entrada" });
    s.addImage({ path: img(`barrido_${i}.png`), x, y: 1.5, w: tile, h: tile, altText: captions[i], objectName: `barrido-${i}` });
    text(s, captions[i], { x, y: 3.45, w: tile, h: 0.3, fontSize: 12, color: i === 0 ? C.accent1 : C.text2, bold: i === 0, align: "center" });
  }
  text(s, "Sesgo a discutir: el modelo empuja rasgos de apariencia, como el pelo, hacia los patrones de sus datos de entrenamiento (LAION).", { x: MARGIN, y: 4.0, w: 7.85, h: 0.9, fontSize: 15, italic: true, color: C.text2 });
  const findings = [
    ["0,42–0,48: ", "la ropa casi no cambia (diferencia media entre pares de 0,036 a 0,040, escala 0–1)."],
    ["≥ 0,60: ", "aparece el terno, pero el pelo pasa de liso a ondulado o crespo (también en 2 de 5 variaciones)."],
    ["«Formal Clásico»: ", "el color «navy blue» del terno se filtra al pelo."],
    ["Piel: ", "cambio pequeño, ΔL* −0,4 en el centro de la cara y hasta −2,2 en la cara completa."],
  ];
  text(s, findings.map((f, i) => ({ text: f[0] + f[1], options: { bullet: true, breakLine: i < findings.length - 1 } })), { x: 8.85, y: 1.5, w: 3.88, h: 3.6, fontSize: 14, color: C.text1, paraSpaceAfter: 8 });
  card(s, MARGIN, 5.3, CONTENT_W, 1.4, C.text2, "tarjeta-mejora");
  await iconCircle(s, MARGIN + 0.35, 5.7, 0.6, "FaMaskFace", C.accent1, "icono-mejora");
  text(s, [
    { text: "Mejora propuesta: inpainting con máscara facial", options: { bold: true, fontSize: 17, color: C.background1, breakLine: true } },
    { text: "Conservar los píxeles de la cara y el pelo, y regenerar solo la ropa y el fondo: así se puede subir el strength sin perder identidad.", options: { fontSize: 15, color: C.background2 } },
  ], { x: MARGIN + 1.25, y: 5.42, w: CONTENT_W - 1.55, h: 1.16, valign: "middle", paraSpaceAfter: 3 });
  register(s, {
    title: "Hallazgo: más cambio de ropa, menos identidad",
    speaker: "A",
    time: 85,
    notes: "Probamos tres valores de strength, que controla cuánto puede cambiar el modelo. Con los valores que usamos por defecto, entre 0,42 y 0,48, la ropa casi no cambia: la diferencia media entre pares de imágenes es de apenas 0,036 a 0,040 en una escala de cero a uno. Con 0,60 o más aparece el terno, pero la identidad se degrada: el pelo pasa de liso a ondulado o crespo, algo que también vimos en dos de las cinco variaciones. Además, en el estilo Formal Clásico el color navy blue del terno se filtra al pelo. Medimos el tono de piel y el cambio es pequeño: menos 0,4 de luminosidad en el centro de la cara y hasta menos 2,2 en la cara completa. Es un sesgo que hay que discutir: el modelo empuja rasgos hacia los patrones de sus datos de entrenamiento. La mejora que proponemos es inpainting con una máscara facial: conservar los píxeles de la cara y el pelo, y regenerar solo la ropa y el fondo.",
  });
}

async function slideAgente() {
  const s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Resultados" });
  s.addText("Agente explicador: fiel a las decisiones", { placeholder: "title" });
  const h = 5.25;
  const w = h * 1220 / 1340;
  frame(s, MARGIN, 1.45, w, h, "marco-agente");
  s.addImage({ path: fig("fig7_agente.png"), x: MARGIN, y: 1.45, w, h, altText: "Resumen del agente con Gemini: aceptadas, rechazadas y fidelidad", objectName: "captura-agente" });
  const x0 = MARGIN + w + 0.45;
  const avail = 12.73 - x0;
  const stats = [
    ["10 / 10", "corridas con 100% de fidelidad (Gemini 3.5 Flash Lite)"],
    ["100%", "agente de reglas offline"],
    ["11,9 s", "latencia media; máximo 19,9 s"],
  ];
  const sw = (avail - 0.5) / 3;
  for (let i = 0; i < stats.length; i++) {
    const x = x0 + i * (sw + 0.25);
    card(s, x, 1.45, sw, 1.55, C.background2, `tarjeta-agente-${i}`);
    text(s, stats[i][0], { x: x + 0.2, y: 1.55, w: sw - 0.4, h: 0.6, fontSize: 28, bold: true, color: C.accent1, fontFace: THEME.headFontFace });
    text(s, stats[i][1], { x: x + 0.2, y: 2.15, w: sw - 0.35, h: 0.8, fontSize: 12, color: C.text2 });
  }
  const rows = [
    ["FaListCheck", "Lista explícita", "Siempre muestra qué se aceptó y qué se rechazó, tomado del JSON."],
    ["FaRobot", "Cadena de respaldo", "3.1 Flash Lite, flash-lite-latest y 3.8 Flash; si todo falla, agente de reglas."],
    ["FaScaleBalanced", "Métrica de fidelidad", "Cada título con su decisión y los conteos. La v1 daba 93,8% por negaciones («no fue aceptada»); se corrigió. Supone una salida por secciones."],
  ];
  let y = 3.3;
  for (const [iconName, title, body] of rows) {
    await iconRow(s, x0, y, avail, iconName, title, body, { d: 0.55, titleSize: 15, bodySize: 14, h: 1.1 });
    y += 1.12;
  }
  register(s, {
    title: "Agente explicador: fiel a las decisiones",
    speaker: "A",
    time: 75,
    notes: "El agente explicador usa Gemini 3.5 Flash Lite. Si ese modelo está saturado, prueba otros tres en cadena, y si todo falla usa un agente de reglas que funciona sin internet. Para controlar alucinaciones, la app siempre muestra primero la lista exacta de aceptadas y rechazadas, tomada del JSON, y después la explicación del modelo. Además medimos la fidelidad: revisamos que cada título aparezca con su decisión correcta y que los conteos coincidan. En diez corridas con decisiones distintas, Gemini obtuvo 100% en las diez, igual que el agente de reglas, con una latencia media de 11,9 segundos. Una aclaración honesta: la primera versión de la métrica daba 93,8%, pero eran falsos negativos de la métrica cuando el modelo escribía frases como «no fue aceptada»; la corregimos. Su límite es que supone una respuesta ordenada por secciones.",
  });
}

async function slideEtica() {
  const s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Resultados" });
  s.addText("Ética: guardrails antes, durante y después", { placeholder: "title" });
  const h = 3.25;
  const w = h * 300 / 370;
  frame(s, MARGIN, 1.5, w, h, "marco-filtro");
  s.addImage({ path: fig("fig8_filtro.png"), x: MARGIN, y: 1.5, w, h, altText: "El filtro ético bloquea la solicitud «sin ropa»", objectName: "captura-filtro" });
  text(s, "Bloqueo de «sin ropa» antes de la GPU", { x: MARGIN - 0.15, y: 1.5 + h + 0.12, w: w + 0.3, h: 0.5, fontSize: 11, color: C.text2, align: "center" });
  const x0 = MARGIN + w + 0.45;
  const cw = (12.73 - x0 - 0.5) / 3;
  const cols = [
    ["FaShieldHalved", "Antes de generar", "Filtro léxico y regex con normalización NFKD y de números usados como letras («s1n r0pa», «shirtless»). Bloquea antes de la GPU."],
    ["FaImage", "Al generar", "Filtro de contenido de Stable Diffusion activo: ninguna imagen marcada en las pruebas."],
    ["FaLock", "Después: los datos", "Fotos y decisiones en data/processed, fuera del repositorio. API key en .env no versionado. Solo la propia foto, con consentimiento."],
  ];
  for (let i = 0; i < cols.length; i++) {
    const x = x0 + i * (cw + 0.25);
    card(s, x, 1.45, cw, 3.65, C.background2, `tarjeta-etica-${i}`);
    await iconCircle(s, x + 0.3, 1.7, 0.6, cols[i][0], C.accent2, `icono-etica-${i}`);
    text(s, cols[i][1], { x: x + 0.3, y: 2.45, w: cw - 0.6, h: 0.4, fontSize: 17, bold: true });
    text(s, cols[i][2], { x: x + 0.3, y: 2.9, w: cw - 0.5, h: 2.1, fontSize: 14, color: C.text2 });
  }
  const bw = (CONTENT_W - 0.25) / 2;
  const blocks = [
    ["FaTriangleExclamation", "Riesgos", "Suplantación o manipulación de identidad, y sesgo de un modelo entrenado con datos web (LAION)."],
    ["FaCopyright", "Propiedad intelectual", "SD 1.5 bajo CreativeML OpenRAIL-M y ControlNet bajo OpenRAIL: uso permitido con restricciones de uso responsable."],
  ];
  for (let i = 0; i < blocks.length; i++) {
    const x = MARGIN + i * (bw + 0.25);
    card(s, x, 5.4, bw, 1.3, C.text2, `tarjeta-riesgo-${i}`);
    await iconCircle(s, x + 0.3, 5.75, 0.6, blocks[i][0], C.accent1, `icono-riesgo-${i}`);
    text(s, [
      { text: blocks[i][1], options: { bold: true, fontSize: 15, color: C.background1, breakLine: true } },
      { text: blocks[i][2], options: { fontSize: 14, color: C.background2 } },
    ], { x: x + 1.15, y: 5.48, w: bw - 1.4, h: 1.14, valign: "middle", paraSpaceAfter: 2 });
  }
  register(s, {
    title: "Ética: guardrails antes, durante y después",
    speaker: "J",
    time: 65,
    notes: "En ética trabajamos en tres momentos. Antes de generar, un filtro bloquea términos de desnudez, violencia o contenido no profesional; normaliza tildes y números usados como letras, así que «s1n r0pa» también se bloquea, y lo hace antes de usar la GPU. Al generar, dejamos activo el filtro de contenido de Stable Diffusion. Y con los datos: las fotos y decisiones quedan fuera del repositorio, la clave de la API está en un archivo que no se versiona, y el sistema está pensado para usarse solo con la propia foto y con consentimiento. Los riesgos principales son la suplantación de identidad y el sesgo del modelo. Sobre propiedad intelectual, Stable Diffusion 1.5 y ControlNet tienen licencias OpenRAIL, que permiten su uso con restricciones de uso responsable.",
  });
}

async function slideIteraciones() {
  const s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Resultados" });
  s.addText("Iteraciones guiadas por pruebas", { placeholder: "title" });
  const rows = [
    ["Selfie cercana y en contrapicado: no se detectaba la cara", "Reducción de escala, ecualización y dos cascadas Haar"],
    ["El recorte deformaba la cara cuando no cabía", "Recorte siempre cuadrado que no corta la cabeza"],
    ["Fotos de celular llegaban rotadas", "Corrección de la rotación EXIF"],
    ["Gemini 2.5 Flash retirado; modelos grandes saturados (503, timeouts)", "Cadena de modelos lite: de 68 s a 4–20 s"],
    ["Cortes del túnel de Cloudflare", "Reintento automático de la petición"],
    ["Falsos negativos de la métrica con negaciones", "Manejo de negaciones: de 93,8% a 100%"],
    ["Filtro ético evadible («s1n r0pa», «shirtless»)", "Normalización de números y léxico ampliado"],
    ["1.ª corrida: el LoRA no cargó por torchao 0.10.0", "Se desinstala torchao: el LoRA carga en la 2.ª corrida"],
  ];
  const head = (t) => ({ text: t, options: { bold: true, color: C.background1, fill: { color: C.text2 }, fontSize: 14 } });
  const tableRows = [[head("#"), head("Problema detectado"), head("Cambio aplicado")]];
  rows.forEach((r, i) => {
    const fill = { color: i % 2 === 0 ? C.background2 : C.background1 };
    tableRows.push([
      { text: String(i + 1), options: { bold: true, color: C.accent1, fill, align: "center" } },
      { text: r[0], options: { color: C.text1, fill } },
      { text: r[1], options: { color: C.text2, fill } },
    ]);
  });
  s.addTable(tableRows, {
    x: MARGIN, y: 1.45, w: CONTENT_W, colW: [0.55, 5.9, CONTENT_W - 6.45],
    fontSize: 14, fontFace: THEME.bodyFontFace, valign: "middle", rowH: 0.56,
    border: { type: "solid", pt: 0.5, color: "D3DAE0" }, margin: [0.04, 0.12, 0.04, 0.12],
  });
  register(s, {
    title: "Iteraciones guiadas por pruebas",
    speaker: "M",
    time: 45,
    notes: "Esta tabla resume cómo las pruebas guiaron el desarrollo. Cada fila es un problema que encontramos usando el sistema y el cambio que hicimos: desde la detección de la cara y el recorte, hasta la cadena de modelos de Gemini, que bajó la espera de 68 segundos a entre 4 y 20, el reintento ante cortes del túnel, la métrica de fidelidad, el filtro ético y el conflicto de versiones que impidió cargar el LoRA en la primera corrida.",
  });
}

async function slideConclusiones() {
  pres.addSection({ title: "Cierre" });
  const s = pres.addSlide({ masterName: "OSCURO", sectionTitle: "Cierre" });
  s.addText("Conclusiones y próximos pasos", { placeholder: "title" });
  const cw = (CONTENT_W - 0.4) / 2;
  const cols = [
    { x: MARGIN, title: "Logrado", icon: "FaCheck", fill: C.accent6, items: [
      "Dos formas de generar en GPU, con 5 variaciones por foto",
      "Decisión por imagen con registro estructurado",
      "Agente con 100% de fidelidad en 10 corridas",
      "Guardrails éticos antes y durante la generación",
    ] },
    { x: MARGIN + cw + 0.4, title: "Próximos pasos", icon: "FaArrowRight", fill: C.accent1, items: [
      "Inpainting con máscara facial para preservar la identidad",
      "Entrenar un LoRA propio de retrato corporativo",
      "Evaluar también la calidad de las razones del agente",
      "Más variedad de ropa sin tocar el rostro",
    ] },
  ];
  for (const col of cols) {
    text(s, col.title, { x: col.x, y: 1.85, w: cw, h: 0.5, fontSize: 22, bold: true, color: col.fill === C.accent6 ? C.accent4 : C.accent4, fontFace: THEME.headFontFace });
    let y = 2.55;
    for (const item of col.items) {
      await iconCircle(s, col.x, y, 0.5, col.icon, col.fill, `icono-${item}`);
      text(s, item, { x: col.x + 0.75, y: y - 0.05, w: cw - 0.8, h: 0.6, fontSize: 17, color: C.background1, valign: "middle" });
      y += 0.82;
    }
  }
  text(s, "Gracias. Quedamos atentos a sus preguntas.", { x: MARGIN, y: 6.0, w: 7.5, h: 0.5, fontSize: 22, bold: true, color: C.background1, fontFace: THEME.headFontFace });
  text(s, [{ text: "github.com/KarTaGo124/Planning-Decision-Making-AI", options: { hyperlink: { url: REPO_URL }, color: C.accent4 } }], { x: 7.6, y: 6.08, w: 5.13, h: 0.4, fontSize: 14, align: "right" });
  register(s, {
    title: "Conclusiones y próximos pasos",
    speaker: "A",
    time: 60,
    notes: "Para cerrar. Logramos un sistema completo: dos formas de generar en GPU con cinco variaciones por foto, una interfaz donde la persona decide imagen por imagen con un registro estructurado, un agente con 100% de fidelidad en nuestras pruebas y guardrails éticos. También encontramos su límite principal: con Stable Diffusion 1.5 en img2img, cambiar la ropa y conservar la identidad están en tensión. Los próximos pasos son el inpainting con máscara facial, entrenar un LoRA propio de retrato corporativo y evaluar también la calidad de las razones que da el agente. El código está en el repositorio que ven en pantalla. Muchas gracias; quedamos atentos a sus preguntas.",
  });
}

function mmss(seconds) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
}

function buildScript() {
  const total = SLIDES.reduce((acc, s) => acc + s.time, 0);
  const demo = SLIDES.find((s) => s.title === "Demo en vivo").time;
  const lines = [];
  lines.push("# Guion de exposición · Proyecto 2 · Grupo 7");
  lines.push("");
  lines.push("Retratos profesionales con IA, decididos por el usuario. CS5363 Planificación y Toma de Decisiones en IA, UTEC 2026-2.");
  lines.push("");
  lines.push(`Duración total: ${mmss(total)} (exposición ${mmss(total - demo)} y demo en vivo ${mmss(demo)}), dentro de los 15 a 20 minutos. Después vienen 10 minutos de preguntas del jurado.`);
  lines.push("");
  lines.push("Quién habla: José (diapositivas 1 a 4 y 13), Matías (5 a 9 y 14, y opera la demo), Alejandro (10 a 12 y 15). El texto de cada bloque está también en las notas del orador de la presentación.");
  lines.push("");
  lines.push("## Bloques y tiempos");
  lines.push("");
  lines.push("| # | Diapositiva | Habla | Tiempo | Acumulado |");
  lines.push("|---|---|---|---|---|");
  let acc = 0;
  SLIDES.forEach((s, i) => {
    acc += s.time;
    lines.push(`| ${i + 1} | ${s.title} | ${SPEAKERS[s.speaker]} | ${mmss(s.time)} | ${mmss(acc)} |`);
  });
  lines.push("");
  lines.push("## Texto para leer");
  lines.push("");
  SLIDES.forEach((s, i) => {
    lines.push(`### ${i + 1}. ${s.title} · ${SPEAKERS[s.speaker]} · ${mmss(s.time)}`);
    lines.push("");
    lines.push(s.notes);
    lines.push("");
  });
  lines.push(...DEMO_SECTION);
  lines.push(...QUESTIONS_SECTION);
  return lines.join("\n");
}

const DEMO_SECTION = [
  "## Demo en vivo: pasos exactos",
  "",
  "Preparación, 15 a 20 minutos antes de exponer (la primera vez Colab descarga unos 5 GB de modelos):",
  "",
  "1. Abrir https://colab.research.google.com, ir a **Archivo, Subir notebook** y elegir `Project-II/notebooks/controlnet_portrait_pipeline.ipynb`.",
  "2. **Entorno de ejecución, Cambiar tipo de entorno de ejecución, T4 GPU**, Guardar.",
  "3. **Entorno de ejecución, Ejecutar todas**. Cuando la sección 4 lo pida, subir la foto.",
  "4. Esperar la sección 9 y copiar la URL que termina en `.trycloudflare.com`. No cerrar la pestaña de Colab: esa celda queda corriendo.",
  "5. Revisar que exista el archivo `.env` con `GEMINI_API_KEY` en la raíz del repositorio de la laptop de la demo.",
  "6. En la laptop, doble clic en `Project-II/run_app.bat`. Se abre http://localhost:8501.",
  "7. En la barra lateral, en **Motor generativo**, elegir **Nivel Intermedio (ControlNet Canny + img2img, GPU)**. Pegar la URL y presionar **Probar Conexión GPU**. Debe aparecer `Conectado: Tesla T4 · LoRA activo`. Si dice `LoRA no cargado`, se puede seguir igual.",
  "",
  "Durante la demo (unos 3 minutos y medio):",
  "",
  "1. En **1. Fotografía de Entrada**, subir la foto.",
  "2. En **Seleccione un paquete sugerido**, dejar **Paquete Corporativo Multiplataforma (5 Variaciones)**.",
  "3. Presionar **Generar Variaciones Visuales**. Tarda de 25 a 35 s; mientras tanto, explicar que la foto viaja al servidor de Colab.",
  "4. Votar las 5 variaciones con **Aceptar** o **Rechazar**, mover la calificación y escribir un comentario corto en una o dos. Decir en voz alta por qué.",
  "5. En **Modelo para Sintetizar Explicaciones**, elegir **Google Gemini Flash (API)** y presionar **Generar Explicación con Agente IA**. Leer la lista de aceptadas y rechazadas y la fidelidad.",
  "6. En **Personalización (Prompt Libre)**, escribir `sin ropa` y presionar Enter. Mostrar el bloqueo en rojo.",
  "",
  "Si una generación falla con «Remote end closed connection», es un corte del túnel: presionar de nuevo **Generar Variaciones Visuales**.",
  "",
  "## Plan B si falla la GPU",
  "",
  "1. Elegir **Contingencia local (filtro OpenCV, sin modelo generativo)** y decirlo explícitamente: ese modo no es generativo, pero el flujo de decisión, el registro en JSON, el agente y el filtro ético funcionan igual.",
  "2. Mostrar las imágenes reales ya generadas en Colab: diapositivas 10 y 11, y la carpeta `Project-II/data/processed/colab_v1_img2img_sin_preservacion/` (archivos `resumen_*.png`).",
  "3. Si Gemini no responde, el agente usa otro modelo de la cadena o el agente de reglas, que funciona sin internet. La app muestra el motivo en «Modelo Utilizado».",
  "",
];

const QUESTIONS_SECTION = [
  "## Preguntas probables del jurado",
  "",
  "**1. ¿Por qué Stable Diffusion 1.5 y no un modelo más nuevo?**",
  "Porque corre con ControlNet y LoRA dentro de la GPU T4 gratuita de Colab, con 2 a 3 s por imagen, y su ecosistema está maduro. Modelos más grandes superan la memoria o el tiempo disponibles gratis.",
  "",
  "**2. ¿El sistema preserva la identidad?**",
  "No del todo. Con strength bajo la ropa casi no cambia y, aun así, el pelo cambió de textura en 2 de 5 variaciones; con 0,60 o más aparece el terno y el cambio de identidad es mayor. Lo medimos y lo presentamos como la limitación principal. La mejora es inpainting con máscara facial.",
  "",
  "**3. ¿Qué aporta ControlNet si el nivel básico se parece tanto?**",
  "Con strength entre 0,42 y 0,48 ambos dependen sobre todo de la foto inicial, así que las diferencias fueron pequeñas. ControlNet está pensado para fijar la estructura de la cara cuando se sube el strength, pero no comparamos los dos métodos con strength alto: es una prueba pendiente. Cuesta 0,65 s más por imagen.",
  "",
  "**4. ¿Por qué no entrenaron un LoRA propio?**",
  "Por tiempo y por las restricciones de acceso a Khipu. Usamos un LoRA público de detalle. En la primera corrida no cargó por un conflicto de versiones de torchao en Colab; el notebook lo corrige y en la segunda corrida cargó. Su efecto es pequeño (1 a 5 % más de detalle), así que el siguiente paso sería entrenar uno propio con retratos corporativos.",
  "",
  "**5. ¿Cómo saben que el agente no inventa decisiones?**",
  "La app muestra primero la lista exacta de aceptadas y rechazadas, tomada del JSON, y aparte medimos la fidelidad de la explicación del modelo: 100% en 10 corridas. La métrica no evalúa si las razones son buenas, solo que sean consistentes con los datos, y supone una respuesta ordenada por secciones.",
  "",
  "**6. ¿Qué pasa si Gemini no responde?**",
  "El agente prueba otros tres modelos en cadena y, si ninguno responde, usa el agente de reglas, que funciona sin internet. La demo no depende de que Gemini esté disponible.",
  "",
  "**7. ¿Se puede engañar al filtro ético?**",
  "Es un filtro léxico: cubre tildes, mayúsculas y números usados como letras, pero no entiende paráfrasis elaboradas. Por eso hay una segunda capa, el filtro de contenido de Stable Diffusion, que está activo.",
  "",
  "**8. ¿Qué datos guardan y dónde?**",
  "Las decisiones, sesiones e imágenes quedan en `data/processed`, que está fuera del repositorio. La foto se envía al servidor de Colab del propio equipo y no se publica. La API key está en un `.env` que no se versiona.",
  "",
  "**9. ¿Usaron un dataset de rostros?**",
  "No entrenamos un modelo: usamos modelos preentrenados, y la entrada es la foto de la persona. El sesgo que observamos viene de los datos con que se entrenó Stable Diffusion (LAION). Las pruebas se hicieron con fotos del equipo, con consentimiento.",
  "",
  "**10. ¿De quién es la propiedad intelectual de las imágenes generadas?**",
  "Stable Diffusion 1.5 (CreativeML OpenRAIL-M) y ControlNet (OpenRAIL) permiten el uso de las imágenes con restricciones de uso responsable. La foto de entrada es de la propia persona y no usamos fotos de terceros.",
  "",
];

(async () => {
  await slidePortada();
  await slideProblema();
  await slideDesignThinking();
  await slideJourney();
  await slideArquitectura();
  await slidePreproceso();
  await slideGeneracion();
  await slideInterfaz();
  await slideDemo();
  await slideResultados();
  await slideIdentidad();
  await slideAgente();
  await slideEtica();
  await slideIteraciones();
  await slideConclusiones();
  await pres.writeFile({ fileName: OUT_PPTX });
  if (APPLY_THEME) {
    const { applyTheme } = require(APPLY_THEME);
    await applyTheme(OUT_PPTX, THEME);
  }
  fs.writeFileSync(OUT_MD, buildScript(), "utf8");
  const total = SLIDES.reduce((acc, s) => acc + s.time, 0);
  for (const [i, s] of SLIDES.entries()) {
    const words = s.notes.split(/\s+/).length;
    console.log(`${i + 1}. ${s.title} | ${SPEAKERS[s.speaker]} | ${mmss(s.time)} | ${words} palabras (~${mmss(Math.round(words / 135 * 60))} a 135 ppm)`);
  }
  console.log(`total ${mmss(total)}`);
})();
