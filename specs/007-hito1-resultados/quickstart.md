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

## Pruebas

```
python -m pytest tests/hito1 -q
```
