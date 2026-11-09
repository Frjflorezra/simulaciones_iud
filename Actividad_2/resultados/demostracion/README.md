# Demostración de una secuencia

Ejecución del escenario base con 50 eventos sintéticos, semilla 2026, generador PCG64, Python 3.13.3 y NumPy 2.3.3. Los parámetros activos están incluidos en [resumen.json](resumen.json) y la trayectoria completa en [secuencia.csv](secuencia.csv).

| Métrica de esta secuencia | Valor |
|---|---:|
| Exactitud de Viterbi | 0.72 (36/50) |
| Exactitud del decodificador aislado | 0.70 (35/50) |
| Log-verosimilitud | −39.76947842822714 |
| Log-verosimilitud por evento | −0.7953895685645428 |

Estos valores describen una sola secuencia. No se presentan intervalos de confianza ni una conclusión de superioridad entre algoritmos a partir de esta demostración.

## Reproducción

Desde `Actividad_2`, utilizar una carpeta nueva:

```console
py main.py simular --eventos 50 --semilla 2026 --escenario base --salida resultados/reproduccion_demostracion
```

La ejecución se repitió en el mismo entorno y se compararon ambos archivos mediante SHA-256, con coincidencia exacta:

| Archivo | SHA-256 |
|---|---|
| secuencia.csv | 2d5a23852bf831f701ceef68249982e9007c4ea47c249d7b2ea49ec7992122a1 |
| resumen.json | 9703bd9079b505a1045fad5250c89a92b985c136d424455b55bc1c2b7e423210 |

El resumen registra el entorno. Cambiar versiones o plataforma puede cambiar ese archivo y no se garantiza un flujo idéntico universalmente. La procedencia de los datos es completamente sintética y los estados no son etiquetas geofísicas verificadas.
