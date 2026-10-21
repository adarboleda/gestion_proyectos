"""Armado de los conjuntos y publicación de los artefactos en la carpeta de salida."""
import json
import os
import shutil
import uuid
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

from preparacion_datos.config import (
    CLASES,
    PASO_SEGUNDOS,
    PASOS,
    PROPORCION_TEST,
    PROPORCION_TRAIN,
    PROPORCION_VAL,
    VARIABLES_MARGEN,
    VARIABLES_PLANTA,
)
from preparacion_datos.lectura import Simulacion


def construir_conjunto(simulaciones: List[Simulacion]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Apila las muestras de un conjunto, en el mismo orden que `simulaciones`.

    Devuelve las 12 variables de planta sin escalar (N, 150, 12) float64, los márgenes térmicos
    (N, 150, 7) float64 en sus unidades originales, sin ninguna transformación, y las etiquetas
    (N,) int64.
    """
    n = len(simulaciones)
    planta = len(VARIABLES_PLANTA)
    x = np.empty((n, PASOS, planta), dtype=np.float64)
    margenes = np.empty((n, PASOS, len(VARIABLES_MARGEN)), dtype=np.float64)
    y = np.empty(n, dtype=np.int64)
    for i, simulacion in enumerate(simulaciones):
        x[i] = simulacion.serie[:, :planta]
        margenes[i] = simulacion.serie[:, planta:]
        y[i] = simulacion.etiqueta
    return x, margenes, y


def publicar(salida, archivos: Dict[str, object]) -> None:
    """Escribe todos los archivos en un directorio temporal y luego los mueve a `salida`.

    Un fallo antes de mover deja `salida` sin cambios. Solo se reemplazan los archivos publicados:
    cualquier otro archivo que ya estuviera en `salida` no se toca.
    `archivos` asocia nombre -> arreglo de numpy (se guarda como .npy) o texto/bytes.
    """
    salida = Path(salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    temporal = salida.parent / f".{salida.name}.tmp-{uuid.uuid4().hex[:8]}"
    temporal.mkdir()
    try:
        for nombre, contenido in archivos.items():
            destino = temporal / nombre
            if isinstance(contenido, np.ndarray):
                np.save(destino, contenido)
            elif isinstance(contenido, bytes):
                destino.write_bytes(contenido)
            else:
                destino.write_text(contenido, encoding="utf-8")
        salida.mkdir(exist_ok=True)
        for nombre in archivos:
            os.replace(temporal / nombre, salida / nombre)
    finally:
        shutil.rmtree(temporal, ignore_errors=True)


def construir_metadata(resumen) -> dict:
    """Contenido de metadata.json (ver contracts/salidas.md)."""
    return {
        "version_formato": 1,
        "origen": resumen.origen,
        "semilla": resumen.semilla,
        "proporciones": {"train": PROPORCION_TRAIN, "val": PROPORCION_VAL, "test": PROPORCION_TEST},
        "pasos_por_muestra": PASOS,
        "paso_segundos": PASO_SEGUNDOS,
        "clases": dict(CLASES),
        "variables_planta": list(VARIABLES_PLANTA),
        "variables_margen": list(VARIABLES_MARGEN),
        "conteos_archivos": dict(resumen.conteos_archivos),
        "conteos_muestras": {clase: dict(c) for clase, c in resumen.conteos_muestras.items()},
        "totales": dict(resumen.totales),
        "simulaciones": {conjunto: list(archivos) for conjunto, archivos in resumen.simulaciones.items()},
        "escalador": {
            "ajustado_con": "train",
            "filas_ajuste": resumen.filas_ajuste,
            "variables_sin_varianza": list(resumen.variables_sin_varianza),
        },
        "referencia": dict(resumen.referencia),
        "advertencias": list(resumen.advertencias),
        "limitaciones": list(resumen.limitaciones),
    }


def serializar_metadata(metadata: dict) -> str:
    return json.dumps(metadata, indent=2, ensure_ascii=False) + "\n"
