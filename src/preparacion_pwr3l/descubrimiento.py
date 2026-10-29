"""Descubrimiento de las corridas de la carpeta PWR 3L (solo lectura; no lee los datos de planta)."""
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple

import numpy as np

from preparacion_pwr3l.config import (
    CARPETA_AUTO,
    CARPETAS_MANUALES,
    CLASE_OOD,
    CLASES,
    CLASES_AUTO,
    CLASES_CON_AREA,
    DESCARTADAS,
    GEMELAS,
)

PATRON_ID = re.compile(r"^(R\d+[a-z]?)(?=$|[_\s])")
PATRON_AUTO = re.compile(r"^(R\d+[a-z]?)_(.+)$")
PATRON_AREA = re.compile(r"(\d+)\s*cm", re.IGNORECASE)
EXTENSIONES_DATOS = (".csv", ".xls", ".xlsx")
GEMELA_DE = {a: b for par in GEMELAS for a, b in (par, par[::-1])}


class ErrorDatos(Exception):
    """Archivo o carpeta de origen defectuosa: nombra la ruta y la causa."""

    def __init__(self, archivo: str, causa: str, variable: Optional[str] = None):
        self.archivo = archivo
        self.causa = causa
        self.variable = variable
        mensaje = f"ERROR: {archivo}: {causa}"
        if variable:
            mensaje += f" [variable {variable}]"
        super().__init__(mensaje)


@dataclass(eq=False)
class Corrida:
    id: str
    clase: str
    origen: str  # "manual" o "auto"
    archivo: str  # archivo de datos relativo al origen; la carpeta si es descartada u OOD
    area: Optional[int] = None  # cm², solo LOCA y LOCAC
    gemela: Optional[str] = None
    estado: str = "pendiente"  # pendiente -> usable | corta; o descartada | ood
    filas: Optional[int] = None
    serie: Optional[np.ndarray] = None  # (300, 33): 26 entradas y 7 márgenes

    @property
    def etiqueta(self) -> Optional[int]:
        return CLASES.get(self.clase)


def clave_id(identificador: str) -> Tuple[int, str]:
    """Orden natural de los identificadores: R7 < R07b < R10 < R100."""
    coincidencia = re.match(r"^R(\d+)([a-z]?)$", identificador)
    return int(coincidencia.group(1)), coincidencia.group(2)


def clave_orden(corrida: Corrida):
    etiqueta = corrida.etiqueta
    return (len(CLASES) if etiqueta is None else etiqueta, clave_id(corrida.id))


def _ignorada(nombre: str) -> bool:
    return nombre.startswith(("_", "."))


def _subcarpetas(carpeta: Path) -> List[Path]:
    return sorted((p for p in carpeta.iterdir() if p.is_dir() and not _ignorada(p.name)), key=lambda p: p.name)


def _area(*textos: str) -> Optional[int]:
    for texto in textos:
        coincidencia = PATRON_AREA.search(texto or "")
        if coincidencia:
            return int(coincidencia.group(1))
    return None


def _completar(corrida: Corrida, relativo: str, archivos: List[Path], textos: List[str]) -> Corrida:
    """Marca descartadas y OOD o fija el archivo de datos, el área y la gemela."""
    if corrida.id in DESCARTADAS:
        corrida.estado = "descartada"
        return corrida
    if corrida.clase == CLASE_OOD:
        corrida.estado = "ood"
        return corrida
    if not archivos:
        raise ErrorDatos(relativo, "no hay archivo de datos")
    if len(archivos) > 1:
        raise ErrorDatos(relativo, "hay más de un archivo de datos")
    corrida.archivo = f"{relativo}/{archivos[0].name}"
    if corrida.clase in CLASES_CON_AREA:
        corrida.area = _area(*textos)
        if corrida.area is None:
            raise ErrorDatos(relativo, "no se pudo determinar el área de rotura")
    corrida.gemela = GEMELA_DE.get(corrida.id)
    return corrida


def _descubrir_manuales(carpeta_clase: Path, clase: str) -> Iterator[Corrida]:
    for carpeta in _subcarpetas(carpeta_clase):
        relativo = f"{carpeta_clase.name}/{carpeta.name}"
        coincidencia = PATRON_ID.match(carpeta.name)
        if not coincidencia:
            raise ErrorDatos(relativo, "nombre de corrida no reconocido")
        archivos = sorted(
            (
                p for p in carpeta.iterdir()
                if p.is_file() and "plotdata" in p.name.lower() and p.suffix.lower() in EXTENSIONES_DATOS
            ),
            key=lambda p: p.name,
        )
        corrida = Corrida(coincidencia.group(1), clase, "manual", relativo)
        yield _completar(corrida, relativo, archivos, [carpeta.name])


def _leer_configuracion(carpeta: Path, relativo: str) -> Dict:
    ruta = carpeta / "config.json"
    if not ruta.is_file():
        return {}
    try:
        return json.loads(ruta.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as error:
        raise ErrorDatos(f"{relativo}/config.json", f"archivo ilegible ({error.__class__.__name__})") from None


def _descubrir_automaticas(carpeta_auto: Path) -> Iterator[Corrida]:
    for carpeta in _subcarpetas(carpeta_auto):
        relativo = f"{carpeta_auto.name}/{carpeta.name}"
        coincidencia = PATRON_AUTO.match(carpeta.name)
        if not coincidencia:
            raise ErrorDatos(relativo, "nombre de corrida no reconocido")
        identificador, clase = coincidencia.groups()
        if clase not in CLASES_AUTO:
            raise ErrorDatos(relativo, f"clase desconocida ({clase})")
        corrida = Corrida(identificador, clase, "auto", relativo)
        datos = carpeta / "plotdata.csv"
        archivos = [datos] if datos.is_file() else []
        configuracion = _leer_configuracion(carpeta, relativo) if corrida.id not in DESCARTADAS else {}
        corrida = _completar(corrida, relativo, archivos, [carpeta.name, str(configuracion.get("descripcion", ""))])
        declarada = str(configuracion.get("gemelo_de") or "").strip()
        if corrida.estado == "pendiente" and declarada and declarada != corrida.gemela:
            raise ErrorDatos(
                f"{relativo}/config.json",
                f"la gemela declarada en config.json ({declarada}) no coincide con la tabla ({corrida.gemela or 'ninguna'})",
            )
        yield corrida


def descubrir_corridas(origen) -> List[Corrida]:
    """Lista todas las corridas de `origen` sin leer sus datos de planta.

    Orden: por etiqueta de clase (OOD al final) y por número de corrida.
    """
    origen = Path(origen)
    if not origen.is_dir():
        raise ErrorDatos(str(origen), "no existe la carpeta de origen")
    corridas: List[Corrida] = []
    for carpeta in _subcarpetas(origen):
        if carpeta.name == CARPETA_AUTO:
            corridas.extend(_descubrir_automaticas(carpeta))
        elif carpeta.name in CARPETAS_MANUALES:
            corridas.extend(_descubrir_manuales(carpeta, CARPETAS_MANUALES[carpeta.name]))
        else:
            raise ErrorDatos(carpeta.name, "carpeta no reconocida")
    vistas: Dict[str, Corrida] = {}
    for corrida in corridas:
        if corrida.id in vistas:
            raise ErrorDatos(
                corrida.archivo, f"identificador de corrida repetido (también en {vistas[corrida.id].archivo})"
            )
        vistas[corrida.id] = corrida
    for clase in CLASES:
        if not any(c.clase == clase for c in corridas):
            raise ErrorDatos(str(origen), f"no hay corridas de la clase {clase}")
    return sorted(corridas, key=clave_orden)
