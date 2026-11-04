# Iteraciones SDD 002, 003 y 004: resumen unificado

**Proyecto**: IANuclear, sistema consultivo para detectar accidentes LOCA y ATWS en reactores PWR con datos simulados
**Metodología**: Desarrollo Guiado por Especificaciones con GitHub Spec Kit y la extensión `speckit-metricas` · **Constitución**: v2.0.0, sin cambios en las tres iteraciones
**Fecha de las tres iteraciones**: 2026-10-28 · **Documentos detallados**: [ENTREGABLES-002.md](ENTREGABLES-002.md), [ENTREGABLES-003.md](ENTREGABLES-003.md), [ENTREGABLES-004.md](ENTREGABLES-004.md)

---

## 1. Visión de conjunto

Las tres iteraciones construyen, por partes, la preparación de datos de la planta **PWR 3L** (y refuerzan la de **NPPAD**, hecha en 001):

```
PWR 3L:  descubrir y leer corridas  →  medir paso de TIME  →  agrupar y repartir sin fuga  →  escalar  →  salida/reporte/comando
              (002, Marcelo)             (003, Christian)          (004, Abner)              (003)        (002, cierre 04/11)

NPPAD:   lectura y reparto (001)  +  paso medido de TIME (003)  +  verificación de fuga (004)
```

