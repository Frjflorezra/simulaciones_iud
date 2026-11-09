# Modelo y diseño experimental

## Componentes

Sea Z_t el estado oculto y O_t la observación del evento t. El modelo se especifica como λ = (S, V, A, B, π).

| Índice | Estado S | Interpretación operativa |
|---|---|---|
| 0 | Reposo Sísmico (R) | Régimen con predominio de categorías bajas |
| 1 | Actividad Menor (M) | Régimen con mayor probabilidad de categoría media |
| 2 | Enjambre Sísmico (E) | Régimen con mayor probabilidad de categoría alta que los otros dos estados |

Los nombres son etiquetas de simulación, no diagnósticos geofísicos.

| Índice | Observación V | Categoría |
|---|---|---|
| 0 | Magnitud baja | m < 3 |
| 1 | Magnitud media | 3 ≤ m ≤ 5 |
| 2 | Magnitud alta | m > 5 |

Se simulan categorías discretas; m define sus umbrales sin introducir una distribución continua o una escala instrumental específica.

### Distribución inicial

π_i = P(Z_1 = i), con π = [0.80, 0.15, 0.05].

### Matriz de transición

A_ij = P(Z_(t+1) = j | Z_t = i). Las filas representan el estado actual y las columnas el siguiente, en el orden R, M, E.

| A | R | M | E |
|---|---:|---:|---:|
| R | 0.85 | 0.12 | 0.03 |
| M | 0.30 | 0.50 | 0.20 |
| E | 0.10 | 0.30 | 0.60 |

### Matriz de emisión

B_ik = P(O_t = k | Z_t = i). Las filas representan estados y las columnas observaciones, en el orden baja, media, alta.

| B | Baja | Media | Alta |
|---|---:|---:|---:|
| R | 0.85 | 0.12 | 0.03 |
| M | 0.40 | 0.50 | 0.10 |
| E | 0.10 | 0.50 | 0.40 |

Los parámetros son hipotéticos y fijados, no estimados de un catálogo real. Los valores de π y de cada fila de A y B son no negativos y suman uno. La diagonal de A representa persistencia; el solapamiento entre filas de B permite que una observación sea compatible con varios estados.

## Supuestos y mecanismo generador

1. El estado siguiente depende únicamente del actual: P(Z_(t+1) | Z_1,…,Z_t) = P(Z_(t+1) | Z_t).
2. La observación depende únicamente del estado contemporáneo, bajo la estructura de independencia condicional del HMM.
3. A y B permanecen constantes dentro de cada escenario.
4. Z_1 se extrae de una distribución categórica con parámetros π; O_1 se extrae de la fila B correspondiente.
5. Para t > 1, Z_t se extrae de la fila de A correspondiente a Z_(t−1), y O_t de la fila de B correspondiente a Z_t.

La probabilidad conjunta es:

P(z_1:T, o_1:T) = π_(z_1) B_(z_1,o_1) ∏_(t=2)^T [A_(z_(t−1),z_t) B_(z_t,o_t)].

## Escenarios

Cada escenario contiene 200 réplicas de 500 eventos. Se modifica un solo componente respecto del caso base.

| Escenario | Parámetros | Factor evaluado |
|---|---|---|
| Base | A, B y π originales | Referencia |
| Mayor persistencia | A' = 0.5 A + 0.5 I; B y π originales | Persistencia de los estados |
| Emisiones menos informativas | B' = 0.7 B + 0.3 U; A y π originales | Solapamiento de las emisiones |
| Inicio diferente | π' = [0.05, 0.15, 0.80]; A y B originales | Sensibilidad a la condición inicial |

I es la identidad 3 × 3; U es una matriz 3 × 3 con entradas iguales a 1/3. Las combinaciones convexas conservan la normalización de las filas. El efecto de π se analizará tanto en los primeros 20 eventos como en la secuencia completa.

## Inferencia y comparación

Forward evaluará la probabilidad de las observaciones; Viterbi recuperará la trayectoria de estados de máxima probabilidad conjunta condicionada a la secuencia observada. La implementación utilizará escalamiento o logaritmos para evitar problemas numéricos.

Se comparará Viterbi con un decodificador que utilice cada observación de forma aislada y un prior explícito calculado sin estados de evaluación. No se presupone que Viterbi maximice la exactitud por evento: su criterio es la probabilidad de la trayectoria completa.

Los parámetros serán conocidos en generación y decodificación dentro de cada escenario. La evaluación corresponde a inferencia con modelo conocido; no incluye aprendizaje de parámetros. Baum-Welch se tratará en el marco teórico como algoritmo de aprendizaje.

## Métricas y análisis

- Exactitud de decodificación frente a los estados sintéticos generadores.
- Proporción de eventos en cada estado y categoría observable.
- Frecuencia de cambios de estado por transición disponible.
- Log-verosimilitud de las observaciones por evento.
- Métricas del período inicial para evaluar el cambio de π.

La unidad de réplica estadística es el catálogo completo. Para cada escenario y métrica se calcularán media, desviación estándar entre réplicas, mínimo, máximo e intervalo de confianza del 95%. No se tratarán los eventos dependientes de una secuencia como réplicas independientes.

Las comparaciones de log-verosimilitud entre escenarios tendrán en cuenta que el proceso generador también cambia. Las diferencias entre algoritmos se evaluarán sobre las mismas secuencias. El procedimiento exacto de intervalos, la semilla raíz y el esquema de emparejamiento se especificarán antes de ejecutar los experimentos finales.

## Reproducibilidad y validación

Se conservarán parámetros, semillas por réplica, versiones de dependencias, secuencias y métricas crudas. Las réplicas tendrán flujos aleatorios distintos derivados de una semilla raíz; repetir la misma configuración y entorno deberá reproducir las salidas.

La validación computacional incluirá revisión de probabilidades, casos pequeños verificables para Forward y Viterbi y repetición de una ejecución con comparación de resultados. La validación con datos geofísicos reales queda fuera de este diseño.

## Estado experimental

Este documento especifica el diseño; no presenta simulaciones ejecutadas, cifras de desempeño ni conclusiones experimentales.
