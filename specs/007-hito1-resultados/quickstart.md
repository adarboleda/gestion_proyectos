# Quickstart: informe del Hito 1

Requiere el extra `modelo` (PyTorch) para entrenar las etapas. Desde la raíz, en este orden:

```
uv pip install --python .venv/Scripts/python.exe -e ".[dev,modelo]"
.venv/Scripts/entrenar-etapa1                                # 005 → modelos/etapa1/
.venv/Scripts/evaluar-regla-atws                             # 006 → resultados_regla_atws/
.venv/Scripts/medir-tiempo-deteccion                         # 008 → resultados_tiempo_deteccion/
.venv/Scripts/entrenar-etapa2                                # 009 → modelos/etapa2/
.venv/Scripts/evaluar-diagnostico --modelo modelos/etapa1    # 011 → resultados_evaluacion_diagnostico/
.venv/Scripts/informe-hito1                                  # 007 → informe_hito1/hito1.md y hito1.json
```

## Validaciones

1. Cada cifra de `hito1.md` coincide con su archivo de origen (lo comprueba `tests/hito1/integration/test_hito1_real.py`).
2. Ejecutar `informe-hito1` dos veces da el mismo `hito1.json`.
3. Si se borra un archivo de resultados, el comando termina con código 1 y nombra el comando que lo genera.

## Resultado con los datos reales (2026-11-04, esta máquina)

Los cinco comandos tardaron 4 min; `informe-hito1`, menos de 1 s. Copia: [hito1-2026-11-04.md](hito1-2026-11-04.md).

| Meta | Valor | Estado |
|---|---|---|
| Diagnóstico ≤ 10 s desde la falla (KAN-25, prueba) | 10 de 10 | cumple |
| ATWS ≤ 3 s desde la demanda (KAN-25, validación y prueba) | 6 de 6 | cumple |
| LOCA ≥ 50 cm² en ≤ 10 s (KAN-23, prueba) | 2 de 2 | cumple |
| 0 falsas alarmas en NORM (KAN-23, prueba) | 3 (R33, R36, R40) | no cumple |
| F1 de los primeros 30 s ≥ 0.80 (KAN-23) | 0.948 | cumple |
| Etapa 2 sin errores con confianza (KAN-24) | 0 errores, cobertura 0 % | cumple sin decisiones |
| Etapa 2: LOCA ≥ 50 cm² con su rama en ≤ 10 s (KAN-24) | 0 de 2 | no cumple |
| Regla sin falsas alarmas (KAN-22, validación y prueba) | 1 (R54) | no cumple |

Abstención de la Etapa 1 (KAN-26, prueba): **2.0 %** (IC 1.6–2.5 %); errores con confianza alta: 3.0 %; exactitud con abstención: 95.0 %.

## Pruebas

```
python -m pytest tests/hito1 -q
```
