"""Registro de eventos de PCTran (`*.dat`): señales de disparo e instante del scram."""
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

import numpy as np

from preparacion_pwr3l.descubrimiento import Corrida, ErrorDatos
from regla_atws.config import PUNTO_ALTO_FLUJO, SENALES_DISPARO, TEXTO_SCRAM, TIPO_ALTO_FLUJO

PATRON_EVENTO = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*sec,\s*(.*)$")
Evento = Tuple[float, str]


@dataclass(frozen=True)
class Senal:
    tiempo: float  # s desde el inicio de la corrida
    tipo: str  # normalizado: «low sg level», «turbine trip», «scram high flux», …
    fuente: str  # «registro» (línea del .dat) o «alto flujo» (PWNT ≥ 118 %)


def leer_eventos(origen, corrida: Corrida) -> List[Evento]:
    """Eventos `(t, texto)` del único `*.dat` de la carpeta de la corrida (latin-1, como escribe PCTran)."""
    relativo = corrida.archivo.rsplit("/", 1)[0]
    carpeta = Path(origen) / relativo
    registros = sorted(p for p in carpeta.glob("*.dat") if p.is_file())
    if not registros:
        raise ErrorDatos(relativo, "no hay registro de eventos (.dat)")
    if len(registros) > 1:
        raise ErrorDatos(relativo, "hay más de un registro de eventos (.dat)")
    try:
        texto = registros[0].read_text(encoding="latin-1")
    except OSError as error:
        raise ErrorDatos(f"{relativo}/{registros[0].name}", f"registro ilegible ({error.__class__.__name__})") from None
    eventos = []
    for linea in texto.splitlines():
        coincidencia = PATRON_EVENTO.match(linea)
        if coincidencia:
            eventos.append((float(coincidencia.group(1)), coincidencia.group(2).strip()))
    return eventos


def tipo_senal(texto: str) -> str:
    """Tipo normalizado: sin el valor final (`17.0 %`, `93.4 %`), sin `Control Change…`, en minúsculas."""
    limpio = re.sub(r"\s*Control Change.*$", "", texto).strip()
    limpio = re.sub(r"\s*[\d.]+\s*(%|psia|psig|bar)?\s*$", "", limpio).strip()
    return re.sub(r"\s+", " ", limpio).lower()


def _es_senal(texto: str) -> bool:
    return not texto.startswith(TEXTO_SCRAM) and any(senal in texto for senal in SENALES_DISPARO)


def primera_senal(eventos: Sequence[Evento], pwnt: np.ndarray) -> Optional[Senal]:
    """Primera señal del sistema de protección o primer segundo con PWNT ≥ 118 %, lo que ocurra antes."""
    registro = next((Senal(t, tipo_senal(x), "registro") for t, x in eventos if _es_senal(x)), None)
    altos = np.flatnonzero(np.asarray(pwnt) >= PUNTO_ALTO_FLUJO)
    alto = Senal(float(altos[0]), TIPO_ALTO_FLUJO, "alto flujo") if altos.size else None
    if registro is None or (alto is not None and alto.tiempo < registro.tiempo):
        return alto
    return registro


def instante_scram(eventos: Sequence[Evento]) -> Optional[float]:
    return next((t for t, texto in eventos if texto.startswith(TEXTO_SCRAM)), None)
