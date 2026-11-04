"""Calibración (solo entrenamiento) y evaluación de la regla determinista de ATWS (research §2–§4)."""
import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

import numpy as np

from preparacion_pwr3l.descubrimiento import Corrida, ErrorDatos
from regla_atws.config import ESPERA_S
from regla_atws.eventos import Senal


@dataclass(eq=False)
class Caso:
    """Lo que la regla necesita de una corrida: su señal, su scram y la serie de PWNT (300 s)."""

    corrida: Corrida
    conjunto: str
    senal: Optional[Senal]
    scram: Optional[float]
    pwnt: np.ndarray


@dataclass
class Regla:
    umbral: float  # % del PWNT inicial
    retardos: Dict[str, float]  # tipo de señal -> s hasta el scram (entrenamiento)
    retardo_por_defecto: float  # el mayor de entrenamiento
    espera: float
    minimo_atws: float
    maximo_no_atws: float
    solape: bool
    falsas_alarmas_entrenamiento: int


@dataclass
class Resultado:
    id: str
    clase: str
    conjunto: str
    es_atws: bool
    tipo_senal: Optional[str]
    fuente_senal: Optional[str]
    t_senal: Optional[float]
    retardo: Optional[float]
    retardo_por_defecto: bool
    t_demanda: Optional[float]
    t_decision: Optional[int]
    pwnt_decision: Optional[float]
    recomendacion: str  # «posible ATWS» o «sin ATWS»
    motivo: str  # flujo alto | flujo caído | sin demanda | decisión fuera de la ventana
    acierto: bool
    t_deteccion_demanda: Optional[float] = None
    t_deteccion_senal: Optional[float] = None


def calibrar_retardos(casos: Sequence[Caso]) -> Dict[str, float]:
    """Por tipo de señal, el mayor tiempo entre la señal y «Reactor Scram» en las corridas dadas."""
    retardos: Dict[str, float] = {}
    for caso in casos:
        if caso.senal is not None and caso.scram is not None and caso.scram >= caso.senal.tiempo:
            retardo = round(caso.scram - caso.senal.tiempo, 6)
            retardos[caso.senal.tipo] = max(retardos.get(caso.senal.tipo, 0.0), retardo)
    return dict(sorted(retardos.items()))


def calibrar_umbral(flujos_atws: Sequence[float], flujos_no_atws: Sequence[float]) -> dict:
    """Punto medio si los ATWS quedan por encima de todo lo demás; si no, el mayor umbral que no omite ATWS."""
    if not flujos_atws:
        raise ValueError("No hay ATWS de entrenamiento con demanda de disparo para calibrar el umbral.")
    minimo = float(min(flujos_atws))
    maximo = float(max(flujos_no_atws)) if flujos_no_atws else 0.0
    if minimo > maximo:
        return {"umbral": (minimo + maximo) / 2, "minimo_atws": minimo, "maximo_no_atws": maximo,
                "solape": False, "falsas_alarmas": 0}
    umbral = float(np.nextafter(minimo, -np.inf))
    falsas = sum(1 for f in flujos_no_atws if f > umbral)
    return {"umbral": umbral, "minimo_atws": minimo, "maximo_no_atws": maximo, "solape": True, "falsas_alarmas": falsas}


def _flujo_relativo(caso: Caso) -> np.ndarray:
    inicial = float(caso.pwnt[0])
    if not inicial > 0:
        raise ErrorDatos(caso.corrida.archivo, "PWNT inicial no positivo", "PWNT")
    return np.asarray(caso.pwnt, dtype=np.float64) / inicial * 100.0


def _decision(caso: Caso, retardos: Dict[str, float], defecto: float, espera: float):
    """(retardo, por defecto, t_demanda, t_decision, flujo en la decisión o None si cae fuera)."""
    flujo = _flujo_relativo(caso)
    if caso.senal is None:
        return None, False, None, None, None
    por_defecto = caso.senal.tipo not in retardos
    retardo = defecto if por_defecto else retardos[caso.senal.tipo]
    t_demanda = round(caso.senal.tiempo + retardo, 6)
    t_decision = math.ceil(round(t_demanda + espera, 6))
    valor = float(flujo[t_decision]) if t_decision < len(flujo) else None
    return retardo, por_defecto, t_demanda, t_decision, valor


def calibrar(casos_entrenamiento: Sequence[Caso], espera: float = ESPERA_S) -> Regla:
    """Retardos y umbral a partir de las corridas de entrenamiento únicamente."""
    ajenos = [c.corrida.id for c in casos_entrenamiento if c.conjunto != "train"]
    if ajenos:
        raise ValueError(f"La calibración solo admite corridas de entrenamiento; recibió {', '.join(ajenos)}.")
    retardos = calibrar_retardos(casos_entrenamiento)
    if not retardos:
        raise ValueError("No hay corridas de entrenamiento con señal y scram para medir los retardos.")
    defecto = max(retardos.values())
    atws, otros = [], []
    for caso in casos_entrenamiento:
        valor = _decision(caso, retardos, defecto, espera)[4]
        if valor is not None:
            (atws if caso.corrida.clase == "ATWS" else otros).append(valor)
    umbral = calibrar_umbral(atws, otros)
    return Regla(
        umbral=umbral["umbral"], retardos=retardos, retardo_por_defecto=defecto, espera=espera,
        minimo_atws=umbral["minimo_atws"], maximo_no_atws=umbral["maximo_no_atws"], solape=umbral["solape"],
        falsas_alarmas_entrenamiento=umbral["falsas_alarmas"],
    )


def evaluar(regla: Regla, caso: Caso) -> Resultado:
    """Recomendación para una corrida con la regla ya calibrada (no ve nada más que esta corrida)."""
    retardo, por_defecto, t_demanda, t_decision, valor = _decision(
        caso, regla.retardos, regla.retardo_por_defecto, regla.espera
    )
    es_atws = caso.corrida.clase == "ATWS"
    if caso.senal is None:
        recomendacion, motivo = "sin ATWS", "sin demanda"
    elif valor is None:
        recomendacion, motivo = "sin ATWS", "decisión fuera de la ventana"
    elif valor > regla.umbral:
        recomendacion, motivo = "posible ATWS", "flujo alto"
    else:
        recomendacion, motivo = "sin ATWS", "flujo caído"
    detectado = recomendacion == "posible ATWS"
    resultado = Resultado(
        id=caso.corrida.id, clase=caso.corrida.clase, conjunto=caso.conjunto, es_atws=es_atws,
        tipo_senal=caso.senal.tipo if caso.senal else None, fuente_senal=caso.senal.fuente if caso.senal else None,
        t_senal=caso.senal.tiempo if caso.senal else None, retardo=retardo, retardo_por_defecto=por_defecto,
        t_demanda=t_demanda, t_decision=t_decision, pwnt_decision=valor, recomendacion=recomendacion,
        motivo=motivo, acierto=detectado == es_atws,
    )
    if detectado and es_atws:
        resultado.t_deteccion_demanda = round(t_decision - t_demanda, 6)
        resultado.t_deteccion_senal = round(t_decision - caso.senal.tiempo, 6)
    return resultado


def evaluar_todas(regla: Regla, casos: Sequence[Caso]) -> List[Resultado]:
    return [evaluar(regla, caso) for caso in casos]
