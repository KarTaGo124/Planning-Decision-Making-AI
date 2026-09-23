# Feedback del profesor sobre el informe técnico

Extraído de las anotaciones (comentarios en PDF) que dejó el Mg. Robert Buleje sobre `docs/informe_tecnico.pdf`. El archivo original que comentó fue `buleje_informe_tecnico.pdf`, revisado el 22 de septiembre de 2026, sobre la versión del informe que Matías subió ese mismo día (commits `bd98fb5` y `b5e06df`). Verificado que el contenido base de esa versión es idéntico, carácter por carácter, al que está en `main` ahora mismo.

**Nota que mencionó el profesor:** *"Si tuviera que colocarles una nota, tendrían 3."* (comentario junto a la sección de Restricciones, página 1).

Cada punto trae entre paréntesis la página del PDF y la sección de nuestro informe a la que le queda más cerca, para ubicarlo rápido. Los que no tienen texto (algunas marcas a mano / círculos) no se listan porque no traen contenido que aplicar.

Marcar con `[x]` a medida que se van resolviendo.

---

## Portada / nombre del proyecto

- [ ] Uniformizar el nombre completo del sistema en todo el documento (ej. "Sistema Inteligente de Detección de Fraude..."). Sugiere además crear una sigla o acrónimo (ejemplo que dio: "SisFraud"), explicarlo una sola vez y usarlo de ahí en adelante en el resto del documento. *(pág. 1)*

## 1. Introducción y problema

- [ ] Antes de nombrar un modelo o solución directamente, expandir un poco más la idea de que el fraude cambia todo el tiempo y que eso obliga a replantear las estrategias continuamente ("no vayan de frente a decir un modelo"). *(pág. 1)*
- [ ] En la oración donde se justifica el dataset: quitar las palabras "drift mixto" y "alta dimensionalidad", y sacar todo lo que está entre paréntesis. Dice que así queda mejor. *(pág. 1)*

## 2. Objetivos

- [ ] Como sobran ~2 hojas del límite de 8, agregar subtítulos "General" y "Específicos" dentro de esta sección. *(pág. 1)*
- [ ] Aclaración positiva: el objetivo general le gusta tal como está. Confirma que, según el PDF del proyecto, **no es necesario desplegar en AWS/GCP** (es opcional), pero sí **exige una demostración en vivo funcionando**. Sugiere preparar ejemplos para la presentación. *(pág. 1)*
- [ ] Objetivo específico 1 (exploración temporal): complementarlo, ser más específico en qué patrones se busca encontrar (dice: "Analizar los datos en búsqueda de patrones .... y ....", sugiere desarrollarlo un poco más). *(pág. 1)*
- [ ] Objetivo específico 2 (modelado comparativo): falta esclarecer el esquema. Sugiere reescribirlo tipo: *"Comparar el rendimiento (especificando las métricas a utilizar) de un modelo clásico y dos avanzados (ajustar según cuántos modelos usaron) bajo un esquema de evaluación temporal."* *(pág. 1)*

## 3. Restricciones

- [ ] Pregunta abierta: ¿valdría la pena anonimizar los datos personales? Evaluar si aplica como restricción adicional o como aclaración. *(pág. 1)*

## 4. Diseño del sistema

- [ ] Falta describir explícitamente el módulo de monitoreo en esta sección (hay una nota "Sube esto al punto 4" con una flecha que apunta desde la Figura 1 / zona del monitor de drift hacia esta sección). *(pág. 1-2)*
- [ ] El umbral costo-óptimo se menciona pero no queda claro que se refiera a la métrica de decisión, conviene dejarlo explícito en vez de que se tenga que inferir ("me imagino que..."). *(pág. 1)*

## 5. Métricas de éxito

- [ ] Separar la latencia como punto aparte de F1/ROC-AUC (no mezclarlas en la misma viñeta), y aclarar cuál es el umbral mínimo aceptable para decir que el modelo "rinde bien" en este contexto. *(pág. 2)*
- [ ] Explicar mejor la métrica de costo de negocio: poner entre paréntesis qué significan FN y FP la primera vez que aparecen. Sugiere incluso renombrarla como "Ahorro por implementación del modelo", con un ejemplo concreto tipo: *"tomas los datos de 1 semana, si no hubiera modelo se habría perdido tanto dinero, pero con el sistema se perdió tanto, lo que equivale a un ahorro de N dólares (profit)."* *(pág. 2)*
- [ ] Antes de mostrar resultados (sección de Modelado), repetir brevemente cuáles son las métricas usadas y explicitar los periodos temporales con fechas/ejemplos concretos (ej. "se entrena con datos de tal fecha a tal fecha, se testea con los N datos siguientes"). *(pág. 2)*
- [ ] Comentario positivo (no requiere acción): "Lo bueno de su métrica social es que se puede cuantificar." *(pág. 2)*

