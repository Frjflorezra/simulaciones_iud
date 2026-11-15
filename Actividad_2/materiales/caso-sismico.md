# Caso didáctico: niveles de actividad sísmica

Una estación de monitoreo registra, en orden temporal, las magnitudes de eventos sísmicos de una región. Se busca explorar si un modelo oculto de Markov (HMM) permite inferir una secuencia de estados supuestos: Reposo Sísmico, Actividad Menor y Enjambre Sísmico. No se aporta un catálogo real de sismos. Estos estados son etiquetas hipotéticas de la simulación; su interpretación sismológica no está validada.

Observaciones ilustrativas: Magnitud Baja, Magnitud Baja, Magnitud Media, Magnitud Media, Magnitud Alta. Se considera baja una magnitud menor a 3, media una magnitud entre 3 y 5, incluidos ambos límites, y alta una magnitud mayor a 5. Esta secuencia es un ejemplo, no un registro real.

Parámetros hipotéticos para una simulación (no estimados de datos sísmicos):
A = [[0.85, 0.12, 0.03], [0.30, 0.50, 0.20], [0.10, 0.30, 0.60]]
B = [[0.85, 0.12, 0.03], [0.40, 0.50, 0.10], [0.10, 0.50, 0.40]]
pi = [0.80, 0.15, 0.05]

A: matriz de transición; filas (estado actual) y columnas (estado siguiente) en el orden Reposo Sísmico, Actividad Menor, Enjambre Sísmico. B: matriz de emisión; filas en ese mismo orden de estados y columnas Magnitud Baja, Magnitud Media, Magnitud Alta. pi: distribución inicial en el mismo orden de estados.

Tareas: formular pregunta, justificar HMM, proponer método sencillo de comparación, datos, métrica y experimento controlado. Distinguir decodificación con parámetros conocidos de entrenamiento. No inventar hallazgos, fuentes ni cifras.
