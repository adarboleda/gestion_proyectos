# Quickstart: Informe técnico final

## Prerrequisitos

- Features 001–005 con resultados congelados (`fase2_output/`, `fase3_output/`, `fase4_output/`, `fase5_output/`, `pwr3l_output/`).
- Herramienta de conversión a PDF/DOCX acordada con la universidad.

## Pasos

```bash
cd IA-Nuclear/NuclearPowerPlantAccidentData/pipeline

python build_tabla_cumplimiento.py        # nuevo: -> ../../docs/informe/06_cumplimiento_metas.md y cifras.json
python -m unittest test_pwr3l test_fase5 -v   # confirmar que los resultados siguen siendo los reportados
```

Luego, redactar los capítulos de `IA-Nuclear/docs/informe/` y exportar el documento final.

## Verificación

| Verificación | Esperado |
|---|---|
| Metas con fila en la tabla (SC-002) | 100 % |
| Cifras sin fuente en `cifras.json` (SC-003) | 0 |
| Correcciones de documentos (SC-004) | 4 de 4 hechas |
| Lectura por una persona ajena (SC-005) | Regenera un resultado por canal con el anexo |
| Discrepancias entre resumen/presentación e informe (SC-006) | 0 |
| Metas no cumplidas con causa y mitigación (SC-007) | 100 % |
