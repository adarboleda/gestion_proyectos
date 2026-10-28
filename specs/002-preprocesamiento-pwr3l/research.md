# Research: Preprocesamiento PWR 3L en ventanas de 300 s y cinco clases

**Fecha**: 2026-10-28 · **Spec**: [spec.md](spec.md) · **Plan**: [plan.md](plan.md)

Medición previa de la carpeta real `D:\Proyectos\IA-Nuclear\PWR 3L` (script de exploración, no versionado): 110 archivos de datos en 109 carpetas de corrida (R27 tiene dos), 93 columnas en todos, `TIME` de 0 en pasos exactos de 1 s, sin valores faltantes ni tiempos repetidos. 98 archivos tienen 300 o 301 filas; 12 tienen entre 289 y 299 (9 de clases de entrenamiento y 3 OOD).

## 1. Paquete propio para PWR 3L

- **Decisión**: paquete `preparacion_pwr3l`, comando `preparar-pwr3l` y salida `data_processed_pwr3l/`, independientes de `preparacion_datos` (001). Solo se importa `preparacion_datos.salida.publicar`.
- **Razón**: el principio IV prohíbe mezclar plantas; tener variables, pasos y clases de cada planta en paquetes separados lo hace evidente y evita que un cambio en uno altere el otro. `publicar` no sabe nada de NPPAD (recibe nombres y contenidos).
- **Alternativas**: parametrizar 001 con un «perfil de planta» (más acoplamiento y riesgo de romper 001); copiar `publicar` (duplicación de la parte más delicada, ya probada en 001).

## 2. Descubrimiento de corridas

- **Decisión**: en la raíz se reconocen las carpetas de clase `ATWS`, `LOCA COLD`, `LOCA HOT`, `LOCA PORV`, `NORM`, `TRIP_OK` y `auto`. Se ignoran los archivos sueltos y las carpetas que empiezan por `_` o `.`; cualquier otra carpeta detiene la preparación («carpeta no reconocida»). Dentro de cada carpeta de clase, cada subcarpeta es una corrida; su identificador es el prefijo `R<n>[letra]` del nombre. En `auto`, el nombre debe ser `R<n>[letra]_<CLASE>` con `CLASE` en {NORM, LOCA, LOCAC, ATWS, TRIP_OK, OOD}; las subcarpetas que empiezan por `_` se ignoran.
- **Archivo de datos**: en las corridas manuales, el único archivo cuyo nombre contiene `plotdata` (sin distinguir mayúsculas) con extensión `.csv`, `.xls` o `.xlsx`; en `auto`, `plotdata.csv`. Cero o más de uno detiene la preparación.
- **Razón**: es la estructura documentada del dataset; ser estricto evita perder corridas en silencio.
- **Orden**: por etiqueta de clase y luego por número de corrida (`R7` < `R07b` < `R10` < `R100`), de modo que el resultado no depende del orden del sistema de archivos.

## 3. Corridas descartadas y OOD

- **Decisión**: lista fija en `config.py`, con motivo: R07 (estado inicial inestable; el validador la marcó «REPETIR» y se repitió como R07b), R27 (intento de mitigación manual, dos tramos FAILED/mitigation), R28 (intento de boración). Fuente: `docs/PLAN_DATASET_PWR3L_DETECCION_RAPIDA.md` §3.1 de IA-Nuclear. Las descartadas y las OOD se identifican sin leer sus datos (R27 tiene dos archivos y no debe disparar el error de «más de un archivo»).
- **Razón**: FR-003, FR-004 y la tercera aclaración. Una lista explícita es auditable; deducirla del validador externo acoplaría este paquete a otro proyecto.

## 4. Lectura de los dos formatos

- **Decisión**: CSV con `pandas.read_csv(float_precision="round_trip")`; `.xls` y `.xlsx` con `pandas.read_excel(engine="openpyxl")` (los `.xls` de PCTran son libros xlsx; el motor se fuerza porque la extensión engaña a pandas). Nueva dependencia: `openpyxl`.
- **Razón**: `round_trip` hace que el valor leído sea exactamente el del texto (SC-004), igual que la corrección I1 de 001. En los libros de Excel el valor numérico de la celda ya es el del archivo.

## 5. Validación del archivo completo

- **Decisión**: antes de recortar, se valida todo el archivo: columnas requeridas (`TIME` + 26 de entrada + 7 de margen), valores numéricos, no faltantes y finitos en todas las filas de esas columnas, y `TIME` igual a 0, 1, 2, … sin huecos (paso de 1 s). Cualquier defecto lanza `ErrorDatos` con el archivo relativo, la causa y la variable. Solo después se mira la longitud: menos de 300 filas → corrida «corta», excluida con aviso (FR-006); 300 o más → se toman las filas 0–299.
- **Razón**: FR-014 exige detenerse ante defectos en cualquier parte del archivo (lección F5 de 001), y la primera aclaración distingue «defectuosa» (se detiene) de «corta» (se excluye). Un archivo corto y defectuoso se trata como defectuoso.

## 6. Variables de entrada y márgenes

