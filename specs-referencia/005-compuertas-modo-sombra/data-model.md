# Data Model: Compuertas deterministas, rechazo de la IA y modo sombra

## Entidades

### Compuerta
| Campo | Regla |
|---|---|
| id | `ATWS`, `DNBR`, `PCT` |
| estado | `inactiva` → `posible` → `confirmada` (solo ATWS tiene "posible") |
| condición | ATWS: demanda de disparo + retardo del scram + 1.5 s + PWNT > 20 %; DNBR: caída porcentual (configurable) respecto al DNBR nominal de la IC, solo si el reactor no ha disparado y la estimación es fiable; PCT: límite configurable (valor y escala pendientes de la experta) |
| instrucción | texto consultivo (p. ej. FR-S.1 o alerta de disparo) |
| prioridad | siempre mayor que la salida del clasificador |

### EventoDeRechazo
| Campo | Regla |
|---|---|
| t | instante de simulación (s) |
| motivo | `confianza_baja` (< 0.80), `deriva_kl` (> 0.1), `novedad` (monitor físico) |
| valor | confianza, KL medido o valor anormal |
| respaldo | `ninguno` o `setpoints_planta` (setpoints automáticos de la guía + mapeo a E-0 + compuerta ATWS + monitores de novedad) |
| t_conmutacion | segundos hasta activar el respaldo; debe ser < 1 |

### EstadoDeFusion
| Entrada | Regla |
|---|---|
| clase del canal rápido (+ confianza) | alarma temprana inmediata |
| clase del canal lento (+ confianza) | confirma si coincide; INCIERTO si discrepa; ausente → no bloquea |
| compuertas | prevalecen sobre ambos canales |
| orden de prioridad | novedad → compuerta → desacuerdo → clase confirmada |

### RegistroDeSombra (contrato en `contracts/shadow-log.md`)
| Campo | Tipo |
|---|---|
| run_id, canal, planta | texto |
| t | número (s) |
| entradas_resumen | objeto (variables clave en ese instante) |
| diagnostico, confianza | texto / número |
| compuertas | lista de ids activos |
| rechazo | objeto o null |
| eop | lista |
| motivo | texto ("Por qué") |
| referencia, referencia_fuente, acuerdo | texto / `automatica` o `revision_ciega` / booleano |
| advisory_only | siempre `true` |

### ReferenciaDeExpertos
Mapa `clase real del escenario → procedimiento esperado`, con dos fuentes: la guía de umbrales de la experta (automática, incluye los tiempos de referencia de R03, R09 y R28) y la anotación ciega de unas 10 corridas por la experta.

### ResumenDeSombra
Tasa de acuerdo por clase, matriz diagnóstico-referencia, fracción INCIERTO, tiempos de rechazo y cobertura del log.

## Relaciones y transiciones

- Cada decisión de la fusión produce exactamente un `RegistroDeSombra`.
- Un `EventoDeRechazo` cambia el estado de respaldo de `ninguno` a `activo` hasta que el motivo desaparezca durante k instantes consecutivos.
- Compuerta `posible` → `confirmada` (ATWS) o vuelve a `inactiva` si llega el scram.

## Reglas de validación

- `advisory_only` es verdadero en el 100 % de los registros.
- `t_conmutacion` < 1 s en el 100 % de los rechazos.
- Ningún registro usa información posterior a su `t`.
- La lógica de compuertas no importa módulos de modelos.
