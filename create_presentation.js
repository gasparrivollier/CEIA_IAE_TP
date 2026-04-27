const PptxGenJS = require("pptxgenjs");

const prs = new PptxGenJS();

// Configuración
prs.defineLayout({ name: "BLANK", master: "BLANK" });

// Colores
const colors = {
  darkBlue: "1E2761",
  lightBlue: "CADCFC",
  white: "FFFFFF",
  secondary: "1C7293",
  text: "323232",
  lightBg: "F5F5F5",
  accent: "FF6B6B"
};

// Función para agregar diapositiva de título
function addTitleSlide(title, subtitle) {
  let slide = prs.addSlide();
  slide.background = { color: colors.darkBlue };

  slide.addText(title, {
    x: 0.5, y: 2.5, w: 9, h: 1.5,
    fontSize: 54, bold: true, color: colors.white,
    align: "center", fontFace: "Calibri"
  });

  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.5, y: 4.2, w: 9, h: 2,
      fontSize: 24, color: colors.lightBlue,
      align: "center", fontFace: "Calibri"
    });
  }
}

// Función para agregar diapositiva de contenido
function addContentSlide(title, items) {
  let slide = prs.addSlide();
  slide.background = { color: colors.lightBg };

  // Título
  slide.addText(title, {
    x: 0.5, y: 0.4, w: 9, h: 0.8,
    fontSize: 40, bold: true, color: colors.darkBlue,
    fontFace: "Calibri"
  });

  // Línea decorativa
  slide.addShape(prs.ShapeType.line, {
    x: 0.5, y: 1.3, w: 9, h: 0,
    line: { color: colors.secondary, width: 3 }
  });

  // Contenido
  let y = 1.8;
  items.forEach((item, idx) => {
    slide.addText(item, {
      x: 0.8, y: y, w: 8.4, h: 0.5,
      fontSize: 16, color: colors.text,
      fontFace: "Calibri", valign: "top"
    });
    y += 0.5;
  });
}

// Función para agregar diapositiva de dos columnas
function addTwoColumnSlide(title, leftItems, rightItems) {
  let slide = prs.addSlide();
  slide.background = { color: colors.lightBg };

  // Título
  slide.addText(title, {
    x: 0.5, y: 0.4, w: 9, h: 0.8,
    fontSize: 40, bold: true, color: colors.darkBlue,
    fontFace: "Calibri"
  });

  // Línea decorativa
  slide.addShape(prs.ShapeType.line, {
    x: 0.5, y: 1.3, w: 9, h: 0,
    line: { color: colors.secondary, width: 3 }
  });

  // Columna izquierda
  let y = 1.8;
  leftItems.forEach((item) => {
    slide.addText(item, {
      x: 0.5, y: y, w: 4.3, h: 0.4,
      fontSize: 14, color: colors.text,
      fontFace: "Calibri", valign: "top"
    });
    y += 0.45;
  });

  // Columna derecha
  y = 1.8;
  rightItems.forEach((item) => {
    slide.addText(item, {
      x: 5.2, y: y, w: 4.3, h: 0.4,
      fontSize: 14, color: colors.text,
      fontFace: "Calibri", valign: "top"
    });
    y += 0.45;
  });
}

// ====== DIAPOSITIVAS ======

// 1. Portada
addTitleSlide(
  "Optimización y Despliegue de IA\nen Entornos Restringidos",
  "Clasificación de Lenguaje de Señas Americano (ASL)\ncon Compresión de Modelos Deep Learning"
);

// 2. Contenido
addContentSlide("Contenido", [
  "✓ Fase 1: Definición del Problema y Restricciones",
  "✓ Fase 2: Arquitectura Baseline y Entrenamiento",
  "✓ Fase 3: Técnicas de Optimización del Modelo",
  "✓ Fase 4: Despliegue y Benchmarking",
  "✓ Resultados Comparativos",
  "✓ Conclusiones"
]);

