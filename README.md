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

Prepara las corridas de la planta **PWR 3L** (2705 MWt, un dato por segundo; carpeta `PWR 3L`) en muestras de **300 pasos de 1 s** con **cinco clases**: NORM (0), LOCA (1), LOCAC (2), ATWS (3) y TRIP_OK (4). Es una planta distinta de NPPAD: paquete, comando y salida propios, sin mezclar datos. Las corridas se reparten por **grupos completos** (gemelas ATWS/TRIP_OK juntas; LOCA y LOCAC de igual área de rotura juntas), ≈ 70/15/15 con semilla 42, y el escalador se ajusta solo con entrenamiento.

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

Con la carpeta real: 109 corridas encontradas → 91 muestras (62 / 15 / 14). No aportan muestra las 6 OOD, las 3 descartadas por el equipo (R07, R27, R28) y 9 corridas con menos de 300 filas (se excluyen con aviso; no se rellenan).

**Pruebas**: `pytest tests/pwr3l`. Detalle: [specs/002-preprocesamiento-pwr3l/quickstart.md](specs/002-preprocesamiento-pwr3l/quickstart.md).

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
