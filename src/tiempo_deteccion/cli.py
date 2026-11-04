"""Línea de órdenes: mide el tiempo de detección desde la falla en PWR 3L (KAN-25, contracts/cli.md).

cargar → reparto sin fuga (004) → verificar el modelo de 005 → instante de la falla → Etapa 1 segundo a
segundo en validación y prueba → regla de ATWS de 006 (calibrada con entrenamiento) → tiempos, metas y
falsas alarmas → publicar los cuatro archivos juntos → imprimir el reporte.
"""
import argparse
import importlib.util
import sys
from typing import List, Optional

from clasificador_etapa1.config import CONFIRMACION_S, UMBRAL
from preparacion_datos.salida import publicar
from preparacion_pwr3l.config import ORIGEN_POR_DEFECTO, SEMILLA
from preparacion_pwr3l.descubrimiento import ErrorDatos
from preparacion_pwr3l.grupos import formar_grupos
from preparacion_pwr3l.lectura import cargar_corridas
from preparacion_pwr3l.particion import repartir
from preparacion_pwr3l.verificacion import ErrorFuga, verificar_reparto
from regla_atws.cli import construir_casos
from tiempo_deteccion.config import (
    CONJUNTOS_EVALUADOS,
    META_ATWS_S,
    META_DIAGNOSTICO_S,
    MODELO_POR_DEFECTO,
    SALIDA_POR_DEFECTO,
    TOLERANCIA_INCIERTA_S,
)
from tiempo_deteccion.falla import instantes_falla
from tiempo_deteccion.reproduccion import ErrorModelo, verificar_modelo


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
        prog="medir-tiempo-deteccion",
        description="Mide el tiempo de detección desde la falla (Etapa 1 y regla de ATWS) en PWR 3L. Consultivo.",
    )
    parser.add_argument("--origen", default=ORIGEN_POR_DEFECTO, help="carpeta PWR 3L (solo lectura)")
    parser.add_argument("--modelo", default=MODELO_POR_DEFECTO, help="clasificador de Etapa 1 publicado por entrenar-etapa1")
    parser.add_argument("--salida", default=SALIDA_POR_DEFECTO, help="carpeta de resultados")
    parser.add_argument("--semilla", type=int, default=SEMILLA, help="semilla del reparto (la del modelo)")
    return parser


def medir(origen, modelo, semilla: int):
    """Ejecuta la medición completa; devuelve (archivos a publicar, texto del reporte)."""
    from clasificador_etapa1.prediccion import cargar
    from tiempo_deteccion import evaluacion
    from tiempo_deteccion.atws import evaluar_atws
    from tiempo_deteccion.reproduccion import reproducir

    corridas = cargar_corridas(origen)
    if not any(c.estado == "usable" for c in corridas):
        raise ErrorDatos(str(origen), "no hay corridas usables")
    reparto = repartir(formar_grupos(corridas), semilla)
    verificar_reparto(corridas, reparto)
    configuracion_modelo = verificar_modelo(modelo, reparto)
    conjunto_de = {c.id: conjunto for conjunto, lista in reparto.corridas.items() for c in lista}

    fallas = instantes_falla(origen, corridas)
    clasificador = cargar(modelo)
    lineas, evaluadas = {}, []
    for conjunto in CONJUNTOS_EVALUADOS:
        lineas.update(reproducir(clasificador, reparto.corridas[conjunto], conjunto))
        evaluadas += [(c, conjunto) for c in reparto.corridas[conjunto]]

    regla, atws = evaluar_atws(construir_casos(origen, semilla), fallas)
    resultados = evaluacion.resultados_por_corrida(evaluadas, lineas, fallas, atws)
    configuracion = {
        "semilla": semilla,
        "umbral": UMBRAL,
        "confirmacion_s": CONFIRMACION_S,
        "meta_diagnostico_s": META_DIAGNOSTICO_S,
        "meta_atws_s": META_ATWS_S,
        "tolerancia_incierta_s": TOLERANCIA_INCIERTA_S,
        "modelo": {"mejor_epoca": configuracion_modelo.get("mejor_epoca"), "semilla": configuracion_modelo.get("semilla")},
        "regla_atws": {"umbral_pwnt_pct": round(regla.umbral, 6), "espera_s": regla.espera,
                       "retardos_s": regla.retardos, "retardo_por_defecto_s": regla.retardo_por_defecto},
    }
    datos = evaluacion.construir_tiempos(resultados, fallas, conjunto_de, configuracion)
    texto = evaluacion.formatear_reporte(datos)
    archivos = {
        "tiempos.json": evaluacion.serializar_json(datos),
        "tiempos.csv": evaluacion.serializar_tiempos_csv(datos),
        "lineas_tiempo.csv": evaluacion.serializar_lineas_csv(lineas, [r.corrida for r in resultados], atws),
        "reporte.txt": texto,
    }
    return archivos, texto


def main(argv: Optional[List[str]] = None) -> int:
    _tolerar_consolas_limitadas()
    argumentos = _crear_parser().parse_args(argv)
    if not _torch_disponible():
        print('ERROR: falta PyTorch: pip install -e ".[modelo]" '
              "(CPU: --index-url https://download.pytorch.org/whl/cpu)", file=sys.stderr)
        return 3
    try:
        archivos, texto = medir(argumentos.origen, argumentos.modelo, argumentos.semilla)
        publicar(argumentos.salida, archivos)
    except (ErrorDatos, ErrorFuga, ErrorModelo) as error:
        print(error, file=sys.stderr)
        return 1
    except ValueError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"ERROR: no se pudo escribir en {argumentos.salida}: {error}", file=sys.stderr)
        return 1
    print(texto, end="")
    return 0
