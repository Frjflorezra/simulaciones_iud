# Planteamiento del estudio

## Problema

En un HMM, los estados latentes y las observaciones cumplen funciones distintas: los primeros describen regímenes supuestos del proceso y las segundas constituyen la información disponible para inferirlos. En este estudio se considera una secuencia sintética de categorías de magnitud cuyo régimen generador no es observable para el decodificador.

El problema consiste en evaluar cómo las probabilidades de transición, emisión e inicio afectan las secuencias generadas y la recuperación de sus estados ocultos. La simulación proporciona los estados generadores como referencia de evaluación; estos no se suministran al algoritmo de decodificación.

## Justificación del modelo

El HMM permite representar persistencia y cambios entre regímenes mediante una matriz de transición, y asociar cada régimen con distintas probabilidades de observación mediante una matriz de emisión. Una misma categoría de magnitud puede ser emitida por varios estados; observar una magnitud no identifica de manera unívoca el estado generador.

El catálogo sintético permite controlar los parámetros, conocer la secuencia latente de referencia y repetir los experimentos. Su utilidad se limita a evaluar el comportamiento del modelo bajo los supuestos establecidos. El contraste con literatura y la validación con catálogos reales constituyen tareas diferentes.

## Delimitación

La unidad secuencial es un evento: t identifica la posición en el catálogo, sin asignarle una duración física. Se modelan categorías de magnitud, sin generar magnitudes continuas, localizaciones, profundidades o tiempos entre eventos. No se representa una región geográfica ni un período histórico específico.

Los estados conservan las denominaciones Reposo Sísmico, Actividad Menor y Enjambre Sísmico como etiquetas didácticas. Operativamente se interpretan como regímenes de magnitud predominantemente baja, intermedia o elevada. «Reposo» no significa ausencia de eventos ni de peligro; la etiqueta «enjambre» no acredita una clasificación geofísica. No se realizan pronósticos de ocurrencia de terremotos.

## Objetivo general

Diseñar, implementar y evaluar un HMM categórico de tres estados que genere catálogos sísmicos sintéticos y permita analizar la sensibilidad de sus resultados a parámetros probabilísticos controlados.

## Objetivos específicos

1. Formalizar los estados, las observaciones y los parámetros del modelo, distinguiendo supuestos de evidencia empírica.
2. Comparar la decodificación y el comportamiento de las secuencias en escenarios controlados mediante réplicas, estadísticas descriptivas e intervalos de confianza.

## Preguntas de investigación

- **P1:** ¿Cómo representar una secuencia sintética de categorías de magnitud con un HMM de tres estados y qué límites tiene esa interpretación?
- **P2:** ¿Cómo cambia la recuperación de estados y la composición de las secuencias al modificar la matriz de transición o la de emisión por separado?
- **P3:** ¿Se reproducen las salidas con la misma configuración y semillas, y cómo cambia el comportamiento inicial al modificar la distribución de inicio?

## Contribución prevista

El estudio plantea una comparación reproducible de sensibilidad y decodificación con factores separados. La contribución frente a trabajos previos se delimitará mediante la revisión bibliográfica; no se presupone novedad ni superioridad del HMM sobre los métodos de comparación.
