# Material para la sustentación

Esta carpeta reúne el guion individual y la presentación para un video de aproximadamente 4 minutos y 30 segundos.

| Archivo | Uso |
| --- | --- |
| [presentacion.html](presentacion.html) | Ocho diapositivas con diagramas, resultados, notas del expositor y cronómetro de ensayo. |
| [guion.md](guion.md) | Parlamentos completos, tiempos, indicaciones visuales y cifras de consulta. |

## Cómo utilizar la presentación

1. Abrir `presentacion.html` con Chrome, Edge o Firefox. No requiere instalación, servidor ni conexión a internet.
2. Usar las flechas para avanzar o retroceder. Inicio y Fin llevan a la primera y última diapositiva.
3. Pulsar F o «Pantalla completa» para presentar.
4. Pulsar N o «Notas» para consultar el parlamento de la diapositiva durante el ensayo.
5. Antes de grabar, ocultar las notas y pulsar G para ocultar los controles. G o Esc permiten recuperarlos.
6. Si se desea medir el tiempo, T inicia o pausa el cronómetro y R lo reinicia. Las diapositivas no avanzan automáticamente.

La presentación no graba audio ni video. Compartir o capturar la ventana del navegador con la herramienta de grabación que se utilice.

## Contenido y datos

Las ocho diapositivas siguen los cuatro bloques del artículo: contexto y pregunta (0:00–1:00), modelo y experimento (1:00–2:05), resultados analíticos (2:05–3:20) y evaluación Monte Carlo y conclusiones (3:20–4:30).

Los datos de `../resultados/experimento.json` están incorporados en el HTML; las tablas y gráficos se dibujan a partir de esa copia. Así, el archivo se puede abrir o compartir por separado. No necesita las imágenes de `../figures/` ni carga recursos externos. Si se cambia el experimento, se debe actualizar la copia de datos y revisar el guion antes de volver a grabar.

Los resultados se limitan a simulación con parámetros conocidos. No se presenta una validación sismológica ni un valor p no calculado.
