# Quickstart: Verificación de la Documentación del Dataset (Fase 1)

Guía rápida para verificar que la documentación y los metadatos de la Fase 1 están completos y cumplen con las especificaciones.

---

## 1. Verificación de Archivos y Metadatos con Python

```python
import json
from pathlib import Path

# 1. Verificar metadata.json
meta_path = Path("data_processed/metadata.json")
assert meta_path.exists(), "metadata.json no encontrado"
meta = json.loads(meta_path.read_text(encoding="utf-8"))

assert len(meta["selected_features"]) == 12
assert len(meta["margin_features"]) == 7
assert meta["class_mapping"]["NORM"] == 0
assert meta["time_step_seconds"] == 10
assert meta["sequence_length"] == 150
assert len(meta["known_limitations"]) >= 4

# 2. Verificar README_FASE1.md
readme_path = Path("docs/README_FASE1.md")
assert readme_path.exists(), "README_FASE1.md no encontrado"
texto = readme_path.read_text(encoding="utf-8")
assert "PCTRAN" in texto
assert "Tsinghua" in texto
assert "PWR" in texto
assert "DNBR" in texto
assert "StandardScaler" in texto
print("Verificación de documentación completada con éxito.")
```

---

## 2. Ejecutar la Suite de Pruebas Automatizadas

```bash
.venv\Scripts\python.exe -m pytest tests/documentacion -v
```
