# Trazabilidad: USA, MODIFICA y CREA

## USA: utilizar y comprender

Se ejecutó la **celda 0** del cuaderno original, con semilla 42 y su presupuesto original de 300 simulaciones por máscara. El registro completo está en `resultados/ejecucion_base.txt`; `resultados/diagnostico_base.json` conserva los parámetros y el hash del archivo original. No se afirma haber ejecutado todas las celdas del cuaderno original.

La partida base arrojó 91 y 135 puntos y reportó 390 observaciones de dados. Esa cantidad incluye dados conservados, por lo que no equivale al número real de dados nuevos. Se diagramó su flujo en `resultados/flujo_base.svg`.

Se mantienen nombres y conceptos reconocibles: `roll_single_die`, `roll_dice`, `has_sequence`, `score_hand`, `CATEGORIES_ORDER`, `PlayerState`, `GameStats`, `GameState`, `all_keep_masks`, `simulate_expected_value_after_keeps`, `choose_keep_mask_montecarlo`, `play_one_turn` y `play_game`. Sus firmas cambian para recibir parámetros y generadores explícitos.

## MODIFICA: correcciones y mejoras

| Evidencia en el original | Adaptación | Verificación |
|---|---|---|
| Se envía `rolls_remaining - 1` al evaluador; con una repetición disponible simula cero, todas las máscaras empatan y elige la primera (tirar todo). | Se evalúa la siguiente tirada si queda al menos una; se vuelve a decidir tras cada tirada real. | Cinco unos y solo Libre: la última repetición sí se considera. |
| `sims_per_mask=SIMS_PER_MASK` captura 300 al definir la función. Cambiar la variable global a 10, 1 000 o 100 000 no actualiza ese valor. | Parámetro explícito desde la consola y el cuaderno. | Diagnóstico original con global 10 y valor efectivo 300; comparación nueva en CSV. |
| Las estadísticas añaden toda la mano incluso cuando solo se lanzaron dos dados. | `roll_dice` devuelve solo caras nuevas. | Tres dados bloqueados producen dos observaciones, no cinco. |
| Mismo generador global para juego e hipótesis. | Instancias separadas para dados físicos y decisión Montecarlo. | La evaluación no cambia el estado del generador físico. |
| Solo suma las 13 casillas. | Se completan bono superior, bonos adicionales de Yahtzee y Joker. | Pruebas de umbral 63, bono 35, bono 100 y restricciones de Joker. |
| Referencia de convergencia = última estimación. | Enumeración exacta de los 216 resultados de tres dados libres. | Comparación independiente en pruebas. |
| El diagrama conecta un nodo inexistente `mejor_mask_decision`. | Diagrama sin nodo huérfano. | Revisión de flujo. |
| Definiciones duplicadas y ejecuciones automáticas al cargar. | Motor importable, consola y cuaderno separados. | Cuaderno ejecutado en orden. |

Se añade el escenario cargado: P(6)=0.30 y P(1)=...=P(5)=0.14. Las seis probabilidades suman 1. La partida principal sigue siendo uniforme.

## CREA: análisis nuevo

- Convergencia con prefijos de una misma secuencia, error absoluto y error estándar teórico.
- Comparación de Yahtzee en una sola tirada contra `sum(p**5)`, con intervalos de Wilson al 95 %.
- Escenario de decisión [6,6,6,1,2] con una tirada restante y solo Libre sin usar; todas las demás casillas están en cero, incluida Yahtzee, por lo que no hay bonos. Conservar 21 o arriesgar dos dados se compara contra la enumeración exacta de 36 resultados.
- Datos CSV/JSON, gráficos SVG, historial de 26 turnos y pruebas automatizadas.

## Limitaciones y atribución

El evaluador original conserva una máscara fija y sobrescribe los dados libres varias veces; su distribución final no aprovecha los éxitos intermedios. La adaptación hace explícito el horizonte de un paso y recalcula después de cada lanzamiento real. No implementa programación dinámica ni asegura una estrategia global óptima.

No se utiliza la diferencia entre los marcadores base y adaptado como prueba de superioridad: cambiaron reglas, política y consumo de azar. La Ley de los Grandes Números tampoco implica error decreciente en cada punto ni precisión universal del 99.9 %.
