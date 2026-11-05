# Tasks: Hito 1 — informe de resultados preliminares

**Input**: `/specs/007-hito1-resultados/` · **Tests**: primero, deben fallar antes del código.

## Format: `[ID] [P?] [Story] Description`

Código en `src/informe_hito1/`; pruebas en `tests/hito1/` con el prefijo `test_hito1_`. Commits `feat(007)`, `test(007)`, `docs(007)`.

---

## Phase 1: Setup

- [X] T001 Añadir a `pyproject.toml` el guion `informe-hito1 = "informe_hito1.cli:main"` y nombrar 007 en `description`; crear `src/informe_hito1/__init__.py` y `__main__.py`; añadir `informe_hito1/` al `.gitignore`

## Phase 2: Foundational (fuentes)

- [X] T002 Crear `tests/hito1/conftest.py` con archivos de resultados sintéticos que tengan la misma forma que los reales (reporte de 005; resumen y regla de 006; tiempos de 008; reporte de 009; evaluación de 011), escritos en un directorio temporal
- [X] T003 [P] Crear `tests/hito1/unit/test_hito1_fuentes.py`:
  - lectura de las cinco fuentes y SHA-256;
  - archivo ausente → error con el archivo y el comando;
  - JSON ilegible → error;
  - falta una clave requerida → error que la nombra
- [X] T004 Crear `src/informe_hito1/config.py` (fuentes, aviso, limitaciones) y `src/informe_hito1/fuentes.py` (`ErrorFuente`, `cargar_fuentes(rutas)`)

## Phase 3: US1 — informe del Hito 1 (P1)

- [X] T005 [P] [US1] Crear `tests/hito1/unit/test_hito1_consolidar.py`:
  - metas copiadas de 008, 005 y 009 con definición, valor, conjunto y estado;
  - meta de falsas alarmas de la regla (006);
  - matriz 3 × 4 y tasas de 011 que suman 1;
  - validación cruzada;
  - tiempos de prueba de 008;
  - regla por conjunto;
  - Etapa 2 con su cobertura; una meta cumplida sin decisiones queda como «cumple sin decisiones (cobertura 0 %)» (análisis U1);
  - falsas alarmas
- [X] T006 [P] [US1] Crear `tests/hito1/unit/test_hito1_informe.py`:
  - las 11 secciones en orden;
  - aviso consultivo al principio;
  - cada sección cita su KAN y su archivo;
  - las tablas de metas y de la matriz con los valores de la fuente;
  - la validación cruzada dice que reentrena por fold, mientras que prueba y validación usan el modelo publicado (análisis A1)
- [X] T007 [US1] Crear `src/informe_hito1/consolidar.py` con `consolidar(datos)`
- [X] T008 [US1] Crear `src/informe_hito1/informe.py` con `formatear_markdown(hito)`

## Phase 4: US2 — comando, trazabilidad y reproducibilidad (P1)

- [X] T009 [US2] Crear `tests/hito1/integration/test_hito1_cli.py`:
  - código 0 con `hito1.md` y `hito1.json`;
  - SHA-256 de las fuentes;
  - mismo `hito1.json` en dos ejecuciones;
  - falta una fuente → código 1, nombra el comando y no hay salida;
  - `python -m informe_hito1`;
  - valores por defecto
- [X] T010 [US2] Crear `src/informe_hito1/cli.py` y publicar todos o ninguno
- [X] T011 Crear `tests/hito1/integration/test_hito1_real.py` (se omite si no existen los resultados reales): código 0 y cada cifra clave del informe igual a la de su archivo

## Phase 5: Polish

- [X] T012 [P] Añadir al `README.md` la sección «Informe del Hito 1 (funcionalidad 007, KAN-27)»
- [X] T013 Generar el informe con los resultados reales y anotar en `quickstart.md` las cifras principales
- [X] T014 Ejecutar la suite completa

---

## Phase 6: Convergence

- [X] T015 Concordancia en `src/informe_hito1/consolidar.py`: «1 falsa alarma» y no «1 falsas alarmas» en la meta de la regla per FR-008 (partial)
- [X] T016 Nombres legibles en la tabla de validación cruzada de `src/informe_hito1/informe.py` («Tasa de abstención», «Exactitud estándar»…), no las claves internas sin tildes per FR-008 (partial)
