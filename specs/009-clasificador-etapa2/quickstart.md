# Quickstart: Etapa 2

```powershell
uv pip install --python .venv\Scripts\python.exe -e ".[dev]"
uv pip install --python .venv\Scripts\python.exe torch --index-url https://download.pytorch.org/whl/cpu

.venv\Scripts\entrenar-etapa2.exe --origen "<IA-Nuclear>\PWR 3L" --salida modelos\etapa2

$env:IANUCLEAR_DATOS = "<IA-Nuclear>"
.venv\Scripts\python.exe -m pytest tests/etapa2 -q
```

Uso en cascada:

```python
from clasificador_etapa2.prediccion import cargar
etapa2 = cargar("modelos/etapa2")
etapa2.clasificar(serie_pwr_pwnt, familia_etapa1="LOCA")   # (T, 2) sin escalar desde t = 0
```

