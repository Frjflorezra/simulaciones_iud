# Guion individual para la sustentación

**Autor:** Francisco Javier Florez Ramirez  
**Docente asesor:** Dr. Julián Andrés Loaiza López  
**Duración objetivo:** 4 minutos y 30 segundos, con margen de ensayo hasta 5 minutos.  
**Apoyo visual:** presentacion.html, ocho diapositivas.

Los tiempos son una guía de ensayo; las diapositivas se avanzan manualmente. El texto de los parlamentos también está disponible en las notas de la presentación.

| Diapositiva | Tema | Intervalo | Duración |
| --- | --- | --- | ---: |
| 1 | Presentación del estudio | 0:00–0:20 | 20 s |
| 2 | Problema y pregunta | 0:20–1:00 | 40 s |
| 3 | Modelo y métodos | 1:00–1:35 | 35 s |
| 4 | Diseño experimental | 1:35–2:05 | 30 s |
| 5 | Trayectorias en el caso base | 2:05–2:45 | 40 s |
| 6 | Probabilidad de las trayectorias | 2:45–3:20 | 35 s |
| 7 | Evaluación Monte Carlo | 3:20–4:00 | 40 s |
| 8 | Conclusiones y límites | 4:00–4:30 | 30 s |

## 1. Presentación del estudio · 0:00–0:20

Cordial saludo. Mi nombre es Francisco Javier Florez Ramirez, estudiante de Ingeniería de Software y Datos de la IU Digital de Antioquia. Bajo la asesoría del doctor Julián Andrés Loaiza López, presento una comparación del algoritmo de Viterbi y dos clasificadores estáticos mediante una simulación inspirada en actividad sísmica.

**Apoyo visual:** Presentar el título y el alcance del trabajo; mirar a la cámara al iniciar.

## 2. Problema y pregunta · 0:20–1:00

El problema consiste en recuperar estados ocultos a partir de observaciones que pueden ser ambiguas. En nuestro caso, una magnitud media tiene la misma probabilidad de emisión en Actividad Menor y en Enjambre: cero coma cinco. Por eso, la magnitud de un solo evento no basta para distinguirlos mediante máxima emisión. La pregunta es cómo cambian las trayectorias y la precisión al comparar Viterbi, que utiliza la secuencia completa, con dos reglas que clasifican cada observación por separado. Trabajamos con datos sintéticos; estas etiquetas no representan estados sísmicos validados en campo.

**Apoyo visual:** Señalar el empate 0.50 frente a 0.50 y cerrar con la pregunta.

## 3. Modelo y métodos · 1:00–1:35

El modelo tiene tres estados: Reposo, Actividad Menor y Enjambre, y tres observaciones: magnitud Baja, Media y Alta. La matriz A describe las transiciones; B, las emisiones; y pi, la distribución inicial. Estos parámetros son hipotéticos y conocidos: no entrenamos el modelo. Comparamos tres métodos. Viterbi busca la trayectoria completa más probable. El primer baseline selecciona la máxima emisión y resuelve empates hacia Actividad Menor. El segundo pondera la emisión por el prior inicial fijo.

**Apoyo visual:** Explicar A, B y pi sin leer todas las celdas. Destacar la diferencia entre decodificar y entrenar.

## 4. Diseño experimental · 1:35–2:05

La evaluación tiene dos fases. Primero analizamos la secuencia Baja, Baja, Media, Media y Alta, comparando las trayectorias y su probabilidad conjunta. Después generamos cien secuencias de cincuenta eventos, con semilla cuarenta y dos y un protocolo de muestreo fijo. En cada réplica los tres métodos reciben las mismas observaciones. Los estados verdaderos se reservan para calcular la exactitud al final. La unidad de repetición es cada secuencia completa.

**Apoyo visual:** Recorrer las dos fases y señalar que las etiquetas verdaderas solo se usan al evaluar.

## 5. Trayectorias en el caso base · 2:05–2:45

