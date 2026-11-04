"""Línea de órdenes: entrena y evalúa el clasificador de Etapa 2 (rama caliente o fría) de PWR 3L (009)."""
import argparse
import importlib.util
import io
import json
import shutil
import sys
import tempfile
from dataclasses import dataclass, field
from importlib import metadata
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

from clasificador_etapa1.eventos import inicios_evento
from clasificador_etapa1.muestras import Muestras
from clasificador_etapa2.canales import canales_corrida
from clasificador_etapa2.config import (
    ARTEFACTOS,
    CANALES,
    CLASES,
    CONFIRMACION_S,
    HIPERPARAMETROS,
    HORIZONTE_ENTRENAMIENTO_S,
    MEDIA_MOVIL_S,
    SALIDA_POR_DEFECTO,
    SEMILLA,
    UMBRAL,
    VENTANA_PICO_S,
    VENTANA_S,
)
from clasificador_etapa2.muestras import construir_muestras, es_rama
from preparacion_pwr3l.config import CONJUNTOS, ORIGEN_POR_DEFECTO
from preparacion_pwr3l.descubrimiento import Corrida, ErrorDatos
from preparacion_pwr3l.grupos import formar_grupos
from preparacion_pwr3l.lectura import cargar_corridas
from preparacion_pwr3l.particion import repartir
from preparacion_pwr3l.verificacion import ErrorFuga, verificar_reparto


@dataclass(eq=False)
class Ejecucion:
    """Resultado de una ejecución: modelo, muestras de prueba y artefactos listos para publicar."""

    modelo: object
    configuracion: Dict
    corridas_prueba: List[Corrida]
    muestras_prueba: Muestras
    inicios: Dict[str, Optional[float]]
    artefactos: Dict[str, bytes] = field(default_factory=dict)


def _torch_disponible() -> bool:
    return importlib.util.find_spec("torch") is not None


def _tolerar_consolas_limitadas() -> None:
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(errors="replace")
        except (AttributeError, ValueError, OSError):
            pass


def _crear_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="entrenar-etapa2",
        description="Entrena y evalúa el clasificador de Etapa 2 (LOCA rama caliente vs LOCAC rama fría) de PWR 3L.",
    )
    parser.add_argument("--origen", default=ORIGEN_POR_DEFECTO, help="carpeta PWR 3L (solo lectura)")
    parser.add_argument("--salida", default=SALIDA_POR_DEFECTO, help="carpeta donde se publican los artefactos")
    parser.add_argument("--semilla", type=int, default=SEMILLA, help="semilla del reparto y del entrenamiento")
    parser.add_argument("--epocas", type=int, default=HIPERPARAMETROS["epocas"], help="máximo de épocas")
    return parser


def _version() -> str:
    try:
        return metadata.version("preparacion-datos")
    except metadata.PackageNotFoundError:
        return "desconocida"


def entrenar_modelo(origen, semilla: int, epocas: int) -> Ejecucion:
    """Carga corridas, verifica el reparto sin fuga, calcula canales pico, escala con train y entrena."""
    import torch

    from clasificador_etapa2.entrenamiento import (
        ajustar_escalador_canales,
        entrenar,
        escalar_canales,
    )

    corridas = cargar_corridas(origen)
    reparto = repartir(formar_grupos(corridas), semilla)
    verificar_reparto(corridas, reparto)
    inicios = inicios_evento(origen, corridas)

    ramas_por_conjunto = {
        conjunto: [c for c in reparto.corridas[conjunto] if es_rama(c)]
        for conjunto in CONJUNTOS
    }
    todas_ramas = [c for conjunto in CONJUNTOS for c in ramas_por_conjunto[conjunto]]
    canales_brutos = {c.id: canales_corrida(origen, c) for c in todas_ramas}

    x_train = np.stack([canales_brutos[c.id] for c in ramas_por_conjunto["train"]])
    escalador = ajustar_escalador_canales(x_train)
    series = {
        c.id: escalar_canales(escalador, canales_brutos[c.id][None, ...])[0]
        for c in todas_ramas
    }
    muestras = {
        conjunto: construir_muestras(ramas_por_conjunto[conjunto], series, inicios, conjunto == "train")
        for conjunto in CONJUNTOS
    }
    hiperparametros = dict(HIPERPARAMETROS, epocas=epocas)
    resultado = entrenar(muestras["train"], muestras["val"], hiperparametros, semilla)

    configuracion = {
        "clases": list(CLASES),
        "canales": list(CANALES),
        "ventana_s": VENTANA_S,
        "ventana_pico_s": VENTANA_PICO_S,
        "media_movil_s": MEDIA_MOVIL_S,
        "horizonte_entrenamiento_s": HORIZONTE_ENTRENAMIENTO_S,
        "umbral": UMBRAL,
        "confirmacion_s": CONFIRMACION_S,
        "hiperparametros": hiperparametros,
        "semilla": semilla,
        "pesos_clase": [round(float(p), 6) for p in resultado.pesos],
        "escalador": {
            "media": [float(v) for v in escalador.media],
            "escala": [float(v) for v in escalador.escala],
            "filas_ajuste": int(escalador.filas_ajuste),
        },
        "historial": resultado.historial,
        "mejor_epoca": resultado.mejor_epoca,
        "muestras": {conjunto: len(muestras[conjunto]) for conjunto in CONJUNTOS},
        "corridas": {conjunto: [c.id for c in ramas_por_conjunto[conjunto]] for conjunto in CONJUNTOS},
        "version": _version(),
        "entorno": {"torch": torch.__version__, "hilos": torch.get_num_threads()},
    }
    buffer = io.BytesIO()
    torch.save(resultado.modelo.state_dict(), buffer)
    artefactos = {
        "modelo.pt": buffer.getvalue(),
        "modelo.json": json.dumps(configuracion, ensure_ascii=False, indent=2).encode("utf-8"),
    }
    return Ejecucion(
        resultado.modelo,
        configuracion,
        ramas_por_conjunto["test"],
        muestras["test"],
        inicios,
        artefactos,
    )


