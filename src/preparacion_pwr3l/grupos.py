"""Grupos de corridas emparejadas que deben ir al mismo conjunto (principio II)."""
from dataclasses import dataclass, field
from typing import Dict, List

from preparacion_pwr3l.config import CLASES_CON_AREA, FAMILIAS
from preparacion_pwr3l.descubrimiento import Corrida, clave_id, clave_orden


@dataclass(eq=False)
class Grupo:
    clave: str  # AREA-<cm2>, GEMELAS-<Ra>-<Rb> o el id de la corrida
    familia: str  # NORM, LOCA (LOCA+LOCAC) o ATWS (ATWS+TRIP_OK)
    corridas: List[Corrida] = field(default_factory=list)


def clave_grupo(corrida: Corrida) -> str:
    if corrida.clase in CLASES_CON_AREA:
        return f"AREA-{corrida.area}"
    if corrida.gemela:
        a, b = sorted((corrida.id, corrida.gemela), key=clave_id)
        return f"GEMELAS-{a}-{b}"
    return corrida.id


def formar_grupos(corridas: List[Corrida]) -> List[Grupo]:
    """Agrupa las corridas usables; el resultado no depende del orden de entrada.

    Gemelas ATWS/TRIP_OK juntas; LOCA y LOCAC con la misma área de rotura juntas; el resto, una
    corrida por grupo. Si una gemela no es usable, la otra queda sola con la misma clave.
    """
    grupos: Dict[str, Grupo] = {}
    for corrida in sorted(corridas, key=clave_orden):
        if corrida.estado != "usable":
            raise ValueError(f"{corrida.id}: solo se agrupan corridas usables (estado {corrida.estado})")
        clave = clave_grupo(corrida)
        familia = FAMILIAS[corrida.clase]
        grupo = grupos.setdefault(clave, Grupo(clave, familia))
        if grupo.familia != familia:
            raise ValueError(f"{corrida.id}: el grupo {clave} mezcla las familias {grupo.familia} y {familia}")
        grupo.corridas.append(corrida)
    return [grupos[clave] for clave in sorted(grupos)]
