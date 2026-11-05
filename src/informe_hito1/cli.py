"""Línea de órdenes: informe del Hito 1 (KAN-27) a partir de los resultados de la Fase 2."""
import argparse
import json
import sys
from typing import List, Optional

from informe_hito1.config import FUENTES, SALIDA_POR_DEFECTO
from informe_hito1.consolidar import consolidar
from informe_hito1.fuentes import ErrorFuente, cargar_fuentes
from informe_hito1.informe import formatear_markdown
from preparacion_datos.salida import publicar


def _crear_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="informe-hito1", description="Informe consultivo del Hito 1 (KAN-27).")
    for clave, fuente in FUENTES.items():
        parser.add_argument(f"--{clave}", default=fuente["carpeta"], help=f"resultados de {fuente['kan']} ({fuente['comando']})")
    parser.add_argument("--salida", default=SALIDA_POR_DEFECTO, help="carpeta del informe")
    return parser


def _tolerar_consolas_limitadas() -> None:
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(errors="replace")
        except (AttributeError, ValueError, OSError):
            pass


def main(argv: Optional[List[str]] = None) -> int:
    _tolerar_consolas_limitadas()
    argumentos = _crear_parser().parse_args(argv)
    try:
        datos, fuentes = cargar_fuentes({clave: getattr(argumentos, clave) for clave in FUENTES})
        hito = consolidar(datos)
        hito["fuentes"] = fuentes
        publicar(argumentos.salida, {
            "hito1.json": json.dumps(hito, ensure_ascii=False, indent=2) + "\n",
            "hito1.md": formatear_markdown(hito),
        })
    except ErrorFuente as error:
        print(error, file=sys.stderr)
        return 1
    except (ValueError, KeyError, TypeError) as error:
        print(f"ERROR: formato de resultados inesperado: {error}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"ERROR: no se pudo escribir en {argumentos.salida}: {error}", file=sys.stderr)
        return 1
    print(f"Informe del Hito 1 publicado en {argumentos.salida}/hito1.md (recomendaciones consultivas).")
    return 0
