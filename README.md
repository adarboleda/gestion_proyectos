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

## Consejos

- **No te saltes pasos obligatorios**: cada comando usa lo que generó el anterior.
- **Revisa y edita** los archivos generados (`spec.md`, `plan.md`, `tasks.md`) antes de pasar al siguiente paso. Puedes modificarlos a mano.
- En `/speckit-specify` **no menciones tecnologías**; eso va en `/speckit-plan`.
- Si los comandos `/speckit-*` no aparecen, cierra y vuelve a abrir Claude Code en esta carpeta.
- Para actualizar la herramienta `specify`:
  ```
  python -m uv tool install specify-cli --force --from git+https://github.com/github/spec-kit.git
  ```
