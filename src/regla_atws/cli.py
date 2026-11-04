"""Línea de órdenes: calibra y evalúa la regla determinista de ATWS con PWR 3L (KAN-22)."""
import argparse
import csv
import io
import json
import sys
from typing import List, Optional

from preparacion_datos.salida import publicar
from preparacion_pwr3l.config import CONJUNTOS, ORIGEN_POR_DEFECTO, SEMILLA, VARIABLES_ENTRADA
from preparacion_pwr3l.descubrimiento import ErrorDatos
from preparacion_pwr3l.grupos import formar_grupos
from preparacion_pwr3l.lectura import cargar_corridas
from preparacion_pwr3l.particion import repartir
from preparacion_pwr3l.verificacion import ErrorFuga, verificar_reparto
from regla_atws.config import AVISO, META_S, PUNTO_ALTO_FLUJO, SALIDA_POR_DEFECTO
from regla_atws.eventos import instante_scram, leer_eventos, primera_senal
from regla_atws.regla import Caso, Regla, calibrar, evaluar_todas
from regla_atws.reporte import formatear_reporte, resumir, serializar_resumen

INDICE_PWNT = VARIABLES_ENTRADA.index("PWNT")
COLUMNAS_CSV = [
    "id", "clase", "conjunto", "es_atws", "tipo_senal", "fuente_senal", "t_senal", "retardo", "retardo_por_defecto",
    "t_demanda", "t_decision", "pwnt_decision_pct", "recomendacion", "motivo", "acierto",
    "t_deteccion_demanda", "t_deteccion_senal",
]


def _crear_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="evaluar-regla-atws",
        description="Calibra con entrenamiento y evalúa la regla determinista de ATWS (recomendación consultiva).",
    )
    parser.add_argument("--origen", default=ORIGEN_POR_DEFECTO, help="carpeta PWR 3L (solo lectura)")
    parser.add_argument("--salida", default=SALIDA_POR_DEFECTO, help="carpeta de resultados")
    parser.add_argument("--semilla", type=int, default=SEMILLA, help="semilla del reparto (la de 004)")
    return parser


def _tolerar_consolas_limitadas() -> None:
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(errors="replace")
        except (AttributeError, ValueError, OSError):
            pass


def construir_casos(origen, semilla: int) -> List[Caso]:
    """Casos de todas las corridas usables, en el orden de 004 (train, val, test)."""
    corridas = cargar_corridas(origen)
    if not any(c.estado == "usable" for c in corridas):
        raise ErrorDatos(str(origen), "no hay corridas usables")
    reparto = repartir(formar_grupos(corridas), semilla)
    verificar_reparto(corridas, reparto)
    casos = []
    for conjunto in CONJUNTOS:
        for corrida in reparto.corridas[conjunto]:
            eventos = leer_eventos(origen, corrida)
            pwnt = corrida.serie[:, INDICE_PWNT]
            casos.append(Caso(corrida, conjunto, primera_senal(eventos, pwnt), instante_scram(eventos), pwnt))
    return casos


def _numero(valor) -> str:
    if valor is None:
        return ""
    if isinstance(valor, bool):
        return str(valor)
    if isinstance(valor, float):
        return f"{valor:.4f}"
    return str(valor)


def serializar_evaluacion(resultados) -> str:
    salida = io.StringIO()
    escritor = csv.writer(salida, lineterminator="\n")
    escritor.writerow(COLUMNAS_CSV)
    for r in resultados:
        escritor.writerow([
            r.id, r.clase, r.conjunto, r.es_atws, r.tipo_senal or "", r.fuente_senal or "", _numero(r.t_senal),
            _numero(r.retardo), r.retardo_por_defecto, _numero(r.t_demanda), _numero(r.t_decision),
            _numero(r.pwnt_decision), r.recomendacion, r.motivo, r.acierto,
            _numero(r.t_deteccion_demanda), _numero(r.t_deteccion_senal),
        ])
    return salida.getvalue()


def serializar_regla(regla: Regla, semilla: int) -> str:
    contenido = {
        "version_formato": 1,
        "calibrada_con": "train",
        "semilla": semilla,
        "umbral_pwnt_pct": round(regla.umbral, 6),
        "espera_s": regla.espera,
        "punto_alto_flujo_pct": PUNTO_ALTO_FLUJO,
        "meta_s": META_S,
        "retardos_s": regla.retardos,
        "retardo_por_defecto_s": regla.retardo_por_defecto,
        "margen": {
            "minimo_atws_pct": round(regla.minimo_atws, 6),
            "maximo_no_atws_pct": round(regla.maximo_no_atws, 6),
            "separacion_pct": round(regla.minimo_atws - regla.maximo_no_atws, 6),
            "solape": regla.solape,
            "falsas_alarmas_entrenamiento": regla.falsas_alarmas_entrenamiento,
        },
        "aviso": AVISO,
    }
    return json.dumps(contenido, indent=2, ensure_ascii=False) + "\n"


def main(argv: Optional[List[str]] = None) -> int:
    _tolerar_consolas_limitadas()
    argumentos = _crear_parser().parse_args(argv)
    try:
        casos = construir_casos(argumentos.origen, argumentos.semilla)
        regla = calibrar([c for c in casos if c.conjunto == "train"])
        resultados = evaluar_todas(regla, casos)
        archivos = {
            "regla.json": serializar_regla(regla, argumentos.semilla),
            "evaluacion.csv": serializar_evaluacion(resultados),
        }
        resumen = resumir(resultados, regla)
        archivos["resumen.json"] = serializar_resumen(resumen)
        publicar(argumentos.salida, archivos)
    except (ErrorDatos, ErrorFuga) as error:
        print(error, file=sys.stderr)
        return 1
    except ValueError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"ERROR: no se pudo escribir en {argumentos.salida}: {error}", file=sys.stderr)
        return 1
    print(formatear_reporte(argumentos.origen, argumentos.semilla, regla, resumen, resultados, sorted(archivos)), end="")
    return 0
