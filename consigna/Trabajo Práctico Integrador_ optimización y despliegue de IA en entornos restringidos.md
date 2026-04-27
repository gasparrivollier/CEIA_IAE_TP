# Trabajo práctico integrador: optimización y despliegue de IA en entornos restringidos

# Consigna general

El objetivo de este trabajo es seleccionar un problema a resolver mediante Deep Learning y ejecutar el ciclo de vida completo del modelo, enfocándose críticamente en la adaptación de la red neuronal para que opere eficientemente bajo las restricciones de hardware de una plataforma de despliegue específica.

El proyecto deberá desarrollarse siguiendo estas cuatro fases obligatorias:

## Fase 1: definición del problema y restricciones

Antes de escribir código, se debe establecer el marco de trabajo y las limitaciones del proyecto.

* Selección del problema: definir el caso de uso (por ejemplo clasificación de imágenes, detección de anomalías, análisis de audio) y el dataset a utilizar.  
* Plataforma de despliegue objetivo: definir dónde correrá el modelo en la Fase 4\. Puede ser hardware embebido real (Raspberry Pi, microcontrolador), un emulador, o bien una PC estándar forzando restricciones concretas (por ejemplo uso exclusivo de CPU).  
* Definición de restricciones: establecer los criterios de aceptación del proyecto.  
  * Máxima pérdida de precisión admitida (accuracy drop): por ejemplo "no perder más del 2% respecto al modelo base".  
  * Restricciones físicas: límite máximo de tamaño del modelo en memoria/disco, o latencia máxima admitida / mínimos FPS requeridos en la plataforma objetivo.

## Fase 2: arquitectura y entrenamiento inicial (baseline)

Desarrollo del modelo original sin optimizaciones, que servirá como punto de comparación.

* Diseño de Arquitectura: seleccionar o diseñar una red neuronal (CNN, MLP, RNN, etc.).  
  * Opcional: en esta etapa se fomenta el uso de técnicas de Neural Architecture Search (NAS) para hallar una topología inicial que tenga en cuenta las restricciones de la plataforma de forma automatizada.  
* Entrenamiento: entrenar el modelo base utilizando aceleración por hardware (GPU local o Google Colab).  
* Métricas Base: exportar el modelo original (típicamente en FP32) y registrar rigurosamente su tamaño en memoria, complejidad teórica (parámetros/MACs) y precisión inicial (Accuracy/Loss).

## Fase 3: optimización del modelo

En esta etapa se debe modificar la red para que cumpla (o supere) los requisitos pautados en la Fase 1\.

* Aplicación de técnicas de compresión: implementar scripts que tomen el modelo base y le apliquen una o más de las metodologías vistas en clase. Algunas opciones incluyen:  
  * Poda (Pruning): estructurada (canales/filtros) o no estructurada.  
  * Cuantización: Post-Training Quantization (PTQ), Quantization-Aware Training (QAT) o esquemas de precisión mixta (por ejemplo INT8, INT4).  
  * Factorización de tensores.  
  * Destilación del conocimiento (Knowledge Distillation): usar el modelo base como "profesor" para entrenar un "alumno" más pequeño.  
* Exportación optimizada: guardar el nuevo modelo comprimido y documentar los parámetros de la técnica elegida.

## Fase 4: despliegue y benchmarking

Llevar la teoría a la práctica midiendo el rendimiento real sobre el hardware.

* Despliegue: trasladar ambos modelos (el baseline y el optimizado) a la plataforma definida en la Fase 1\.  
* Evaluación empírica: desarrollar un script de validación que ejecute al menos 100 iteraciones de inferencia para ambos modelos y mida comparativamente:  
  * Consumo de memoria: tamaño en disco de los archivos finales y estimación de memoria RAM (Peak Memory) durante la inferencia.  
  * Velocidad de inferencia: tiempo promedio por predicción (en milisegundos) y su equivalente en FPS (Frames/Inferences Per Second) reales en el hardware.  
  * Retención de precisión: evaluar el conjunto de datos de prueba en ambos modelos desplegados y verificar que la caída de precisión respete el límite establecido en la Fase 1\.

---

# Anexo: ejemplos de posibles temas

Para guiar el alcance del trabajo, aquí hay algunas ideas válidas para el proyecto:

1. Poda estructurada en redes de visión computacional: seleccionar una arquitectura conocida (por ejemplo VGG, ResNet, MobileNet) y aplicar un algoritmo de poda estructurada que logre una mejora medible en el tiempo de ejecución en CPU sin pérdida significativa de rendimiento (menor al 2%). Tener en cuenta el soporte de HW para raleo 2:4 si se usa GPU Ampere/Hopper.  
2. Cuantización de precisión mixta extrema: seleccionar una CNN (por ejemplo VGG, ResNet, MobileNet) y aplicar cuantización con aritmética mixta para reducir los pesos a 4 bits (o menos) manteniendo las activaciones en 8 bits (o 4 bits), verificando empíricamente la reducción de RAM. La pérdida de precisión debe ser menor al 2%.  
3. Knowledge Distillation para sensores IoT: entrenar una red pesada para clasificar un dataset complejo y utilizarla como "profesor" para destilar su conocimiento hacia un Perceptrón Multicapa (MLP) muy simple o una CNN ultraligera capaz de correr en restricciones de microcontrolador.  
4. Hardware-Aware NAS aplicado a clasificación de audio: utilizar técnicas de búsqueda de arquitectura para encontrar el modelo más ligero posible (minimizando MACs) capaz de clasificar palabras clave de audio con un Accuracy preestablecido, para luego desplegarlo.

Recuerden que pueden proponer otros temas para desarrollar en el TPI. Los temas propuestos deben ser validados por los docentes.