# Data Model: Asistente EOP y explicabilidad

## Entidades

### EOPDefinition (`EOP_DEFINITIONS`)
| Código | Nombre |
|---|---|
| E-0 | Reactor Trip or Safety Injection |
| E-1 | Loss of Reactor or Secondary Coolant |
| ES-1.2 | Post-LOCA Cooldown and Depressurization |
| FR-S.1 | Response to Loss of Subcriticality / Emergency Boration |
| ES-0.1 | Estabilización posterior al disparo (canal rápido) |

### Árbol de decisión (`EOP_TREE`)
| Diagnóstico | Procedimientos |
|---|---|
| LOCA / LOCAC | E-0 → E-1 → ES-1.2 (con rama estimada en canal rápido) |
| ATWS | FR-S.1 |
| TRANS | E-0 (acción primaria: vigilar el disparo solicitado y verificar la respuesta del reactor) |
| TRIP_OK | E-0 → ES-0.1 |
| NORM | ninguno (vigilancia) |
| UNCERTAIN | ninguno (monitoreo; validar con el operador) |

### EOPResult
| Campo | Regla |
|---|---|
| predicted_class | clase final (incluye UNCERTAIN) |
| confidence | [0, 1]; < 0.80 → UNCERTAIN (`UNCERTAINTY_THRESHOLD = 0.80`) |
| eops | lista de procedimientos del árbol |
| guidance | texto consultivo (puede anteponer rama o motivo de novedad) |
| thermal_alerts | DNBR < 2.5 (escala PCTRAN) y PCT > 900 °C; informativas |
| atws_thermal_caveat | `true` para ATWS: reemplaza el valor numérico por advertencia |

### ExplicacionSHAP
| Campo | Regla |
|---|---|
| method | `GradientExplainer` o `occlusion_fallback` |
| shap | forma (150, F, clases); se agrega `|SHAP|` sobre el tiempo |
| ranking | variables ordenadas por importancia |
| narrative | frase con valor inicial y extremo desnormalizados; "se mantuvo estable" si |Δz| < 0.05 |

### Contrafactual
| Campo | Regla |
|---|---|
| clase_objetivo | segunda clase más probable |
| variables | 1 o 2 variables top-SHAP |
| porcentaje | paso de 10 % de interpolación hacia el perfil medio de train |
| resultado | encontrado o "no encontrado" (límite del método) |

### PorQue (canal rápido)
| Diagnóstico | Campos mostrados |
|---|---|
| ATWS | demanda de disparo y señal; PWNT a +x s frente al retardo del scram; margen 1.5 s |
| LOCA / LOCAC | presión con el umbral automático cruzado; LVCR; LVPZ; presión de contención |
| UNCERTAIN (novedad) | motivo y valor anormal (RM2/RM3/RM4, PSGA/PSGB, PORV, presión de contención) |
| TRIP_OK | demanda de disparo y caída de PWNT |

### MuestraRepresentativa
8 muestras: test #0 ATWS, #3–#6 casos límite, #7 LOCA y #8 LOCAC correctos con ≥ 80 % de confianza, y la NORM de validación (val #2).

### Consola
Datos JSON embebidos (`__SAMPLES_JSON__`), clave de idioma `idss_lang`, enlaces `#vivo:R13`, `#R49`, `#mejora`, `#fases`; reproducción causal por prefijos `[0, t)`.

## Reglas de validación

- Todo LOCA/LOCAC trae exactamente `["E-0", "E-1", "ES-1.2"]`; todo ATWS trae `["FR-S.1"]` con `atws_thermal_caveat = true`.
- `method` de cada explicación declara el método realmente usado.
- La consola no ejecuta modelos; cambiar de pestaña no dispara cálculo de IA.
- Los umbrales automáticos mostrados provienen de la guía de umbrales (132.2, 118.1, 43.27, 11.36, 1.30 bar).
