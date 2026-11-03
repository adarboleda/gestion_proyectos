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

Ejecutado el 2026-11-03 con `D:\Personal\IANuclear\PWR 3L`, semilla 42, PyTorch 2.15.0 (CPU, 8 hilos).

1. **Sin fuga**: 63 / 15 / 13 corridas, ninguna repetida; `verificar_reparto` sin violaciones. ✔
2. **Pesos de clase**: NORM 0,520 · LOCA 1,857 · TRANS 1,857 (8 449 muestras de entrenamiento). ✔
3. **Reproducibilidad**: una segunda ejecución en otra carpeta dio `reporte.json`, `modelo.json` y `modelo.pt` idénticos. ✔
4. **Reporte**: 10 detecciones (una por corrida de evento de prueba), horizontes 1–30 s y falsas alarmas. ✔
5. **Metas** (se informan tal como salen):

| Meta | Resultado | Estado |
|---|---|---|
| SC-001: LOCA ≥ 50 cm² confirmada en ≤ 10 s | 0 de 2 (R44 y R83, 100 cm²: 19 s) | **No cumple** |
| SC-002: 0 falsas alarmas en corridas NORM | 0 (y 0 en los tramos previos) | Cumple |
| SC-003: F1 macro de los primeros 30 s ≥ 0,80 | 0,927 | Cumple |

6. **Clasificación**: `cargar("modelos/etapa1").clasificar(serie)` devuelve probabilidades que suman 1, recomendación o «INCIERTO» y el aviso. ✔ (pruebas)
7. **Tiempo**: 16,7 s para cargar las 109 corridas, entrenar (8 épocas; mejor la 2.ª) y evaluar. ✔

**Métricas globales en prueba** (3 835 muestras): F1 macro 0,978; NORM F1 0,978, LOCA 0,971, TRANS 0,986. Matriz de confusión: NORM [1193, 0, 0], LOCA [46, 1253, 0], TRANS [7, 30, 1306].

**Por horizonte** (exhaustividad en k = h):

| h | 1 s | 2 s | 3 s | 5 s | 10 s | 20 s | 30 s |
|---|---|---|---|---|---|---|---|
| LOCA | 0,00 | 0,00 | 0,00 | 0,00 | 0,80 | 1,00 | 1,00 |
| TRANS | 0,50 | 0,80 | 1,00 | 1,00 | 1,00 | 1,00 | 1,00 |

**Tiempo de confirmación**: TRANS 5 de 5 en 2–4 s (mediana 3 s). LOCA 4 de 5: 19 s con 100 cm² (R44, R83), 120 s con 10 cm² (R19, R88) y la de 5 cm² (R46) no se detecta.

**Lectura honesta**: el transitorio con disparo se reconoce en pocos segundos, pero la familia LOCA necesita unos 10–20 s (y mucho más con roturas pequeñas); el modelo no alcanza la meta de ≤ 10 s del plan de referencia. El F1 de validación se estabiliza en la 2.ª época y la selección por F1 global no premia la rapidez. Mejoras posibles, a evaluar solo con validación: elegir el modelo por el F1 de los primeros segundos, ventanas más cortas o variables de tendencia. La prueba tiene 13 corridas: las cifras tienen mucha incertidumbre.
