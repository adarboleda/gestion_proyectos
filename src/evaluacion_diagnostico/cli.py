"""Línea de órdenes: evalúa el diagnóstico con matriz de confusión, abstenciones y validación cruzada."""
import argparse
import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import numpy as np

from evaluacion_diagnostico.config import (
    ARTEFACTOS,
    K_FOLDS_DEFAULT,
    SALIDA_POR_DEFECTO,
    SEMILLA_DEFAULT,
    UMBRAL_DEFAULT,
)
from evaluacion_diagnostico.metricas import metricas_conjuntas
from evaluacion_diagnostico.reporte import construir_reporte_json, formatear_reporte_texto
from evaluacion_diagnostico.validacion_cruzada import ejecutar_kfold
from preparacion_pwr3l.config import CONJUNTOS, ORIGEN_POR_DEFECTO, VARIABLES_ENTRADA
from preparacion_pwr3l.descubrimiento import ErrorDatos
from preparacion_pwr3l.escalado import ajustar_escalador, aplicar
from preparacion_pwr3l.grupos import formar_grupos
from preparacion_pwr3l.lectura import cargar_corridas
from preparacion_pwr3l.particion import repartir
from preparacion_pwr3l.verificacion import ErrorFuga, verificar_reparto


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
        prog="evaluar-diagnostico",
        description="Evalúa el diagnóstico de Fase 2 reportando exactitud con abstención, matriz 3x4 y Group K-Fold.",
    )
    parser.add_argument("--origen", default=ORIGEN_POR_DEFECTO, help="carpeta del dataset PWR 3L (solo lectura)")
    parser.add_argument("--salida", default=SALIDA_POR_DEFECTO, help="carpeta de destino para los reportes")
    parser.add_argument("--modelo", default=None, help="ruta a carpeta o archivo del modelo entrenado")
    parser.add_argument("--k", type=int, default=K_FOLDS_DEFAULT, help="número de particiones de validación cruzada")
    parser.add_argument("--semilla", type=int, default=SEMILLA_DEFAULT, help="semilla para partición y reproducibilidad")
    parser.add_argument("--epocas", type=int, default=5, help="épocas por fold para entrenamiento")
    parser.add_argument("--umbral", type=float, default=UMBRAL_DEFAULT, help="umbral de confianza para abstención")
    return parser


def ejecutar_evaluacion_completa(
    origen: Union[str, Path] = ORIGEN_POR_DEFECTO,
    modelo_ruta: Optional[Union[str, Path]] = None,
    k: int = K_FOLDS_DEFAULT,
    semilla: int = SEMILLA_DEFAULT,
    epocas: int = 5,
    umbral: float = UMBRAL_DEFAULT,
) -> Tuple[Dict, Dict, Dict]:
    """Ejecuta el flujo completo de evaluación: validación, prueba y validación cruzada."""
    import torch
    from clasificador_etapa1.config import HIPERPARAMETROS
    from clasificador_etapa1.entrenamiento import entrenar, predecir
    from clasificador_etapa1.eventos import inicios_evento
    from clasificador_etapa1.modelo import BiLSTMEtapa1
    from clasificador_etapa1.muestras import construir_muestras
    from clasificador_etapa1.prediccion import cargar

    corridas = cargar_corridas(origen)
    reparto = repartir(formar_grupos(corridas), semilla)
    verificar_reparto(corridas, reparto)
    inicios = inicios_evento(origen, corridas)

    x_train = np.stack([c.serie[:, : len(VARIABLES_ENTRADA)] for c in reparto.corridas["train"]])
    escalador = ajustar_escalador(x_train)
    usables = [c for conjunto in CONJUNTOS for c in reparto.corridas[conjunto]]
    series = {c.id: aplicar(escalador, c.serie[None, :, : len(VARIABLES_ENTRADA)])[0] for c in usables}

    m_train = construir_muestras(reparto.corridas["train"], series, inicios, entrenamiento=True)
    m_val = construir_muestras(reparto.corridas["val"], series, inicios, entrenamiento=False)
    m_test = construir_muestras(reparto.corridas["test"], series, inicios, entrenamiento=False)

    modelo = None
    if modelo_ruta:
        p_mod = Path(modelo_ruta)
        if (p_mod / "modelo.pt").is_file() and (p_mod / "modelo.json").is_file():
            clasif = cargar(p_mod)
            modelo = clasif.modelo
        elif p_mod.is_file():
            hp = dict(HIPERPARAMETROS)
            modelo = BiLSTMEtapa1(
                entradas=len(VARIABLES_ENTRADA),
                unidades=hp["unidades"],
                capas=hp["capas"],
                dropout=hp["dropout"],
            )
            modelo.load_state_dict(torch.load(p_mod, weights_only=True))
            modelo.eval()

    if modelo is None:
        hp = dict(HIPERPARAMETROS, epocas=epocas)
        res_entrenamiento = entrenar(m_train, m_val, hp, semilla=semilla)
        modelo = res_entrenamiento.modelo

    probs_val = predecir(modelo, m_val.x)
    probs_test = predecir(modelo, m_test.x)

    val_metrics = metricas_conjuntas(m_val.y, probs_val, umbral=umbral)
    test_metrics = metricas_conjuntas(m_test.y, probs_test, umbral=umbral)

    cv_summary = ejecutar_kfold(
        corridas=usables,
        inicios=inicios,
        k=k,
        semilla=semilla,
        umbral=umbral,
        epocas=epocas,
    )

    return val_metrics, test_metrics, cv_summary


def publicar(salida: Union[str, Path], artefactos: Dict[str, bytes]) -> None:
    """Escribe los artefactos atómicamente en `salida`."""
    salida = Path(salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    temporal = Path(tempfile.mkdtemp(prefix=f".{salida.name}-", dir=salida.parent))
    try:
        for nombre, contenido in artefactos.items():
            (temporal / nombre).write_bytes(contenido)
        salida.mkdir(parents=True, exist_ok=True)
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
        val_m, test_m, cv_s = ejecutar_evaluacion_completa(
            origen=argumentos.origen,
            modelo_ruta=argumentos.modelo,
            k=argumentos.k,
            semilla=argumentos.semilla,
            epocas=argumentos.epocas,
            umbral=argumentos.umbral,
        )

        reporte_dict = construir_reporte_json(val_m, test_m, cv_s, umbral=argumentos.umbral)
        reporte_texto = formatear_reporte_texto(reporte_dict)

        artefactos_bytes = {
            "evaluacion_diagnostico.json": json.dumps(reporte_dict, ensure_ascii=False, indent=2).encode("utf-8"),
            "evaluacion_diagnostico.txt": reporte_texto.encode("utf-8"),
        }
        publicar(argumentos.salida, artefactos_bytes)

    except (ErrorDatos, ErrorFuga, ValueError, FileNotFoundError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"ERROR: no se pudo escribir en {argumentos.salida}: {error}", file=sys.stderr)
        return 1

    print(reporte_texto, end="")
    return 0
