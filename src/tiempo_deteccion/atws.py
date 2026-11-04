"""Tiempo de ATWS con la regla de 006, calibrada solo con entrenamiento (research.md §4).

La meta de 3 s se mide desde la demanda de disparo (señal del registro + retardo de la lógica); el
tiempo desde la falla (evento iniciador) se informa como dato y queda vacío en las corridas inciertas.
"""
from dataclasses import dataclass
from typing import Dict, Optional, Sequence, Tuple

from regla_atws.regla import Caso, Regla, calibrar, evaluar
from tiempo_deteccion.config import CONJUNTOS_EVALUADOS
from tiempo_deteccion.falla import InstanteFalla


@dataclass
class ResultadoATWS:
    corrida: str
    conjunto: str
    clase: str
    es_atws: bool
    recomendacion: str  # «posible ATWS» o «sin ATWS»
    motivo: str
    t_demanda: Optional[float]
    t_decision: Optional[int]
    tiempo_desde_demanda_s: Optional[float]  # solo ATWS detectados
    tiempo_desde_falla_s: Optional[float]  # solo ATWS detectados con instante de falla confiable
    falsa_alarma: bool  # «posible ATWS» en una corrida que no es ATWS


def evaluar_atws(casos: Sequence[Caso], fallas: Dict[str, InstanteFalla]) -> Tuple[Regla, Dict[str, ResultadoATWS]]:
    """Calibra con los casos de entrenamiento y evalúa los de validación y prueba."""
    regla = calibrar([c for c in casos if c.conjunto == "train"])
    resultados = {}
    for caso in casos:
        if caso.conjunto not in CONJUNTOS_EVALUADOS:
            continue
        r = evaluar(regla, caso)
        detectado = r.recomendacion == "posible ATWS"
        desde_falla = None
        falla = fallas.get(r.id)
        if detectado and r.es_atws and falla is not None and falla.t is not None and not falla.incierta:
            desde_falla = round(r.t_decision - falla.t, 6)
        resultados[r.id] = ResultadoATWS(
            corrida=r.id, conjunto=r.conjunto, clase=r.clase, es_atws=r.es_atws, recomendacion=r.recomendacion,
            motivo=r.motivo, t_demanda=r.t_demanda, t_decision=r.t_decision,
            tiempo_desde_demanda_s=r.t_deteccion_demanda, tiempo_desde_falla_s=desde_falla,
            falsa_alarma=detectado and not r.es_atws,
        )
    return regla, resultados
