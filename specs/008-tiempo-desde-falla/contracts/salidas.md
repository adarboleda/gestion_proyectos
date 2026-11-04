# Contrato: resultados de `medir-tiempo-deteccion`

| Archivo | Contenido |
|---|---|
| `tiempos.json` | `aviso`, `configuracion` (semilla, umbral, confirmación, metas, tolerancia), `corridas` (un `ResultadoCorrida` por corrida de validación y prueba), `resumen`, `metas`, `falsas_alarmas`, `confusiones`, `inciertas` e `instantes` (instante de la falla de las 72 corridas de evento de los tres conjuntos, con su fuente; SC-001) (data-model.md) |
| `tiempos.csv` | Una fila por corrida evaluada: `corrida, conjunto, clase, familia, area, t_falla, fuente_falla, incierta, inicio_validador, diferencia_validador_s, t_confirmacion, primera_familia, tiempo_diagnostico_s, tiempo_desde_validador_s, atws_recomendacion, atws_motivo, t_demanda, tiempo_atws_demanda_s, tiempo_atws_falla_s, falsas_alarmas_etapa1` |
| `lineas_tiempo.csv` | Una fila por corrida y segundo: `corrida, conjunto, tau, p_norm, p_loca, p_trans, confirmada, decision_atws` (`decision_atws` solo en el segundo de decisión de la regla) |
| `reporte.txt` | Reporte legible; es lo que imprime el comando |

Los dos CSV empiezan con una línea de comentario `# <aviso consultivo>` (se lee con `comment="#"`). Los cuatro se publican juntos; otros archivos de la carpeta no se tocan. Se regeneran con el comando; no se editan a mano.

## Invariantes

- Cada corrida de evento de validación y prueba aparece una vez en `tiempos.csv`.
- `tiempo_diagnostico_s` = `t_confirmacion − t_falla` cuando ambos existen.
- `lineas_tiempo.csv` tiene 295 filas por corrida (τ = 5…299).
- Las corridas inciertas no cuentan en la meta de diagnóstico; sí en la de ATWS (desde la demanda).
