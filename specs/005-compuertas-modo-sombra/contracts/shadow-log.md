# Contrato: log de modo sombra (`shadow_log_*.jsonl`)

Un archivo por canal y ejecución. Una línea JSON por decisión, solo se añade (no se reescribe).

## Registro

```json
{
  "run_id": "R49",
  "canal": "rapido",
  "planta": "PWR3L",
  "t": 38.0,
  "entradas_resumen": {"PWNT": 97.2, "P": 148.1, "RPS_DEMAND": 1},
  "diagnostico": "ATWS",
  "confianza": 0.99,
  "compuertas": ["ATWS"],
  "rechazo": null,
  "eop": ["FR-S.1"],
  "motivo": "Demanda de disparo a +1.0 s; PWNT sigue en 97 % tras el retardo del scram + 1.5 s",
  "referencia": "FR-S.1",
  "referencia_fuente": "automatica",
  "acuerdo": true,
  "advisory_only": true
}
```

## Reglas

- `canal` ∈ {`rapido`, `lento`, `fusion`}; `planta` ∈ {`PWR3L`, `NPPAD`}.
- `rechazo`, si existe: `{"motivo": "confianza_baja|deriva_kl|novedad", "valor": <número>, "respaldo": "setpoints_planta", "t_conmutacion": <s>}`.
- `referencia_fuente` ∈ {`automatica`, `revision_ciega`}; la revisión ciega solo existe para la muestra de ~10 corridas.
- `acuerdo` es `null` si aún no hay referencia para esa corrida.
- `advisory_only` siempre `true`.
- Una línea por instante de decisión: 1 s en PWR 3L, 10 s en NPPAD.

## Resumen (`shadow_summary.json`)

```json
{
  "corridas": 106,
  "registros": 31800,
  "acuerdo_por_clase": {"LOCA": 0.0, "LOCAC": 0.0, "ATWS": 0.0, "TRIP_OK": 0.0, "NORM": 0.0},
  "fraccion_incierto": 0.0,
  "rechazos": {"confianza_baja": 0, "deriva_kl": 0, "novedad": 0},
  "t_conmutacion_max": 0.0,
  "cobertura_log": 1.0
}
```

Los valores son un ejemplo de forma; se llenan al ejecutar el modo sombra.