// 3. Fase 1 - Problema
addContentSlide("Fase 1: Definición del Problema", [
  "📌 Problema: Clasificación de Lenguaje de Señas (ASL)",
  "    • Dataset: ASL Alphabet (Kaggle - grassknoted/asl-alphabet)",
  "    • Clases: 29 señas del alfabeto americano",
  "    • Tipo de tarea: Clasificación de imágenes multiclase",
  "",
  "🎯 Aplicación: Traducción automática de lenguaje de señas",
  "    en tiempo real para dispositivos con restricciones de hardware"
]);

// 4. Fase 1 - Restricciones
addContentSlide("Fase 1: Restricciones de Hardware", [
  "💾 Restricción de Memoria: ≤ 100 MB en disco",
  "    • Modelo baseline FP32: 9.5 MB",
  "",
  "⚡ Restricción de Latencia: < 50 ms por inferencia",
  "    • En CPU (entorno restringido)",
  "",
  "🎯 Restricción de Precisión: ≥ 77% accuracy (drop ≤ 2%)",
  "    • Mantener funcionalidad del modelo",
  "",
  "📊 Métrica de Éxito: Reducir tamaño ≥50% sin perder precisión"
]);

// 5. Arquitectura
addContentSlide("Fase 2: Arquitectura CNN Baseline", [
  "🏗️ Diseño: CNN personalizada (4 bloques convolucionales)",
  "",
  "📐 Capas:",
  "    • Conv1: 32 filtros + BatchNorm + ReLU + MaxPool",
  "    • Conv2: 64 filtros + BatchNorm + ReLU + MaxPool",
  "    • Conv3: 128 filtros + BatchNorm + ReLU + MaxPool",
  "    • Conv4: 256 filtros + BatchNorm + ReLU + MaxPool",
  "    • FC: 512 → 256 → 29 clases",
  "    • Regularización: Dropout, BatchNormalization"
]);

// 6. Métricas Baseline
addTwoColumnSlide("Fase 2: Métricas Baseline (FP32)",
  [
    "📊 Complejidad Teórica:",
    "• Parámetros: 2.49 M",
    "• MACs: 63.25 M",
    "• Tamaño: 9.5 MB",
    "",
    "⚙️ Entrenamiento:",
    "• 25 épocas",
    "• Optimizador: Adam",
    "• Loss: CrossEntropyLoss"
  ],
  [
    "✅ Performance (CPU):",
    "• Val Accuracy: 79.32%",
    "• Test Accuracy: 79.09%",
    "• Val Loss: 0.9008",
    "",
    "⏱️ Inferencia:",
    "• Latencia: 4.98 ms",
    "• FPS: ~201",
    "• Peak Memory: ~350 MB"
  ]
);

// 7. Técnicas de Optimización
addContentSlide("Fase 3: Técnicas de Optimización", [
  "🔧 Cuantización: Conversión de FP32 → INT8/INT4",
  "    • Dinámica (dynamic quantization)",
  "    • Estática (static quantization)",
  "    • Quantization-Aware Training (QAT)",
  "",
  "✂️ Poda (Pruning): Eliminación de pesos no significativos (40%)",
  "",
  "📦 Factorización: Descomposición de convoluciones",
  "    • Separación en convoluciones depthwise + pointwise",
  "",
  "🎓 Destilación: Transfer de conocimiento (Teacher-Student)"
]);

// 8. Resultados Cuantización
addTwoColumnSlide("Fase 3: Resultados - Cuantización",
  [
    "INT8 Dinámica:",
    "• Accuracy: 79.15%",
    "• Tamaño: 3.51 MB (-63%)",
    "• Latencia: 4.85 ms",
    "",
    "INT8 Estática:",
    "• Accuracy: 79.22%",
    "• Tamaño: 2.38 MB (-75%)",
    "• Latencia: 3.92 ms"
  ],
  [
    "✅ Beneficios:",
    "• Reducción: 63-75%",
    "• Sin pérdida de accuracy",
    "• Compatible CPU",
    "",
    "⚡ Mejora de velocidad:",
    "• 20-27% más rápido",
    "• Menor consumo RAM"
  ]
);

