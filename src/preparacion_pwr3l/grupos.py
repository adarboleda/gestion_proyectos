"""Grupos de corridas PWR 3L que deben ir siempre al mismo conjunto (sin fuga de datos)."""
from dataclasses import dataclass, field
from typing import Dict, List

from preparacion_pwr3l.config import CLASES, CLASES_CON_AREA, FAMILIAS
from preparacion_pwr3l.descubrimiento import Corrida, ErrorDatos, clave_id, clave_orden

ORDEN_FAMILIAS = ("NORM", "LOCA", "ATWS")


@dataclass(eq=False)
class Grupo:
    clave: str  # AREA-<cm2>, GEMELAS-<a>-<b> o <Rid>
    familia: str  # NORM, LOCA o ATWS
    corridas: List[Corrida] = field(default_factory=list)

    @property
    def tamano(self) -> int:
        return len(self.corridas)


def _orden_grupo(grupo: Grupo):
    return ORDEN_FAMILIAS.index(grupo.familia), grupo.clave


def formar_grupos(corridas: List[Corrida]) -> List[Grupo]:
    """Agrupa las corridas usables: LOCA y LOCAC por área de rotura, gemelas ATWS/TRIP_OK juntas y
    el resto, una por grupo. Ignora las corridas cortas, descartadas y OOD.

    Devuelve los grupos ordenados por familia (NORM, LOCA, ATWS) y por clave; no modifica las corridas.
    """
    usables = sorted((c for c in corridas if c.estado == "usable" and c.clase in CLASES), key=clave_orden)
    if not usables:
        raise ValueError("No hay corridas usables que repartir.")
    por_id = {c.id: c for c in usables}
    claves: Dict[str, List[Corrida]] = {}
    for corrida in usables:
        if corrida.clase in CLASES_CON_AREA:
            if corrida.area is None:
                raise ErrorDatos(corrida.archivo, f"corrida {corrida.clase} sin área de rotura")
            clave = f"AREA-{corrida.area}"
        elif corrida.gemela in por_id:
            pareja = sorted((corrida.id, corrida.gemela), key=clave_id)
            clave = f"GEMELAS-{pareja[0]}-{pareja[1]}"
        else:
            clave = corrida.id
        claves.setdefault(clave, []).append(corrida)
    grupos = [
        Grupo(clave, FAMILIAS[miembros[0].clase], sorted(miembros, key=clave_orden))
        for clave, miembros in claves.items()
    ]
    return sorted(grupos, key=_orden_grupo)