## 7. Análisis y preparación de datos (EDA)

- [ ] Mejorar la legibilidad de la Figura 2 (volumen y tasa de fraude por semana). Sugiere buscar gráficas similares de referencia (papers/dashboards) y copiar el estilo. Como son 2 series de datos, evaluar si conviene juntarlas en un solo gráfico en vez de dos paneles separados. *(pág. 3)*
- [ ] Agregar una gráfica pequeña adicional que enmarque específicamente el hallazgo de que el fraude se dispara entre las 5am y las 9am. *(pág. 2)*
- [ ] Insiste en general: esta sección necesita **más gráficas**, no solo texto. Su frase textual: "en texto se pierden los hallazgos y se minimizan". Revisar si faltan visualizaciones para otros hallazgos del EDA (ProductCD, identity, etc.), no solo los que ya tienen figura. *(pág. 2)*

## 8. Modelado y evaluación

- [ ] Evaluar los modelos con ventana deslizante o múltiples periodos, no con un solo corte train/val. Su argumento: si usan un solo periodo, puede preguntar "¿si movemos el periodo de tal forma, seguiría ganando el modelo XX?". Cuanto más robusto el análisis, menos flancos para cuestionarlo en la presentación. *(pág. 3)*
- [ ] Señala una incoherencia: el texto menciona "precision" y "recall" en la interpretación de resultados, pero las métricas declaradas oficialmente son solo F1 y ROC-AUC. Decidir si se expande la lista de métricas declaradas o si se mantiene solo F1/ROC-AUC en el texto. Recuerda que había sugerido que **entre 3 y 5 métricas** es el número ideal. *(pág. 3)*
- [ ] Pregunta si no sería bueno comparar también la métrica social en esta sección de resultados (no solo mencionarla en la definición de métricas). *(pág. 3)*
- [ ] Mejorar la redacción de por qué XGBoost es "el mejor modelo": dice que no se entiende del todo el razonamiento tal como está escrito. *(pág. 3)*
- [ ] Sobre la Figura 3 (costo de negocio vs. umbral): sugiere considerar, como alternativa o complemento, una gráfica de promedio acumulado. *(pág. 3)*

## 10. Detección y adaptación al concept drift

- [ ] Mejorar la redacción del párrafo 2 de esta sección (el que empieza con "Se simularon 5 estrategias de reentrenamiento..."): dice que es un poco difícil de leer y entender. *(pág. 5)*
- [ ] Nota ya incorporada por el equipo antes de la revisión: aclarar que el umbral del 5% es una decisión de diseño propia, no un estándar de la literatura, y que su validación queda pendiente de experimentos temporales (falsas alarmas, costo de errores, costo de reentrenamiento). *(pág. 5, ya está en el `.tex` actual)*

## 11. Propuesta de despliegue

- [ ] Falta el gráfico de arquitectura de despliegue. Se pide explícitamente una arquitectura visual, no solo texto. Sugiere proponerla usando componentes de AWS o GCP (el que le resulte más cómodo al equipo). *(pág. 6)*

---

## Resumen de lo más urgente (para no perder puntos por lo básico)

1. **Falta la arquitectura de despliegue como diagrama** (sección 11): es un pedido explícito y hoy no existe ningún gráfico ahí.
2. **Incoherencia precision/recall vs. F1/ROC-AUC**: es fácil de arreglar y es exactamente el tipo de detalle que "resta puntos por descuido".
3. **Faltan más gráficas en el EDA** y mejorar legibilidad de las que ya hay. Lo repite dos veces, parece ser su observación más fuerte.
4. **Evaluar modelos con múltiples periodos/ventana deslizante**, no un solo corte. Pide robustecer el análisis para que no se lo puedan cuestionar en la presentación.
5. Redacción poco clara en 2 puntos puntuales: por qué XGBoost es el mejor modelo, y el párrafo 2 de la sección de drift.

El resto son mejoras de redacción, orden y presentación (subtítulos, acrónimo, aclarar paréntesis) que se pueden resolver rápido una vez que se ataquen los 5 puntos de arriba.