// 9. Pruning
addContentSlide("Fase 3: Resultados - Pruning (40%)", [
  "✂️ Modelo Podado (FP32):",
  "    • Parámetros: 1.47 M (-41%)",
  "    • Tamaño: 5.6 MB (-41%)",
  "    • Accuracy: 78.95% (-0.14%)",
  "    • Latencia: 3.52 ms (-29%)",
  "",
  "✂️ Podado + INT8 Estático (Óptimo):",
  "    • Tamaño: 1.42 MB (-85%)",
  "    • Accuracy: 79.11% (preservado)",
  "    • Latencia: 2.15 ms (-57%)",
  "    • ✅ Cumple todas las restricciones"
]);

// 10. Distilación
addContentSlide("Fase 3: Resultados - Knowledge Distillation", [
  "🎓 Student Model (MLP comprimido):",
  "    • Parámetros: 315K (-87%)",
  "    • Tamaño: 1.21 MB (-87%)",
  "    • Accuracy: 77.45% (-1.64%)",
  "",
  "🎓 Student + INT8 Estático:",
  "    • Tamaño: 0.31 MB (-97%)",
  "    • Accuracy: 77.38% (dentro del límite)",
  "    • Latencia: 1.05 ms (-79%)",
  "    • 🚀 Máxima compresión alcanzada"
]);

// 11. Tabla Comparativa
addContentSlide("Fase 4: Comparativa de Modelos", [
  "Modelo                  Tamaño    Accuracy   Latencia",
  "Baseline FP32           9.5 MB    79.09%     4.98 ms",
  "INT8 Dinámico           3.51 MB   79.15%     4.85 ms",
  "INT8 Estático           2.38 MB   79.22%     3.92 ms",
  "Podado 40%              5.6 MB    78.95%     3.52 ms",
  "Podado + INT8 ⭐        1.42 MB   79.11%     2.15 ms",
  "Student INT8 🚀         0.31 MB   77.38%     1.05 ms"
]);

// 12. Análisis
addContentSlide("Fase 4: Análisis de Resultados", [
  "✅ Restricciones Cumplidas:",
  "    ✓ Tamaño ≤ 100 MB (alcanzado 0.31-1.42 MB)",
  "    ✓ Latencia < 50 ms (alcanzado 1.05-2.15 ms)",
  "    ✓ Drop de precision ≤ 2% (máximo 1.64%)",
  "",
  "📈 Logros Principales:",
  "    • Reducción de 85-97% en tamaño",
  "    • Mejora de 20-79% en velocidad",
  "    • Preservación de precisión del modelo"
]);

// 13. Conclusiones
let slide = prs.addSlide();
slide.background = { color: colors.darkBlue };

slide.addText("Conclusiones", {
  x: 0.5, y: 2, w: 9, h: 1,
  fontSize: 48, bold: true, color: colors.white,
  align: "center", fontFace: "Calibri"
});

let conclusions = [
  "✓ Compresión exitosa: 85-97% reducción de tamaño",
  "✓ Modelos optimizados viables para dispositivos embebidos",
  "✓ Combinación Pruning + Cuantización es óptima",
  "✓ Knowledge Distillation logra máxima compresión",
  "✓ Ciclo completo de optimización completado exitosamente"
];

let y = 3.2;
conclusions.forEach((item) => {
  slide.addText(item, {
    x: 1, y: y, w: 8, h: 0.45,
    fontSize: 18, color: colors.lightBlue,
    fontFace: "Calibri", valign: "top"
  });
  y += 0.55;
});

prs.writeFile({fileName: "TP_Integrador_Optimizacion_IA.pptx"});
console.log("✓ Presentación creada: TP_Integrador_Optimizacion_IA.pptx");
