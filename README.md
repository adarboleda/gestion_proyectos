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

## Consejos

- **No te saltes pasos obligatorios**: cada comando usa lo que generó el anterior.
- **Revisa y edita** los archivos generados (`spec.md`, `plan.md`, `tasks.md`) antes de pasar al siguiente paso. Puedes modificarlos a mano.
- En `/speckit-specify` **no menciones tecnologías**; eso va en `/speckit-plan`.
- Si los comandos `/speckit-*` no aparecen, cierra y vuelve a abrir Claude Code en esta carpeta.
- Para actualizar la herramienta `specify`:
  ```
  python -m uv tool install specify-cli --force --from git+https://github.com/github/spec-kit.git
  ```