- **Decisión**: 26 entradas medibles, en este orden: `P, TAVG, THA, THB, TCA, TCB, WRCA, WRCB, LVPZ, LVCR, PWNT, PSGA, PSGB, NSGA, NSGB, WFWA, WFWB, WSTA, WSTB, TBLD, WHPI, WCHG, WECS, PRB, TRB, RM1` (las del canal rápido de IA-Nuclear y del plan del dataset §3.2). 7 márgenes: `DNBR, TPCT, SCMA, SCMB, TSAT, FRCL, FRZR` (mismos que 001).
- **Razón**: FR-009. `WLR` (caudal de fuga) salta de 0 a decenas de miles de t/h en el primer segundo de un LOCA y no se mide en planta: con ella la clasificación sería trivial. Tampoco entran `PWR` (calorimétrica, lenta), reactividades ni `WBK`.
- **Alternativa descartada**: las 12 variables de 001 (incluyen `WLR` y `PWR` y omiten el secundario, clave para distinguir ATWS de TRIP_OK).

## 7. Grupos de corridas emparejadas

- **Decisión**: (a) gemelas ATWS/TRIP_OK según una tabla fija de 19 pares en `config.py` (R21–R59, R22–R60, R23–R61, R24–R62, R29–R63, R26–R53, R47–R54, R48–R55, R49–R56, R50–R57, R51–R58, R91–R99, R92–R100, R93–R101, R94–R102, R95–R103, R96–R104, R97–R105, R98–R106); (b) LOCA y LOCAC por área de rotura: el número antes de `cm` en el nombre de la carpeta (manuales, p. ej. `R10_LOCA_hot_50cm_t60` → 50) o en la `descripcion` de `config.json` (automáticas, p. ej. «LOCA rama fría 500 cm2» → 500); (c) el resto, un grupo por corrida. Claves: `AREA-<cm2>`, `GEMELAS-<Ra>-<Rb>`, `<Rid>`.
- **Razón**: FR-008 y la segunda aclaración. La tabla de gemelas viene de `plan_corridas_pwr3l.csv` de IA-Nuclear; las automáticas la repiten en `config.json` (`gemelo_de`) y la prueba con la carpeta real lo verifica. Las manuales R59–R63 no tienen `config.json`, por eso la tabla es la fuente.
- **Consecuencia**: si una gemela no aporta muestra (corta), la otra queda sola en su grupo; no hay fuga posible porque la ausente no está en ningún conjunto.

## 8. Reparto de grupos

- **Decisión**: los grupos se separan en tres familias (NORM; LOCA+LOCAC; ATWS+TRIP_OK). En cada familia, los grupos se ordenan por clave, se barajan con `numpy.random.default_rng(semilla)` y se asignan uno a uno al conjunto con mayor déficit respecto de su meta (0.70 · n, 0.15 · n, 0.15 · n corridas de la familia), con desempate train → val → test. Semilla por defecto: 42.
- **Razón**: con grupos de tamaño distinto (de 1 a 8 corridas) no se puede cortar exactamente 70/15/15; el déficit da el reparto más cercano sin partir grupos. Trabajar por familia evita que, por ejemplo, todos los NORM caigan en entrenamiento. El resultado no depende del orden de entrada.
- **Alternativas**: `GroupShuffleSplit` de scikit-learn (no garantiza proporciones con grupos desiguales ni estratifica); reparto por clase (rompería los grupos que mezclan LOCA y LOCAC o ATWS y TRIP_OK).

## 9. Escalado

- **Decisión**: `StandardScaler` ajustado con las filas de `X_train` aplanadas (N·300, 26) en float64 y aplicado a los tres conjuntos; se guardan media y escala (26,). Las variables sin variación en entrenamiento quedan con escala 1 (comportamiento de scikit-learn) y se informan.
- **Razón**: FR-010, igual que 001. La normalización respecto al estado inicial (plan del dataset §3.3) es ingeniería de características del clasificador y queda para su iteración.

## 10. Salida y publicación

- **Decisión**: `X_<conjunto>.npy` (N, 300, 26) float32, `y_<conjunto>.npy` (N,) int64, `margins_<conjunto>.npy` (N, 300, 7) float64, `scaler_mean.npy` y `scaler_std.npy` (26,) float64 y `metadata.json`, publicados con `publicar` (todos o ninguno). `data_processed_pwr3l/` se añade a `.gitignore`.
- **Razón**: mismo contrato que 001 para que el entrenamiento posterior los cargue igual; el orden de las filas se documenta en `metadata.json` (`corridas[conjunto]`).

## 11. Sin comparación con una referencia

- **Decisión**: no hay opción `--referencia`. La salida previa de IA-Nuclear (`data_processed_pwr3l/`) es por paso, con 108 características derivadas y cuatro clases; sus conteos no son comparables.
- **Razón**: una comparación que siempre «difiere» no informa nada. Códigos de salida: 0 (éxito) y 1 (error de datos o de escritura).

## 12. Tolerancia de consola

- **Decisión**: igual que 001 (decisión 12 de su research), `sys.stdout`/`sys.stderr` se reconfiguran con `errors="replace"` para que un carácter no representable en la consola de Windows no corte el reporte.