def agregar_reporte(ejecucion: Ejecucion) -> str:
    """Evalúa sobre prueba, añade `reporte.json` y `reporte.txt` a los artefactos y devuelve el texto."""
    from clasificador_etapa2.evaluacion import evaluar, formatear_reporte

    configuracion = ejecucion.configuracion
    reporte = evaluar(ejecucion.modelo, ejecucion.muestras_prueba, ejecucion.corridas_prueba)
    reporte["entrenamiento"] = {
        "pesos_clase": configuracion["pesos_clase"],
        "mejor_epoca": configuracion["mejor_epoca"],
        "epocas_ejecutadas": len(configuracion["historial"]),
        "f1_validacion": max(h["f1_val"] for h in configuracion["historial"]),
        "muestras": configuracion["muestras"],
        "semilla": configuracion["semilla"],
    }
    reporte["validacion"] = {
        "f1_macro": reporte["entrenamiento"]["f1_validacion"],
        "mejor_epoca": configuracion["mejor_epoca"],
    }
    reporte["reparto"] = {
        conjunto: {
            "corridas": len(configuracion["corridas"][conjunto]),
            "muestras": configuracion["muestras"][conjunto],
        }
        for conjunto in CONJUNTOS
    }
    texto = formatear_reporte(reporte)
    ejecucion.artefactos["reporte.json"] = json.dumps(reporte, ensure_ascii=False, indent=2).encode("utf-8")
    ejecucion.artefactos["reporte.txt"] = texto.encode("utf-8")
    return texto


def publicar(salida, artefactos: Dict[str, bytes]) -> None:
    """Escribe los artefactos en una carpeta temporal y reemplaza solo esos archivos en `salida`."""
    salida = Path(salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    temporal = Path(tempfile.mkdtemp(prefix=f".{salida.name}-", dir=salida.parent))
    try:
        for nombre, contenido in artefactos.items():
            (temporal / nombre).write_bytes(contenido)
        salida.mkdir(exist_ok=True)
        for nombre in artefactos:
            (temporal / nombre).replace(salida / nombre)
    finally:
        shutil.rmtree(temporal, ignore_errors=True)


def main(argv: Optional[List[str]] = None) -> int:
    _tolerar_consolas_limitadas()
    argumentos = _crear_parser().parse_args(argv)
    if not _torch_disponible():
        print(
            'ERROR: falta PyTorch: pip install -e ".[modelo]" '
            "(CPU: --index-url https://download.pytorch.org/whl/cpu)",
            file=sys.stderr,
        )
        return 3
    try:
        ejecucion = entrenar_modelo(argumentos.origen, argumentos.semilla, argumentos.epocas)
        texto = agregar_reporte(ejecucion)
        publicar(argumentos.salida, {n: c for n, c in ejecucion.artefactos.items() if n in ARTEFACTOS})
    except (ErrorDatos, ErrorFuga, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    except OSError as error:
        print(f"ERROR: no se pudo escribir en {argumentos.salida}: {error}", file=sys.stderr)
        return 1
    print(texto, end="")
    return 0

