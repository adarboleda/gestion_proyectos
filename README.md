# gestion_proyectos

Proyecto configurado con [GitHub Spec Kit](https://github.com/github/spec-kit) para trabajar con **Desarrollo Guiado por Especificaciones** (Spec-Driven Development) usando Claude Code.

La idea es simple: **primero se define QUÉ se quiere y POR QUÉ, después CÓMO, y al final se programa.**

---

## Orden de uso (paso a paso)

Escribe estos comandos en el chat de Claude Code, **en este orden**:

| # | Comando | ¿Obligatorio? | Qué hace | Qué genera |
|---|---------|---------------|----------|------------|
| 1 | `/speckit-constitution` | Sí (una sola vez) | Define los principios y reglas del proyecto (calidad, pruebas, estilo, etc.) | `.specify/memory/constitution.md` |
| 2 | `/speckit-specify` | Sí | Describe la funcionalidad: **qué** quieres y **por qué** (sin hablar de tecnología) | `specs/001-nombre/spec.md` |
| 3 | `/speckit-clarify` | Opcional (recomendado) | Te hace hasta 5 preguntas para aclarar lo que quedó ambiguo en la especificación | Actualiza `spec.md` |
| 4 | `/speckit-plan` | Sí | Define el **cómo**: tecnologías, arquitectura, modelo de datos | `plan.md`, `research.md`, `data-model.md`, etc. |
| 5 | `/speckit-checklist` | Opcional | Crea una lista de verificación para revisar que los requisitos estén completos y claros | `checklists/*.md` |
| 6 | `/speckit-tasks` | Sí | Divide el plan en tareas pequeñas y ordenadas | `tasks.md` |
| 7 | `/speckit-analyze` | Opcional (recomendado) | Revisa que spec, plan y tareas sean coherentes entre sí (no modifica nada) | Reporte en el chat |
| 8 | `/speckit-implement` | Sí | Ejecuta las tareas de `tasks.md` y escribe el código | Código del proyecto |
| 9 | `/speckit-converge` | Opcional | Compara el código con la spec y agrega a `tasks.md` lo que faltó construir | Actualiza `tasks.md` |

> **Resumen rápido:** `constitution` → `specify` → `clarify` → `plan` → `tasks` → `analyze` → `implement`

---

## Ejemplos

**1. Constitución** (solo la primera vez):
```
/speckit-constitution El código debe ser simple y legible, toda funcionalidad debe tener pruebas, la interfaz debe estar en español.
```

**2. Especificación** (enfócate en el qué y el por qué, NO en la tecnología):
```
/speckit-specify Quiero una aplicación para gestionar proyectos donde pueda crear proyectos, asignar tareas a miembros del equipo y ver el avance de cada proyecto.
```

**3. Aclaraciones:**
```
/speckit-clarify
```

**4. Plan** (aquí SÍ se habla de tecnología):
```
/speckit-plan Usar Python con Flask, base de datos SQLite y HTML/CSS simple para el frontend.
```

**5. Tareas, análisis e implementación:**
```
/speckit-tasks
/speckit-analyze
/speckit-implement
```

---

## Para una nueva funcionalidad

La constitución se hace **una sola vez**. Para cada funcionalidad nueva repite desde el paso 2:

```
/speckit-specify  →  /speckit-clarify  →  /speckit-plan  →  /speckit-tasks  →  /speckit-analyze  →  /speckit-implement
```

Cada funcionalidad queda en su propia carpeta numerada: `specs/001-...`, `specs/002-...`, etc.

---

## Estructura de carpetas

```
gestion_proyectos/
├── .claude/skills/        # Comandos /speckit-* para Claude Code
├── .specify/
│   ├── memory/
│   │   └── constitution.md   # Principios del proyecto
│   ├── scripts/powershell/   # Scripts auxiliares de Spec Kit
│   └── templates/            # Plantillas de spec, plan, tasks y checklist
└── specs/                 # (se crea al usar /speckit-specify)
    └── 001-mi-funcionalidad/
        ├── spec.md
        ├── plan.md
        └── tasks.md
```

---

## Preparación de datos (funcionalidad 001)

Prepara los datos de simulación NPPAD (carpeta `Operation_csv_data`) para entrenar y evaluar después un clasificador de accidentes PWR, sin fuga de información: las simulaciones se reparten completas (70/15/15, semilla 42), una simulación nunca está en dos conjuntos y el escalador se ajusta solo con entrenamiento.

**Instalación** (Python 3.11 o superior, desde la raíz del repositorio):

```
pip install -e ".[dev]"
```

**Ejecución** (un solo comando; imprime el reporte y escribe `data_processed/`):

```
preparar-datos
```

Equivale a `python -m preparacion_datos`. Opciones: `--origen RUTA` (por defecto `../IA-Nuclear/NuclearPowerPlantAccidentData/Operation_csv_data`, solo lectura), `--salida RUTA`, `--semilla N` y `--referencia RUTA` o `--sin-referencia`. Si un archivo de origen es defectuoso, el comando termina con código 1, nombra el archivo y la causa, y no escribe ningún conjunto.

**Salida** en `data_processed/` (se regenera con el comando; no se edita a mano):

| Archivo | Contenido |
|---|---|
| `X_train/val/test.npy` | `(N,150,12)` float32: 12 variables de planta escaladas |
| `y_train/val/test.npy` | `(N,)` int64: 0 = NORM, 1 = LOCA, 2 = LOCAC, 3 = ATWS |
| `margins_train/val/test.npy` | `(N,150,7)` float64: 7 márgenes térmicos sin escalar |
| `scaler_mean.npy`, `scaler_std.npy` | `(12,)` parámetros de escala, ajustados solo con entrenamiento |
| `metadata.json` | conteos, simulaciones de cada conjunto, advertencias y limitaciones |

Normal y ATWS tienen una sola simulación en el dataset: van completas a entrenamiento y no tienen muestras de validación ni de prueba; el reporte lo advierte.

**Pruebas**: `pytest`. Detalle y validaciones: [specs/001-preparacion-datos/quickstart.md](specs/001-preparacion-datos/quickstart.md).

---

## Preprocesamiento PWR 3L (funcionalidad 002, KAN-18)

Prepara las corridas de la planta **PWR 3L** (2705 MWt, un dato por segundo; carpeta `PWR 3L`) en muestras de **300 pasos de 1 s** con **cinco clases**: NORM (0), LOCA (1), LOCAC (2), ATWS (3) y TRIP_OK (4). Es una planta distinta de NPPAD: paquete, comando y salida propios, sin mezclar datos. Las corridas se reparten por **grupos completos** (gemelas ATWS/TRIP_OK juntas; LOCA y LOCAC de igual área de rotura juntas), ≈ 70/15/15 con semilla 42 (reparto y verificación de fuga de 004), el escalador se ajusta solo con entrenamiento (003) y el paso de muestreo se mide desde `TIME` (003).

**Ejecución** (tras `pip install -e ".[dev]"`; imprime el reporte y escribe `data_processed_pwr3l/`):

```
preparar-pwr3l
```

Equivale a `python -m preparacion_pwr3l`. Opciones: `--origen RUTA` (por defecto `../IA-Nuclear/PWR 3L`, solo lectura), `--salida RUTA` y `--semilla N`. Un archivo defectuoso termina con código 1, nombra el archivo y la causa, y no escribe nada.

**Salida** en `data_processed_pwr3l/` (se regenera; no se edita a mano):

| Archivo | Contenido |
|---|---|
| `X_train/val/test.npy` | `(N,300,26)` float32: 26 variables medibles escaladas (sin `WLR`) |
| `y_train/val/test.npy` | `(N,)` int64: 0 = NORM, 1 = LOCA, 2 = LOCAC, 3 = ATWS, 4 = TRIP_OK |
| `margins_train/val/test.npy` | `(N,300,7)` float64: 7 márgenes térmicos sin escalar |
| `scaler_mean.npy`, `scaler_std.npy` | `(26,)`, ajustados solo con entrenamiento |
| `metadata.json` | corridas y grupos de cada conjunto (orden de las filas), corridas excluidas con su motivo, advertencias y limitaciones |

Con la carpeta real: 109 corridas encontradas → 91 muestras (63 / 15 / 13). No aportan muestra las 6 OOD, las 3 descartadas por el equipo (R07, R27, R28) y 9 corridas con menos de 300 filas (se excluyen con aviso; no se rellenan).

**Pruebas**: `pytest tests/pwr3l`. Detalle: [specs/002-preprocesamiento-pwr3l/quickstart.md](specs/002-preprocesamiento-pwr3l/quickstart.md).

---

## División sin fuga de datos (funcionalidad 004)

Reparte las corridas usables de **PWR 3L** en entrenamiento, validación y prueba por corrida completa, sin fuga de datos:

- Las LOCA y LOCAC con **la misma área de rotura** van al mismo conjunto (división pareada por severidad).
- Cada ATWS va con su **gemela TRIP_OK**.
- Los grupos se reparten por familia (NORM; LOCA y LOCAC; ATWS y TRIP_OK) hacia 70/15/15, de mayor a menor tamaño, con semilla 42.
- Una verificación independiente comprueba que ninguna corrida ni grupo quede en dos conjuntos.

```python
from preparacion_pwr3l.lectura import cargar_corridas
from preparacion_pwr3l.grupos import formar_grupos
from preparacion_pwr3l.particion import repartir
from preparacion_pwr3l.verificacion import verificar_reparto

corridas = cargar_corridas("../IA-Nuclear/PWR 3L")
reparto = repartir(formar_grupos(corridas))   # verifica su propio resultado
verificar_reparto(corridas, reparto)          # con todas las corridas, también las excluidas
print(reparto.conteos)
```

`preparar-datos` (NPPAD) también verifica su partición: si encontrara una fuga, termina con código 1 y el mensaje `FUGA DE DATOS` sin publicar nada.

**Pruebas con los datos reales**: si IA-Nuclear no está en `../IA-Nuclear`, indica su ruta con la variable `IANUCLEAR_DATOS` (PowerShell: `$env:IANUCLEAR_DATOS = "C:\ruta\IA-Nuclear"`). Detalle: [specs/004-division-sin-fuga/quickstart.md](specs/004-division-sin-fuga/quickstart.md).

---

## Clasificador de Etapa 1 (funcionalidad 005)

Una Bi-LSTM que, cada segundo, mira los últimos 30 s de las 26 variables medibles de **PWR 3L** y recomienda la familia del evento: **NORM** (operación normal), **LOCA** (rama caliente o fría) o **TRANS** (transitorio con disparo: ATWS o TRIP_OK). Se entrena con el reparto sin fuga de 004, el escalado de 003, pesos de clase para el desbalance y parada por validación. Es **consultivo**: recomienda, no actúa sobre la planta.

**Instalación** (PyTorch para CPU):

```powershell
uv pip install --python .venv\Scripts\python.exe -e ".[dev]"
uv pip install --python .venv\Scripts\python.exe torch --index-url https://download.pytorch.org/whl/cpu
```

**Entrenar y evaluar**:

```powershell
.venv\Scripts\entrenar-etapa1.exe --origen "D:\Personal\IANuclear\PWR 3L" --salida modelos\etapa1
```

Deja en `modelos\etapa1\` (no se versiona) `modelo.pt`, `modelo.json`, `reporte.json` y `reporte.txt`, e imprime el reporte: métricas por familia, exhaustividad a 1–30 s del inicio del evento, tiempo de confirmación de cada corrida de prueba (≥ 0,80 dos segundos seguidos), falsas alarmas y metas.

**Usar el modelo**:

```python
from clasificador_etapa1.prediccion import cargar
resultado = cargar("modelos/etapa1").clasificar(serie)   # serie: (T, 26) sin escalar, hasta el instante actual
# {"probabilidades": {...}, "recomendacion": "LOCA" | ... | "INCIERTO", "aviso": "Recomendación consultiva: ..."}
```

Resultados y detalle: [specs/005-clasificador-etapa1/quickstart.md](specs/005-clasificador-etapa1/quickstart.md).

---

## Regla determinista de ATWS (funcionalidad 006, KAN-22)

Regla fija y explicable para el canal rápido de **PWR 3L**. Si hay **demanda de disparo** del reactor y el flujo neutrónico (PWNT) sigue por encima de un umbral **2 s después**, recomienda **«posible ATWS»**. Es **consultiva**: no actúa sobre la planta ni sustituye la protección.

- **Demanda de disparo** = primera señal del sistema de protección en el registro de eventos (`*.dat`: Low SG Level, Turbine trip, RCP-A trip, Scram …) o PWNT ≥ 118 % (alto flujo), más el retardo de la lógica de protección para ese tipo de señal.
- **Calibración solo con entrenamiento** del reparto de 004: los retardos por tipo (el mayor tiempo señal → «Reactor Scram») y el umbral (punto medio entre el ATWS con menor flujo y el no-ATWS con mayor flujo).

```
evaluar-regla-atws                    # o: python -m regla_atws
```

Opciones: `--origen` (por defecto `../IA-Nuclear/PWR 3L`), `--salida` (`resultados_regla_atws`) y `--semilla` (42). Escribe `regla.json`, `evaluacion.csv` (una fila por corrida) y `resumen.json`.

**Resultado con la carpeta real**:
- Umbral: 19.3 % del PWNT inicial. Margen en entrenamiento: el ATWS con menor flujo queda en 32.9 % y el no-ATWS con mayor flujo en 5.7 %.
- **18 de 18 ATWS detectados**, todos en ≤ 3 s desde la demanda.
- **1 falsa alarma** (R54, en validación). Es un disparo correcto por turbina, un tipo de señal sin ejemplo en entrenamiento: recibe el mayor retardo de entrenamiento (2.5 s), y el real es de 5 s.

Detalle: [specs/006-regla-atws/quickstart.md](specs/006-regla-atws/quickstart.md).

---

## Tiempo de detección desde la falla (funcionalidad 008, KAN-25)

Mide cuánto tardan el clasificador de Etapa 1 (005) y la regla de ATWS (006) en reconocer el evento en **PWR 3L**. Reproduce cada corrida de validación y de prueba segundo a segundo, de forma causal: en cada segundo solo usa los datos hasta ese segundo. El tiempo se cuenta **desde el instante de la falla**, no desde el inicio de la ventana ni desde el inicio que detectó el validador. No entrena ni ajusta nada.

- **Instante de la falla.** En ATWS y TRIP_OK es la primera línea del Transient Report (`*.dat`, con t > 0) que registra la acción iniciadora: cierre de una FWIV, «RCP-A trip», «Turbine Trip Control Change: True» o la válvula de la turbina del AFW al 100 %. En las demás corridas el registro no anota la rotura, así que se usa el **instante programado**: el retardo de la falla en `config.json` (sin contar la falla 8) o el `_t<n>` del nombre de la carpeta.
- **Corrida incierta.** Es aquella en la que el validador ve cambios más de 2 s antes del instante de la falla. Se informa aparte y no cuenta para la meta de diagnóstico.
- **Diagnóstico.** Es el primer segundo τ en que la familia correcta tiene probabilidad ≥ 0,80 dos segundos seguidos, con τ − 1 ≥ t_falla. El tiempo es τ − t_falla.
- **ATWS.** Es la decisión «posible ATWS» de la regla menos la demanda de disparo. El tiempo desde la falla se da como dato.

```powershell
.venv\Scripts\medir-tiempo-deteccion.exe --origen "D:\Personal\IANuclear\PWR 3L" --modelo modelos\etapa1   # o: python -m tiempo_deteccion
```

Opciones: `--origen`, `--modelo` (`modelos/etapa1`, publicado por `entrenar-etapa1`), `--salida` (`resultados_tiempo_deteccion`) y `--semilla` (42; debe ser la del modelo, o el comando termina con código 1).

El comando escribe cuatro archivos:
- `tiempos.json`: por corrida, resumen, metas, falsas alarmas, confusiones, inciertas e instantes.
- `tiempos.csv`: una fila por corrida.
- `lineas_tiempo.csv`: una fila por corrida y segundo, con las probabilidades, la familia confirmada y la decisión de ATWS.
- `reporte.txt`: el reporte legible.

**Cómo leer las metas**:
- `diagnostico_10s` cuenta las corridas de evento de prueba no inciertas confirmadas en ≤ 10 s desde la falla.
- `atws_3s` cuenta los ATWS de validación y prueba reconocidos en ≤ 3 s desde la demanda. La regla no usó validación para calibrarse.

**Resultado con la carpeta real** (≈ 1 min, idéntico en dos ejecuciones):
- Instante de la falla: 72 corridas de evento (29 del registro y 43 programado). Hay 5 inciertas: R22, R47, R48, R54 y R99; ninguna está en prueba.
- **Diagnóstico ≤ 10 s: NO CUMPLE (5 de 10 en prueba).** TRANS: 5 de 5, en 2–5 s. LOCA: 0 de 5, en 19 s (100 cm²), 120–121 s (10 cm²) y no detectada (5 cm²).
- **ATWS ≤ 3 s desde la demanda: CUMPLE (6 de 6;** solo prueba, 3 de 3), en 2–2,5 s.
- Falsas alarmas en prueba: 0 de la Etapa 1 y 0 de la regla. En validación, 1 de la regla (R54, la misma de 006).

Detalle: [specs/008-tiempo-desde-falla/quickstart.md](specs/008-tiempo-desde-falla/quickstart.md).

---

## Clasificador de Etapa 2 (funcionalidad 009)

Una Bi-LSTM que separa la rotura en **rama caliente (LOCA)** de la rotura en **rama fría (LOCAC)** cuando la Etapa 1 detecta la familia LOCA en **PWR 3L**. Utiliza como entrada los dos canales de desviación pico causal de potencia térmica (`PWR`) y flujo neutrónico (`PWNT`) previa al scram. Si la confianza es menor al 80 %, el sistema se abstiene (`UNCERTAIN`). Si la Etapa 1 no indica LOCA, devuelve `NO_APLICA`. La salida es **consultiva**: recomienda, no actúa sobre la planta.

**Entrenar y evaluar**:

```powershell
.venv\Scripts\entrenar-etapa2.exe --origen "C:\Users\Administrador\Desktop\Nuecleare\IA-Nuclear\PWR 3L" --salida modelos\etapa2
```

Deja en `modelos\etapa2\` (no se versiona) `modelo.pt`, `modelo.json`, `reporte.json` y `reporte.txt`, e imprime el reporte con las métricas con abstención, horizontes a 1–30 s, resultado por corrida y por rango de área.

**Usar el modelo en cascada**:

```python
from clasificador_etapa2.prediccion import cargar
etapa2 = cargar("modelos/etapa2")
resultado = etapa2.clasificar(serie, familia_etapa1="LOCA")  # serie: (T, 2) de [PWR, PWNT] crudas
```

Detalle: [specs/009-clasificador-etapa2/quickstart.md](specs/009-clasificador-etapa2/quickstart.md).

---

## Consejos

- **No te saltes pasos obligatorios**: cada comando usa lo que generó el anterior.
- **Revisa y edita** los archivos generados (`spec.md`, `plan.md`, `tasks.md`) antes de pasar al siguiente paso. Puedes modificarlos a mano.
- En `/speckit-specify` **no menciones tecnologías**; eso va en `/speckit-plan`.
- Si los comandos `/speckit-*` no aparecen, cierra y vuelve a abrir Claude Code en esta carpeta.
- Para actualizar la herramienta `specify`:
  ```
  python -m uv tool install specify-cli --force --from git+https://github.com/github/spec-kit.git
  ```
