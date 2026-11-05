# Research & Analysis: Documentación del dataset de Fase 1

## 1. Fuentes de Datos y Análisis Comparativo

### 1.1 Repositorio de Referencia (`C:\Users\Administrador\Desktop\Nuecleare\IA-Nuclear`)

Se analizaron las tres fuentes clave existentes en el repositorio de referencia:
1. `NuclearPowerPlantAccidentData/README_ES.md` / `README.md`:
   - Publicación original: *Qi, B., Xiao, X., Liang, J. et al. An open time-series simulated dataset covering various accidents for nuclear power plants. Sci Data 9, 766 (2022)*.
   - Simulador: PCTRAN (Micro-Simulation Technology), ampliamente empleado en entrenamiento y análisis de seguridad nuclear.
   - Modelo de planta: Reactor de agua a presión (PWR) de 2 lazos con generadores de vapor tipo recirculación, presurizador con rociadores y calentadores, y sistemas de salvaguardias (HPI, LPSI, acumuladores).
   - Variables globales: 97 variables de estado termohidráulico, neutrónico, radiológico y de contención.
2. `NuclearPowerPlantAccidentData/pipeline/README_FASE1.md`:
   - Define el pipeline de Fase 1 hacia el clasificador Bi-LSTM.
   - Corrige el bug histórico del mapeo de carpetas: la carpeta en disco se llama `Normal` (no `NORM`), y separa `LOCA` (rama caliente) de `LOCAC` (rama fría).
   - Selecciona 12 variables de planta normalizadas con `StandardScaler` ajustado únicamente en `train`.
   - Extrae 7 variables de margen térmico (`DNBR`, `TPCT`, `SCMA`, `SCMB`, `TSAT`, `FRCL`, `FRZR`) manteniéndolas en unidades físicas reales.
   - Documenta los conteos de archivos base: NORM (1), LOCA (100), LOCAC (100), ATWS (1), total 202 CSV.
   - Documenta la limitación matemática de NORM: el archivo posee solo 302 filas, por lo que no es posible obtener 3 bloques temporales disjuntos de 150 pasos ($3 \times 150 = 450$).
3. `data_processed/metadata.json`:
   - Estructura JSON canónica consumida por las fases posteriores.

---

## 2. Decisiones Técnicas Adoptadas

### D1: Ubicación Canónica de la Documentación en el Repositorio
- Se ubica en `docs/README_FASE1.md` para formar parte de la documentación estructurada del proyecto, y se enlaza directamente en el `README.md` principal.
- Esto mantiene la separación modular y respeta la estructura del repositorio `gestion_proyectos`.

### D2: Conservación Canónica de `metadata.json`
- Se asegura la existencia de `data_processed/metadata.json` con el esquema canónico completo para que cualquier script de fases posteriores (Fase 2, HMI, calculador de márgenes) disponga de la información exacta sin depender de rutas relativas complejas.

### D3: Doble perspectiva de conteos de muestras
- La documentación expondrá con total claridad las dos modalidades de partición:
  1. *Estrategia de 1 muestra por simulación* (la implementada en `src/preparacion_datos/cli.py`): genera 1 muestra de 150 pasos por archivo, resultando en `train`: 142 (70 LOCA, 70 LOCAC, 1 NORM, 1 ATWS), `val`: 30 (15 LOCA, 15 LOCAC), `test`: 30 (15 LOCA, 15 LOCAC), con advertencia de que NORM y ATWS no tienen val ni test.
  2. *Estrategia de ventaneo en archivos continuos* (la documentada en la referencia de `IA-Nuclear`): divide los archivos únicos de NORM y ATWS en bloques temporales disjuntos con paso deslizante, resultando en `train`: 151, `val`: 34, `test`: 33, con NORM test en 0.
- Esto evita cualquier discrepancia conceptual o ambigüedad entre los miembros del equipo.

