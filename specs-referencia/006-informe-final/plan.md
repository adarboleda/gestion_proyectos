# Implementation Plan: Informe técnico final y documentación consolidada

**Branch**: `006-informe-final` | **Date**: 2026-10-18 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/006-informe-final/spec.md`

## Summary

Escribir el informe técnico final como capítulos en Markdown dentro del repositorio, con una tabla de cumplimiento generada desde los archivos de resultados (para que cada cifra tenga fuente), corregir los cuatro documentos con errores conocidos, y derivar de ahí el resumen ejecutivo y la presentación en español e inglés. Se escribe después de cerrar la Fase 5 para no citar cifras que cambien.

## Technical Context

**Language/Version**: Markdown para los capítulos; Python 3.x para el script que arma la tabla de cumplimiento

**Primary Dependencies**: Ninguna nueva; conversión a PDF/DOCX con la herramienta que fije la universidad (por ejemplo, Pandoc)

**Storage**: Archivos de texto en `IA-Nuclear/docs/informe/`

**Testing**: Revisión por una persona ajena al código y verificación automática de que cada cifra de la tabla existe en su archivo fuente

**Target Platform**: Documento PDF/DOCX para entrega

**Project Type**: Documentación

**Performance Goals**: N/A (ventana de 1.5 semanas: 24 oct – 4 nov 2026)

**Constraints**: Cifras solo de archivos de resultados vigentes; español con resumen en inglés; lenguaje consultivo inequívoco

**Scale/Scope**: ~8 capítulos + anexos; ~9 metas del canal rápido + metas de Fases 1–5; 4 correcciones de documentos

## Constitution Check

| Principio | Cumplimiento |
|---|---|
| I. Consultiva | ✅ FR-011: declaración explícita. |
| II. Causalidad / sin fuga | ✅ El informe describe cómo se evitó (particiones, escaladores, causalidad). |
| III. Honestidad | ✅ Tabla de cumplimiento con metas no cumplidas y capítulo de limitaciones. |
| IV. Abstención y compuertas | ✅ Descritas con sus resultados reales. |
| V. Procedencia | ✅ FR-002. |
| VI. Alcance | ✅ FR-001. |

**Post-diseño**: sin violaciones.

## Project Structure

### Documentation (this feature)

```text
specs/006-informe-final/
├── plan.md
├── research.md
├── quickstart.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

*Esta feature no tiene `data-model.md` ni `contracts/`: no maneja datos ni interfaces externas.*

### Source Code (repository `IA-Nuclear/`)

```text
IA-Nuclear/docs/
├── informe/
│   ├── 00_resumen.md                   # español + resumen en inglés
│   ├── 01_introduccion_alcance.md
│   ├── 02_revision_literatura.md       # desde RSL.docx y Articulos/
│   ├── 03_datos_dos_plantas.md         # NPPAD y PWR 3L
│   ├── 04_metodologia.md               # Fases 1–5, normalización, TTD, ruido, ablación
│   ├── 05_resultados.md                # por fase y por canal
│   ├── 06_cumplimiento_metas.md        # tabla generada
│   ├── 07_limitaciones.md
│   ├── 08_conclusiones_trabajo_futuro.md
│   ├── anexo_reproduccion.md
│   └── cifras.json                     # cada cifra con su archivo de origen
├── planning/                           # documentos a corregir
└── (resumen, presentaciones y consolas existentes)
NuclearPowerPlantAccidentData/pipeline/
└── build_tabla_cumplimiento.py         # NUEVO: arma 06_cumplimiento_metas.md desde los JSON de resultados
```

**Structure Decision**: Carpeta `informe/` con un archivo por capítulo para poder revisarlos por separado; la tabla de cumplimiento se genera para evitar transcribir cifras a mano.

## Complexity Tracking

| Decisión | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| Script que genera la tabla de cumplimiento | SC-003: cero cifras sin fuente | Copiar las cifras a mano reproduce el problema de las versiones inconsistentes |