| | 002 | 003 | 004 |
|---|---|---|---|
| **Tarea** | KAN-18: preprocesamiento PWR 3L (ventanas de 300 s, 5 clases) | Normalización solo con entrenamiento y paso de muestreo medido | División en entrenamiento, validación y prueba sin fuga |
| **Responsable** | Marcelo Acuña | Christian Bonifaz | Abner Arboleda |
| **Rama** | `002-preprocesamiento-pwr3l` | `003-normalizacion-paso-muestreo` | `004-division-sin-fuga` |
| **Estado** | **Completa** (cierre del 2026-11-04 en `002-preprocesamiento-pwr3l-cierre`): 38/38 tareas, `converged` | **Completa**, `converged` | **Completa**, `converged` |
| **Fusionada en `main`** | Sí (PR #2) | Sí (PR #3) | No (pendiente de PR) |

---

## 2. Resumen corto de cada iteración (para exponer)

### 002 · Preprocesamiento PWR 3L (Marcelo Acuña)

- **Problema**: PWR 3L es otra planta (2705 MWt, un dato por segundo); la constitución prohíbe mezclarla con NPPAD, así que necesita paquete y comando propios (`preparacion_pwr3l`, `preparar-pwr3l`).
- **Qué se descubrió en los datos**: 109 corridas en dos formatos (los `.xls` son en realidad libros xlsx), 9 corridas con menos de 300 filas y 6 eventos OOD que no son clase de entrenamiento. Resultado esperado: 91 muestras.
- **Decisiones**: corridas cortas excluidas con aviso (no se inventan datos); LOCA y LOCAC de igual área juntas; gemelas ATWS/TRIP_OK juntas; 26 variables medibles en sala de control (sin `WLR`).
- **Resultado**: spec, plan (12 decisiones), tareas (34 tareas, 95 puntos) y análisis completos; implementado el descubrimiento y la lectura (T001–T010, 31 puntos = 33 %). 44 pruebas, 43 en verde al cerrar.
- **Queda**: el núcleo del preprocesamiento (salida, reporte y comando). La agrupación y el reparto los terminó 004.

### 003 · Normalización y paso de muestreo (Christian Bonifaz)

- **Problema**: el paso de muestreo estaba fijo en el código (10 s en NPPAD, 1 s en PWR 3L) y nada garantizaba que el escalado de PWR 3L usara solo entrenamiento.
- **Qué se hizo**: el paso se **mide** desde la columna `TIME` en todas las filas de cada archivo; si no es constante, positivo e igual en todo el dataset, la preparación se detiene. Se publica en `metadata.json` y en el reporte.
- **Escalado de PWR 3L**: nuevo `escalado.py` que ajusta `StandardScaler` solo con entrenamiento y valida la forma `(N, 300, 26)`.
- **Datos reales**: NPPAD mide 10 s exactos y PWR 3L 1 s exacto, constantes en todos los archivos.
- **Resultado**: 22/22 tareas (48 puntos), `converged`, 166 pruebas en verde; además corrigió la prueba del xlsx que 002 había dejado fallando.

### 004 · División sin fuga de datos (Abner Arboleda)

- **Problema**: en LOCA y LOCAC el mismo tamaño de rotura debe caer en el mismo conjunto para ambas ramas; NPPAD ya lo cumplía (001), PWR 3L no.
- **Qué se hizo**: `grupos.py` (LOCA/LOCAC por área de rotura y gemelas ATWS/TRIP_OK), `particion.py` (reparto 70/15/15 por familia, grupos grandes primero, semilla 42) y `verificacion.py` (comprobación independiente de fuga). `preparar-datos` (NPPAD) también verifica su reparto.
- **Datos reales**: 91 corridas → 63 / 15 / 13; las 14 áreas y las 15 parejas de gemelas en un solo conjunto; 0 violaciones. NPPAD: 142 / 30 / 30 y `COINCIDE` con la referencia.
- **Hallazgo**: el método del proyecto de referencia (IA-Nuclear) agrupa solo gemelas y deja **6 de 10 áreas partidas entre entrenamiento y prueba**; con 004 son 0.
- **Resultado**: 25/25 tareas (54 puntos), `converged`, 44 pruebas nuevas; suite completa con datos reales: 210 pasadas y 1 omitida.

---

## 3. Fases de Spec Kit en cada iteración

| Fase | 002 | 003 | 004 |
|---|---|---|---|
| `/speckit-specify` | 3 historias, 16 FR, 8 SC | 3 historias, 14 FR, 6 SC | 3 historias, 15 FR, 7 SC |
| `/speckit-clarify` | 3 preguntas (elegidas por el agente por delegación) | 2 preguntas (respondidas con el usuario) | 2 preguntas (respondidas por el responsable) |
| `/speckit-plan` | 12 decisiones, 2 contratos | 6 decisiones, 2 contratos | 7 decisiones, 1 contrato |
| `/speckit-tasks` | 34 tareas · 95 puntos | 22 tareas · 48 puntos | 25 tareas · 54 puntos |
| `/speckit-analyze` | 8 hallazgos (0 críticos, 3 medios, 5 bajos) | 3 hallazgos bajos | 7 hallazgos (0 críticos, 1 medio, 6 bajos) |
| Correcciones del análisis | 8 aplicadas | 3 aplicadas | 5 aplicadas con aprobación del responsable |
| `/speckit-implement` | Parcial: T001–T010 | 22/22 | 25/25 |
| `/speckit-converge` | No ejecutado | `converged` | `converged` (primera pasada) |
| Comandos de métricas | `sesion`, `puntos` | todos | todos (`sesion`, `cerrar`, `puntos`, `recolectar`, `calibrar`, `estimar`, `exportar`) |

---

## 4. Métricas unificadas (`speckit-metricas`, `recolectar` del 2026-10-29)

Todas las cifras salen del mismo cálculo (`metricas/salidas/resumen-funcionalidades.csv`), así que son comparables entre iteraciones. Pueden diferir un poco de los documentos individuales; las diferencias se explican en las notas.

### 4.1 Tamaño de la especificación

| Medida | 002 | 003 | 004 | **Total** |
|---|---|---|---|---|
| Historias de usuario | 3 | 3 | 3 | **9** |
| Requisitos funcionales (FR) | 16 | 14 | 15 | **45** |
| Criterios de éxito (SC) | 8 | 6 | 7 | **21** |
| Escenarios de aceptación | 10 | 13 | 15 | **38** |
| Tareas planeadas | 34 | 22 | 25 | **81** |
| Tareas hechas | 10 ⁽¹⁾ | 22 | 25 | **57 (70 %)** |
| Puntos de tarea del plan | 95 | 48 | 54 | **197** |
| Puntos de tarea hechos | 31 | 48 | 54 | **133 (68 %)** |

### 4.2 Esfuerzo

| Fase (horas) | 002 | 003 | 004 | **Total** |
|---|---|---|---|---|
| Especificar | 0,25 | 0,25 | 0,25 | 0,75 |
| Aclarar | 0,25 | 0,25 | 0,25 | 0,75 |
| Planificar | 0,25 | 0,25 | 0,25 | 0,75 |
| Tareas | 0,25 | 0,25 | 0,25 | 0,75 |
| Analizar (incluye converge) | 0,25 | 0,25 | 0,50 | 1,00 |
| Implementar | 0,25 | 0,25 | 0,25 | 0,75 |
| **Total** | **1,50** | **1,50** | **1,75** | **4,75 h** |
| Sesiones | 6 | 6 | 7 | **19** |
| Persona-mes | 0,0099 | 0,0099 | 0,0115 | **0,0313** |
| Modelo de IA | `claude-opus-5-5` | `claude-opus-5-5` (medium) y `gemini-4-argon` (low) | `claude-opus-5-5` | |

⚠ Las horas son el **mínimo que la extensión registra por sesión (0,25 h)**, no un cronómetro: en el reloj, cada iteración tomó entre 20 y 35 minutos de trabajo del agente. La exploración previa de los datos no está registrada. No se informaron tokens ni costo.

### 4.3 Código, pruebas y desperdicio

| Medida | 002 | 003 | 004 | **Total** |
|---|---|---|---|---|
| Commits | 10 | 10 | 17 | **37** |
| Código agregado | 342 | 266 | 276 | **884** |
| Código que sobrevive | 329 | 266 | 275 | **870** |
| Código eliminado en la iteración | 0 | 36 | 2 | **38** |
| · por requisito | 0 | 36 | 1 | 37 |
| · sin clasificar | 0 | 0 | 1 ⁽²⁾ | 1 |
| Desperdicio atribuido | 13 ⁽³⁾ | 0 | 1 | **14 (1,6 %)** |
| Pruebas agregadas / eliminadas | +496 / −0 | +376 / −31 | +568 / −0 | **+1440 / −31** |
| Pruebas nuevas | 44 | 166 en la suite al cerrar | 44 | — |

**Notas**

1. `recolectar` informa 0 tareas hechas en 002 porque su `tasks.md` no se marcó; según su documento, T001–T010 están implementadas.
2. Un commit de 004 (`53069a5`) reescribió 2 líneas sin el trailer `Causa:`; su causa real es `requisito`.
3. Son 13 líneas escritas en 002 (el paso de muestreo fijo) que 003 reemplazó por el paso medido: el script las cuenta como desperdicio de quien las escribió. En 003 figuran como «eliminadas por requisito».

### 4.4 Proyecto completo (001–004)

| Medida | Valor |
|---|---|
| Funcionalidades | 4 |
| Historias / FR / SC | 12 / 58 / 29 |
| Puntos de tarea | 300 (279 del plan + 21 agregados después del plan) |
| Tareas | 86 marcadas como hechas de 120; las 34 sin marcar son las de 002 (10 de ellas ya implementadas) |
| Código entregado | 2128 agregadas, 2076 sobreviven |
| Pruebas | +3447 líneas |
| Desperdicio | 52 líneas (2,4 %): 37 por requisito, 14 por defecto, 1 sin clasificar |
| Esfuerzo | 7,5 h en 29 sesiones (0,0493 persona-mes) |
| Pruebas automáticas hoy | **210 pasadas, 1 omitida** (con los datos reales, rama 004) |

### 4.5 Calibración y estimación (`calibrar`, `estimar`)

- **Calibración con 4 puntos (001–004): modelo exploratorio.** La mejor medida de tamaño es KSLOC: `PM = 0,0253 · KSLOC^0,706`, MMRE 0,08, PRED(25) 1,0 y MMRE en validación cruzada 0,24. COCOMO II estándar no sirve a esta escala (MMRE 76).
- **Estimación de 004** con el modelo: 1,6–1,7 h, frente a 1,75 h reales. No es una validación independiente, porque 004 está en los datos de calibración.
- **Dataset exportado**: `metricas/salidas/dataset-IANuclear-20261028.zip`.

---

## 5. Carpetas: dónde está cada cosa

```
gestion_proyectos/
├── ENTREGABLES-002.md                  ← detalle de 002
├── ENTREGABLES-003.md                  ← detalle de 003
├── ENTREGABLES-004.md                  ← detalle de 004
├── ENTREGABLES-002-003-004.md          ← este documento
│
├── specs/
│   ├── 002-preprocesamiento-pwr3l/     spec, plan, research, data-model, contracts/ (cli, salidas),
│   │                                   quickstart, tasks, puntos-tarea.csv, analisis-inicial, checklists/
│   ├── 003-normalizacion-paso-muestreo/  los mismos documentos que 002
│   └── 004-division-sin-fuga/          los mismos documentos + contracts/api.md y auditoria.md
│
├── src/
│   ├── preparacion_datos/              NPPAD (001)
│   │   ├── lectura.py, config.py, salida.py, reporte.py, escalado.py, cli.py   ← paso medido (003)
│   │   └── verificacion.py             ← NUEVO en 004 (y cli.py la llama)
│   └── preparacion_pwr3l/              PWR 3L
│       ├── config.py, descubrimiento.py, lectura.py   ← 002 (paso medido: 003)
│       ├── escalado.py                 ← 003
│       └── grupos.py, particion.py, verificacion.py   ← 004
│
├── tests/
│   ├── datos_reales.py                 ← 004 (variable IANUCLEAR_DATOS)
│   ├── unit/                           NPPAD (test_verificacion.py: 004)
│   ├── integration/                    NPPAD (test_verificacion_real.py: 004)
│   └── pwr3l/
│       ├── unit/                       descubrimiento y lectura (002), escalado (003),
│       │                               grupos, particion y verificacion (004)
│       └── integration/                test_pwr3l_particion_real.py (004)
│
└── metricas/
    ├── config.json
    ├── sesiones/                       un archivo por sesión:
    │                                   002 → 20261028-1843 … 1856 (6)
    │                                   003 → 20261028-2008 … 2030 (6)
    │                                   004 → 20261028-2148 … 2214 (7)
    └── salidas/                        (no se versiona) resúmenes, calibración, dataset exportado
```

---

## 6. Pendientes del equipo

| Pendiente | Responsable previsto | Detalle |
|---|---|---|
| ~~Terminar KAN-18 (002)~~ **Hecho el 2026-11-04** (rama `002-preprocesamiento-pwr3l-cierre`, ver [ENTREGABLES-002.md](ENTREGABLES-002.md)) | Marcelo Acuña | Salida `X_*`, `y_*`, `margins_*`, reporte, `metadata.json` y comando `preparar-pwr3l` (T019–T034 de 002), usando `repartir` y `verificar_reparto(corridas, reparto)` de 004 con todas las corridas, y el escalado de 003. Marcar en el `tasks.md` de 002 las tareas ya hechas (T001–T010, y T012, T013, T016 y T017 cubiertas por 004) |
| PR de 004 | Abner Arboleda | Subir la rama y abrir el pull request hacia `main` |
| Limitación conocida | — | Las corridas NORM parecidas entre sí no se agrupan (D1 de 002) |
