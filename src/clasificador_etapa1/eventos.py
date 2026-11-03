"""Instante de inicio del evento de cada corrida PWR 3L (solo lectura).

Fuentes, en orden: `validacion.json` de la carpeta de la corrida (automáticas), la fila de la
corrida en `validacion_corridas.csv` (manuales; se ignoran las filas `[mitigation]`) y el número
tras `_t` en el nombre de la carpeta (instante planificado). Las corridas NORM no tienen inicio.
"""
import csv
import json
import re
from pathlib import Path
from typing import Dict, List, Optional

from clasificador_etapa1.config import FAMILIA_DE_CLASE
from preparacion_pwr3l.descubrimiento import Corrida, ErrorDatos

PATRON_ID_FILA = re.compile(r"^(R\d+[a-z]?)(?=$|[_\s])")
PATRON_T_CARPETA = re.compile(r"_t(\d+(?:\.\d+)?)(?=$|_)")


def _leer_tabla_validacion(origen: Path) -> Dict[str, float]:
    ruta = Path(origen) / "validacion_corridas.csv"
    if not ruta.is_file():
        return {}
    tabla: Dict[str, float] = {}
    with open(ruta, encoding="utf-8-sig", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            nombre = (fila.get("corrida") or "").strip()
            coincidencia = PATRON_ID_FILA.match(nombre)
            valor = (fila.get("t_inicio_real") or "").strip()
            if not coincidencia or not valor or "[mitigation]" in nombre:
                continue
            tabla.setdefault(coincidencia.group(1), float(valor))
    return tabla


def _inicio(origen: Path, corrida: Corrida, tabla: Dict[str, float]) -> Optional[float]:
    if FAMILIA_DE_CLASE.get(corrida.clase) == "NORM":
        return None
    carpeta = (Path(origen) / corrida.archivo).parent
    validacion = carpeta / "validacion.json"
    if validacion.is_file():
        valor = json.loads(validacion.read_text(encoding="utf-8-sig")).get("t_inicio_real")
        if valor is not None:
            return float(valor)
    if corrida.id in tabla:
        return tabla[corrida.id]
    coincidencia = PATRON_T_CARPETA.search(carpeta.name)
    if coincidencia:
        return float(coincidencia.group(1))
    raise ErrorDatos(corrida.archivo, "no se conoce el instante de inicio del evento")


def inicio_evento(origen, corrida: Corrida) -> Optional[float]:
    """Inicio del evento de `corrida` en segundos; ``None`` si es NORM; ``ErrorDatos`` si no se conoce."""
    return _inicio(Path(origen), corrida, _leer_tabla_validacion(Path(origen)))


def inicios_evento(origen, corridas: List[Corrida]) -> Dict[str, Optional[float]]:
    """Inicio del evento de cada corrida usable de las cinco clases."""
    origen = Path(origen)
    tabla = _leer_tabla_validacion(origen)
    return {
        c.id: _inicio(origen, c, tabla)
        for c in corridas
        if c.estado == "usable" and c.clase in FAMILIA_DE_CLASE
    }
