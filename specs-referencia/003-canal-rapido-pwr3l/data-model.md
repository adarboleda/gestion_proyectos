# Data Model: Canal rápido de detección a 1 s con PWR 3L

## Entidades

### CorridaPWR3L (`manifest` implícito en `plan_corridas_pwr3l.csv` + `data_processed_pwr3l/metadata.json`)
| Campo | Regla |
|---|---|
| run_id | R01…R108 |
| clase | NORM, LOCA, LOCAC, ATWS, TRIP_OK, OOD |
| subtipo / área | tamaño de rotura 2–8500 cm² (LOCA); iniciador (ATWS/TRIP_OK) |
| ic_origen | solo 1, 2 o 3 (100 % EOC/MOC/BOC) |
| fallas | `numero:fraccion:retardo[:rampa]` separadas por `;` |
| t_inicio_real | calculado de los datos (no del Excel); diferencia > 2 s con el plan se marca |
| t_disparo_requerido, retardo_scram, senal_requerida | señal propia o la del gemelo si son idénticas hasta ese instante |
| gemelo_de | pareja ATWS ↔ TRIP_OK |
| estado | usar / repetir / descartar / fuera de distribución |
| duración / muestreo | 300 s a 1 s |

Conjunto: 106 corridas = 20 NORM + 20 LOCA + 20 LOCAC + 20 ATWS + 20 TRIP_OK + 6 OOD (R20, R64, R65, R66, R107, R108).

### SecuenciaRelativa
| Campo | Regla |
|---|---|
| x_rel(t) | `(x(t) − x_base) / escala_física`; `x_base` = promedio en `[0, min(15, t_inicio − 2)]` s; `escala` = rango típico del instrumento |
| entradas | 26 variables medibles + `RPS_DEMAND` + picos enclavados de PWNT y PWR |
| cambios | valor relativo y variaciones en 1, 3 y 10 s |
| ruido | σ por instrumento (ver FR-011) |

### Etiqueta por ventana (ATWS y TRIP_OK)
| Tramo | Etiqueta |
|---|---|
| antes del evento | NORM |
| del evento al disparo requerido | TRANS |
| después del disparo requerido | ATWS o TRIP_OK |

### Deteccion (salida por segundo)
| Campo | Valores |
|---|---|
| diagnosis | NORM, TRANS, TRIP_OK, ATWS, LOCA, UNCERTAIN |
| confidence | [0, 1]; confirmación con k = 2 s y ≥ 0.80 |
| early_alarm | bool |
| atws_gate | bool: demanda de disparo + retardo del scram + 1.5 s + PWNT > 20 % |
| novelty / novelty_reason | monitor físico y valor anormal |
| branch | caliente / fría / sin decidir (solo si LOCA) |
| eop | procedimiento recomendado (feature 004) |

### MonitorDeNovedad
| Monitor | Regla |
|---|---|
| radiación fuera de contención | RM2, RM3 o RM4 sobre 1.5 × envolvente de lo conocido |
| asimetría de GV | diferencia de presión entre PSGA y PSGB |
| PORV | abierta con presión baja |
| contención | presión sube sin aumento de radiación |

### ResultadoDeAceptacion (`pwr3l_output/acceptance/acceptance.json`)
`criterios` (por clase, por tamaño, por iniciador) y `veredictos` (9 metas, cada una con `ok` = true / false / "parcial" y `valor`).

## Reglas de validación

- Un grupo de validación cruzada nunca separa un ATWS de su gemelo.
- Las 6 corridas OOD nunca entran a entrenamiento.
- Las corridas con IC 4, 5, 6, 22 y 23 no se usan.
- La salida de cada falla se verifica con `--probar-fallas`: #13 y #14 no tienen efecto; #9 ignora el retardo; #12 con magnitud 30 cae la demo.
- Escaladores solo con corridas de entrenamiento.
