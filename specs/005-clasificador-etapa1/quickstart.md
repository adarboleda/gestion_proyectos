# Quickstart: Clasificador de Etapa 1

Contratos en [contracts/cli.md](contracts/cli.md) y [contracts/salidas.md](contracts/salidas.md).

## Requisitos

- Entorno del proyecto con el extra del modelo:

```powershell
uv pip install --python .venv\Scripts\python.exe -e ".[dev]"
uv pip install --python .venv\Scripts\python.exe torch --index-url https://download.pytorch.org/whl/cpu
```

- Carpeta PWR 3L de IA-Nuclear (en esta máquina: `D:\Personal\IANuclear\PWR 3L`).

## Entrenar y evaluar

```powershell
.venv\Scripts\entrenar-etapa1.exe --origen "D:\Personal\IANuclear\PWR 3L" --salida modelos\etapa1
```

Termina con código 0, imprime el reporte y deja `modelo.pt`, `modelo.json`, `reporte.json` y `reporte.txt` en `modelos\etapa1`.

## Validaciones

1. **Sin fuga**: `modelo.json["corridas"]` tiene 63 / 15 / 13 corridas y ninguna repetida; el comando ejecutó `verificar_reparto` (si hubiera fuga terminaría con código 1).
2. **Pesos de clase**: `modelo.json["pesos_clase"]` tiene 3 valores, mayores para las familias menos frecuentes.
3. **Reproducibilidad**: repetir el comando con la misma semilla en otra carpeta da `reporte.json` idéntico.
4. **Reporte**: hay una entrada de detección por cada corrida de evento de prueba, la tabla de horizontes 1–30 s y el conteo de falsas alarmas.
5. **Metas**: `reporte.json["metas"]` indica si se cumplen SC-001, SC-002 y SC-003; se informa el resultado tal como sale.
6. **Clasificación**: `cargar("modelos/etapa1").clasificar(serie)` devuelve tres probabilidades que suman 1, una recomendación o «INCIERTO» y el aviso consultivo.
7. **Tiempo**: entrenar y evaluar termina en menos de 15 minutos (SC-006).

## Pruebas automáticas

```powershell
$env:IANUCLEAR_DATOS = "D:\Personal\IANuclear"
.venv\Scripts\python.exe -m pytest tests/etapa1 -q
```

## Resultados obtenidos

Se anotan aquí al ejecutar la validación con los datos reales.