En el caso de cinco eventos, Viterbi reconstruye Reposo, Reposo, Actividad Menor, Enjambre y Enjambre. El clasificador por máxima emisión elige Actividad Menor en las dos observaciones medias, aplicando la misma convención de desempate que usamos en Monte Carlo. El clasificador bayesiano asigna Reposo a todos los eventos por el peso del prior inicial. La celosía muestra que Viterbi conserva predecesores y reconstruye el camino mediante retroceso. No calcula la trayectoria eligiendo simplemente el estado con mayor valor local en cada instante.

**Apoyo visual:** Seguir el camino azul y comparar el cuarto evento entre Viterbi y máxima emisión.

## 6. Probabilidad de las trayectorias · 2:45–3:20

Las tres trayectorias se comparan bajo el mismo modelo. Viterbi obtiene una log-probabilidad conjunta de menos siete coma dos cinco tres ocho; máxima emisión, menos siete coma cuatro tres seis uno; y el bayesiano estático, menos ocho coma nueve cuatro cinco tres. Un valor mayor, es decir, menos negativo, indica mayor probabilidad conjunta. Este resultado verifica el objetivo de Viterbi. No equivale a demostrar mayor exactitud para esos cinco eventos, porque el caso ilustrativo no aporta estados verdaderos.

**Apoyo visual:** Señalar los puntos de izquierda a derecha. Distinguir probabilidad del camino y exactitud.

## 7. Evaluación Monte Carlo · 3:20–4:00

En Monte Carlo sí conocemos los estados generados y podemos medir aciertos. Viterbi alcanza una exactitud media del setenta y dos coma sesenta y dos por ciento; máxima emisión, sesenta y nueve coma setenta y dos; y el bayesiano, sesenta y uno coma cincuenta y cuatro. Las ventajas medias son de dos coma noventa y once coma cero ocho puntos porcentuales. Los intervalos reflejan la incertidumbre de las medias entre secuencias. Son intervalos aproximados del noventa y cinco por ciento; no presentamos un valor p ni una prueba de hipótesis pareada.

**Apoyo visual:** Mostrar las tres medias y sus intervalos. Decir «puntos porcentuales», no porcentaje relativo.

## 8. Conclusiones y límites · 4:00–4:30

Concluimos que, para esta configuración, Viterbi encuentra la trayectoria más probable y obtiene la mayor exactitud media entre los tres métodos. Esto no implica que siempre tenga menos variabilidad ni permite atribuir la diferencia únicamente a la matriz de transición. El experimento compara métodos completos. Los resultados se limitan a datos sintéticos y parámetros conocidos: no constituyen una herramienta de predicción de terremotos. El código y los datos exportados permiten reproducir la evaluación. Muchas gracias.

**Apoyo visual:** Cerrar mirando a la cámara. Evitar afirmar utilidad predictiva sobre sismos reales.

## Preparación de la grabación

- Ensayar una lectura completa y ajustar las pausas al tiempo disponible.
- Abrir presentacion.html en el navegador y activar pantalla completa. Las flechas permiten cambiar de diapositiva.
- Consultar las notas con N durante el ensayo; ocultarlas antes de grabar. G activa el modo de grabación sin controles en pantalla.
- El cronómetro es opcional, se inicia manualmente y no cambia las diapositivas. T inicia o pausa y R reinicia el tiempo.
- Pronunciar HMM como «modelo oculto de Markov», pi como «pi» e IC95 como «intervalo de confianza del noventa y cinco por ciento».
- No leer todas las celdas de las matrices; explicar qué representa cada una y señalar el empate.

## Cifras de consulta rápida

| Método | Secuencia del caso base | ln P | Exactitud Monte Carlo | IC95 % |
| --- | --- | ---: | ---: | --- |
| Viterbi | s1, s1, s2, s3, s3 | −7.2538 | 72.62 % | [70.48 %, 74.76 %] |
| Máxima emisión | s1, s1, s2, s2, s3 | −7.4361 | 69.72 % | [68.07 %, 71.37 %] |
| Bayesiano estático | s1, s1, s1, s1, s1 | −8.9453 | 61.54 % | [58.56 %, 64.52 %] |

El caso base no tiene estados verdaderos conocidos y se evalúa mediante probabilidad conjunta. La exactitud y sus intervalos corresponden exclusivamente a las cien secuencias Monte Carlo de cincuenta eventos. Los intervalos usan desviación muestral y una aproximación normal; no se calculó un valor p.

