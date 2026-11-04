"""Instante de la falla de cada corrida de evento PWR 3L (research.md §1–§2; solo lectura).

1. ATWS y TRIP_OK: la primera línea del Transient Report con t > 0 que es la acción iniciadora
   (fuente «registro»). Las líneas en t = 0 son la configuración inicial.
2. Si no hay esa línea (LOCA, extracción de barras, falla sin iniciador registrado): el instante
   programado: el retardo de la primera falla de `config.json["fallas"]` distinta de la 8, o el
   número tras `_t` en el nombre de la carpeta (fuente «programado»).
3. Sin ninguna fuente: `t = None` (fuente «ninguna»), incierta.

Es incierta también la corrida en que el validador (el inicio usado en 005) ve cambios más de 2 s
antes del instante de la falla.
"""
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from clasificador_etapa1.config import FAMILIA_DE_CLASE
from clasificador_etapa1.eventos import PATRON_T_CARPETA, inicio_evento
from preparacion_pwr3l.descubrimiento import Corrida, ErrorDatos
from regla_atws.eventos import leer_eventos
from tiempo_deteccion.config import (
    CLASES_CON_REGISTRO,
    FALLA_EXCLUIDA,
    FUENTE_NINGUNA,
    FUENTE_PROGRAMADO,
    FUENTE_REGISTRO,
    PATRON_INICIADOR,
    TOLERANCIA_INCIERTA_S,
)


@dataclass(frozen=True)
class InstanteFalla:
    t: Optional[float]  # s desde el inicio de la corrida
    fuente: str  # «registro», «programado» o «ninguna»
    detalle: str  # línea del registro, «config.json fallas=…» o «carpeta _t60»
    inicio_validador: Optional[float]  # inicio de 005 (validador), para comparar
    incierta: bool
    motivo: Optional[str]  # por qué es incierta


def _carpeta(origen: Path, corrida: Corrida) -> Path:
    return (Path(origen) / corrida.archivo).parent


def _del_registro(origen: Path, corrida: Corrida) -> Optional[Tuple[float, str]]:
    if corrida.clase not in CLASES_CON_REGISTRO:
        return None
    return next(((t, texto) for t, texto in leer_eventos(origen, corrida) if t > 0 and PATRON_INICIADOR.match(texto)), None)


def _programado(origen: Path, corrida: Corrida) -> Optional[Tuple[float, str]]:
    carpeta = _carpeta(origen, corrida)
    configuracion = carpeta / "config.json"
    if configuracion.is_file():
        fallas = (json.loads(configuracion.read_text(encoding="utf-8-sig")).get("fallas") or "").strip()
        campos = [f.split(":") for f in fallas.split(";") if f.strip()]
        iniciadoras = [c for c in campos if c[0].strip() != FALLA_EXCLUIDA and len(c) >= 3]
        if iniciadoras:
            return float(iniciadoras[0][2]), f"config.json fallas={fallas}"
    coincidencia = PATRON_T_CARPETA.search(carpeta.name)
    if coincidencia:
        return float(coincidencia.group(1)), f"carpeta _t{coincidencia.group(1)}"
    return None


def _inicio_validador(origen: Path, corrida: Corrida) -> Optional[float]:
    try:
        return inicio_evento(origen, corrida)
    except ErrorDatos:
        return None


def instante_falla(origen, corrida: Corrida) -> Optional[InstanteFalla]:
    """Instante de la falla de `corrida`; ``None`` si es de operación normal."""
    if FAMILIA_DE_CLASE.get(corrida.clase, "NORM") == "NORM":
        return None
    origen = Path(origen)
    inicio = _inicio_validador(origen, corrida)
    encontrado = _del_registro(origen, corrida)
    fuente = FUENTE_REGISTRO
    if encontrado is None:
        encontrado = _programado(origen, corrida)
        fuente = FUENTE_PROGRAMADO
    if encontrado is None:
        return InstanteFalla(None, FUENTE_NINGUNA, "sin línea del iniciador ni instante programado", inicio, True,
                             "no se conoce el instante de la falla")
    t, detalle = encontrado
    if inicio is not None and inicio < t - TOLERANCIA_INCIERTA_S:
        motivo = (f"el validador ve cambios desde {inicio:g} s, más de {TOLERANCIA_INCIERTA_S:g} s antes "
                  f"de la falla ({t:g} s)")
        return InstanteFalla(t, fuente, detalle, inicio, True, motivo)
    return InstanteFalla(t, fuente, detalle, inicio, False, None)


def instantes_falla(origen, corridas: List[Corrida]) -> Dict[str, InstanteFalla]:
    """Instante de la falla de cada corrida de evento usable."""
    resultado = {}
    for corrida in corridas:
        if corrida.estado != "usable":
            continue
        falla = instante_falla(origen, corrida)
        if falla is not None:
            resultado[corrida.id] = falla
    return resultado
