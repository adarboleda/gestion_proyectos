"""Tiempos de diagnóstico, falsas alarmas, confusiones, metas y reporte (research.md §3, §5–§7).

Definiciones:
- tiempo de diagnóstico: menor τ con la familia correcta confirmada y τ − 1 ≥ t_falla, menos t_falla;
- falsa alarma de la Etapa 1: LOCA o TRANS confirmada en una corrida NORM, o con τ < t_falla en una
  corrida de evento no incierta (en las inciertas no se cuenta: se informan aparte);
- confusión: la primera familia confirmada tras la falla no es la correcta;
- meta de diagnóstico: corridas de evento de prueba no inciertas con tiempo ≤ 10 s;
- meta de ATWS: ATWS de validación y prueba (inciertos incluidos) reconocidos en ≤ 3 s desde la demanda.
"""
import csv
import io
import json
from collections import defaultdict
from dataclasses import dataclass
from statistics import median
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from clasificador_etapa1.config import FAMILIA_DE_CLASE
from clasificador_etapa1.muestras import inicio_entero
from preparacion_pwr3l.descubrimiento import Corrida, clave_id
from tiempo_deteccion.atws import ResultadoATWS
from tiempo_deteccion.config import AVISO, CONJUNTOS_EVALUADOS, META_ATWS_S, META_DIAGNOSTICO_S
from tiempo_deteccion.falla import InstanteFalla
from tiempo_deteccion.reproduccion import LineaTiempo

FAMILIAS_EVENTO = ("LOCA", "TRANS")
NOMBRE_CONJUNTO = {"train": "entrenamiento", "val": "validación", "test": "prueba"}


@dataclass
class ResultadoCorrida:
    corrida: str
    clase: str
    familia: str  # NORM, LOCA o TRANS
    conjunto: str
    area: Optional[int]
    falla: Optional[InstanteFalla]  # None en NORM
    t_confirmacion: Optional[int]
    primera_familia: str  # primera familia confirmada tras la falla, o «»
    confusion: bool
    tiempo_diagnostico_s: Optional[float]
    tiempo_desde_validador_s: Optional[float]  # como en 005, para comparar (FR-011)
    atws: Optional[ResultadoATWS]
    falsas_alarmas_etapa1: Optional[Dict]  # {"episodios", "instantes"}; None en las inciertas

    @property
    def incierta(self) -> bool:
        return self.falla is not None and self.falla.incierta


# --- Por corrida --------------------------------------------------------------------------------

def _validos_desde(linea: LineaTiempo, t_inicio: float) -> np.ndarray:
    return linea.tau - 1 >= t_inicio


def tiempo_diagnostico(linea: LineaTiempo, familia: str, t_inicio: Optional[float]) -> Tuple[Optional[int], Optional[float]]:
    """(τ de confirmación, τ − t_inicio) de la primera confirmación de `familia` con τ − 1 ≥ t_inicio."""
    if t_inicio is None:
        return None, None
    validos = _validos_desde(linea, t_inicio) & (np.array(linea.confirmada, dtype=object) == familia)
    if not validos.any():
        return None, None
    tau = int(linea.tau[np.argmax(validos)])
    return tau, round(tau - t_inicio, 6)


def tiempo_desde_validador(linea: LineaTiempo, familia: str, inicio_validador: Optional[float]) -> Optional[float]:
    """Tiempo medido como en 005: desde el inicio del validador redondeado hacia arriba al segundo."""
    if inicio_validador is None:
        return None
    return tiempo_diagnostico(linea, familia, float(inicio_entero(inicio_validador)))[1]


def primera_familia(linea: LineaTiempo, t_falla: Optional[float]) -> str:
    """Primera familia de evento (LOCA o TRANS) confirmada con τ − 1 ≥ t_falla, o «» si ninguna.

    NORM no cuenta: tras la falla el modelo sigue viendo operación normal hasta que reconoce el evento.
    """
    if t_falla is None:
        return ""
    for tau, familia in zip(linea.tau, linea.confirmada):
        if familia in FAMILIAS_EVENTO and tau - 1 >= t_falla:
            return familia
    return ""


def falsas_alarmas_etapa1(linea: LineaTiempo, t_falla: Optional[float]) -> Dict:
    """Episodios e instantes con LOCA o TRANS confirmada antes de la falla (toda la corrida si `t_falla` es None)."""
    alarma = np.isin(np.array(linea.confirmada, dtype=object), FAMILIAS_EVENTO)
    if t_falla is not None:
        alarma &= linea.tau < t_falla
    episodios = int(alarma[0]) + int(np.sum(alarma[1:] & ~alarma[:-1])) if len(alarma) else 0
    return {"episodios": episodios, "instantes": int(alarma.sum())}


def resultados_por_corrida(
    corridas: Sequence[Tuple[Corrida, str]],
    lineas: Dict[str, LineaTiempo],
    fallas: Dict[str, InstanteFalla],
    atws: Dict[str, ResultadoATWS],
) -> List[ResultadoCorrida]:
    resultados = []
    for corrida, conjunto in corridas:
        familia = FAMILIA_DE_CLASE[corrida.clase]
        linea = lineas[corrida.id]
        falla = fallas.get(corrida.id) if familia != "NORM" else None
        t_falla = falla.t if falla is not None else None
        if familia == "NORM":
            t_conf, tiempo, primera, alarmas = None, None, "", falsas_alarmas_etapa1(linea, None)
            desde_validador = None
        else:
            t_conf, tiempo = tiempo_diagnostico(linea, familia, t_falla)
            primera = primera_familia(linea, t_falla)
            desde_validador = tiempo_desde_validador(linea, familia, falla.inicio_validador if falla else None)
            incierta = falla is None or falla.incierta
            alarmas = None if incierta else falsas_alarmas_etapa1(linea, t_falla)
        resultados.append(ResultadoCorrida(
            corrida=corrida.id, clase=corrida.clase, familia=familia, conjunto=conjunto, area=corrida.area,
            falla=falla, t_confirmacion=t_conf, primera_familia=primera,
            confusion=familia != "NORM" and primera not in ("", familia), tiempo_diagnostico_s=tiempo,
            tiempo_desde_validador_s=desde_validador,
            atws=atws.get(corrida.id), falsas_alarmas_etapa1=alarmas,
        ))
    return sorted(resultados, key=lambda r: (CONJUNTOS_EVALUADOS.index(r.conjunto) if r.conjunto in CONJUNTOS_EVALUADOS else 9,
                                             clave_id(r.corrida)))


# --- Resumen y metas ----------------------------------------------------------------------------

def _estadistica(tiempos: List[Optional[float]], meta: float) -> Dict:
    detectados = [t for t in tiempos if t is not None]
    return {
        "corridas": len(tiempos),
        "detectadas": len(detectados),
        "en_meta": sum(1 for t in detectados if t <= meta),
        "mediana_s": median(detectados) if detectados else None,
        "maximo_s": max(detectados) if detectados else None,
    }


def _diagnosticables(resultados, conjunto):
    return [r for r in resultados if r.conjunto == conjunto and r.familia != "NORM" and not r.incierta]


def _diagnostico(resultados: List[ResultadoCorrida], conjunto: str) -> Dict:
    eventos = _diagnosticables(resultados, conjunto)
    datos = {"total": _estadistica([r.tiempo_diagnostico_s for r in eventos], META_DIAGNOSTICO_S)}
    for familia in FAMILIAS_EVENTO:
        datos[familia] = _estadistica([r.tiempo_diagnostico_s for r in eventos if r.familia == familia], META_DIAGNOSTICO_S)
    por_area = defaultdict(list)
    for r in eventos:
        if r.familia == "LOCA":
            por_area[r.area].append(r.tiempo_diagnostico_s)
    datos["LOCA_por_area"] = {str(a): por_area[a] for a in sorted(por_area, key=lambda a: (a is None, a or 0))}
    return datos


def _atws_de(resultados, conjuntos) -> List[ResultadoCorrida]:
    return [r for r in resultados if r.conjunto in conjuntos and r.clase == "ATWS"]


def _estadistica_atws(seleccion: List[ResultadoCorrida]) -> Dict:
    tiempos = [r.atws.tiempo_desde_demanda_s if r.atws else None for r in seleccion]
    datos = _estadistica(tiempos, META_ATWS_S)
    datos["por_corrida"] = {r.corrida: t for r, t in zip(seleccion, tiempos)}
    return datos


def _falsas_alarmas(resultados: List[ResultadoCorrida], conjunto: str) -> Dict:
    del_conjunto = [r for r in resultados if r.conjunto == conjunto]
    norm = [r for r in del_conjunto if r.familia == "NORM" and r.falsas_alarmas_etapa1["episodios"]]
    previos = [r for r in del_conjunto if r.familia != "NORM" and r.falsas_alarmas_etapa1
               and r.falsas_alarmas_etapa1["episodios"]]
    regla = [r for r in del_conjunto if r.atws is not None and r.atws.falsa_alarma]
    return {
        "etapa1": {
            "corridas_norm": {"episodios": sum(r.falsas_alarmas_etapa1["episodios"] for r in norm),
                              "corridas": [r.corrida for r in norm]},
            "tramos_previos": {"episodios": sum(r.falsas_alarmas_etapa1["episodios"] for r in previos),
                               "corridas": [r.corrida for r in previos]},
            "inciertas_no_contadas": [r.corrida for r in del_conjunto if r.incierta],
        },
        "regla": {"recomendaciones": len(regla), "corridas": [r.corrida for r in regla]},
    }


def resumen(resultados: List[ResultadoCorrida]) -> Dict:
    return {
        "diagnostico": {c: _diagnostico(resultados, c) for c in CONJUNTOS_EVALUADOS},
        "atws": {
            "val_y_test": _estadistica_atws(_atws_de(resultados, CONJUNTOS_EVALUADOS)),
            "test": _estadistica_atws(_atws_de(resultados, ("test",))),
        },
        "falsas_alarmas": {c: _falsas_alarmas(resultados, c) for c in CONJUNTOS_EVALUADOS},
        "confusiones": {c: [r.corrida for r in resultados if r.conjunto == c and r.confusion] for c in CONJUNTOS_EVALUADOS},
    }


def _meta(dentro: int, total: int, unidad: str) -> Dict:
    if total == 0:
        return {"dentro": 0, "total": 0, "valor": f"no hay {unidad}", "cumple": "sin datos"}
    return {"dentro": dentro, "total": total, "valor": f"{dentro} de {total} ({100 * dentro / total:.0f} %)",
            "cumple": dentro == total}


def metas(resultados: List[ResultadoCorrida]) -> Dict:
    prueba = _diagnosticables(resultados, "test")
    dentro = sum(1 for r in prueba if r.tiempo_diagnostico_s is not None and r.tiempo_diagnostico_s <= META_DIAGNOSTICO_S)
    diagnostico = _meta(dentro, len(prueba), "corridas de evento de prueba no inciertas")
    diagnostico["meta"] = (f"familia del evento confirmada en ≤ {META_DIAGNOSTICO_S:g} s desde la falla en el 100 % "
                           "de las corridas de evento de prueba no inciertas")

    def atws_en(conjuntos):
        seleccion = _atws_de(resultados, conjuntos)
        dentro_atws = sum(1 for r in seleccion if r.atws and r.atws.tiempo_desde_demanda_s is not None
                          and r.atws.tiempo_desde_demanda_s <= META_ATWS_S)
        return _meta(dentro_atws, len(seleccion), "ATWS")

    atws = atws_en(CONJUNTOS_EVALUADOS)
    atws["meta"] = (f"ATWS reconocido en ≤ {META_ATWS_S:g} s desde la demanda de disparo en el 100 % de los ATWS "
                    "de validación y prueba (inciertos incluidos; no detectado = incumple)")
    atws["solo_prueba"] = atws_en(("test",))
    return {"diagnostico_10s": diagnostico, "atws_3s": atws}


# --- Serialización ------------------------------------------------------------------------------

def _num(valor, decimales=4):
    if valor is None:
        return None
    if isinstance(valor, (bool, np.bool_)):
        return bool(valor)
    if isinstance(valor, (int, np.integer)):
        return int(valor)
    return round(float(valor), decimales)


def falla_a_dict(falla: Optional[InstanteFalla]) -> Optional[Dict]:
    if falla is None:
        return None
    return {"t": _num(falla.t), "fuente": falla.fuente, "detalle": falla.detalle,
            "inicio_validador": _num(falla.inicio_validador), "incierta": falla.incierta, "motivo": falla.motivo}


def atws_a_dict(r: Optional[ResultadoATWS]) -> Optional[Dict]:
    if r is None:
        return None
    return {"recomendacion": r.recomendacion, "motivo": r.motivo, "es_atws": r.es_atws, "t_demanda": _num(r.t_demanda),
            "t_decision": _num(r.t_decision), "tiempo_desde_demanda_s": _num(r.tiempo_desde_demanda_s),
            "tiempo_desde_falla_s": _num(r.tiempo_desde_falla_s), "falsa_alarma": r.falsa_alarma}


def resultado_a_dict(r: ResultadoCorrida) -> Dict:
    return {
        "corrida": r.corrida, "conjunto": r.conjunto, "clase": r.clase, "familia": r.familia, "area": r.area,
        "falla": falla_a_dict(r.falla), "t_confirmacion": r.t_confirmacion, "primera_familia": r.primera_familia,
        "confusion": r.confusion, "tiempo_diagnostico_s": _num(r.tiempo_diagnostico_s),
        "tiempo_desde_validador_s": _num(r.tiempo_desde_validador_s),
        "atws": atws_a_dict(r.atws), "falsas_alarmas_etapa1": r.falsas_alarmas_etapa1,
    }


def construir_tiempos(resultados: List[ResultadoCorrida], fallas: Dict[str, InstanteFalla],
                      conjunto_de: Dict[str, str], configuracion: Dict) -> Dict:
    """Contenido de `tiempos.json` (contracts/salidas.md)."""
    datos_resumen = resumen(resultados)
    orden = sorted(fallas, key=clave_id)
    return {
        "aviso": AVISO,
        "configuracion": configuracion,
        "corridas": [resultado_a_dict(r) for r in resultados],
        "resumen": {"diagnostico": datos_resumen["diagnostico"], "atws": datos_resumen["atws"]},
        "metas": metas(resultados),
        "falsas_alarmas": datos_resumen["falsas_alarmas"],
        "confusiones": datos_resumen["confusiones"],
        "inciertas": [dict(corrida=rid, conjunto=conjunto_de.get(rid), **falla_a_dict(fallas[rid]))
                      for rid in orden if fallas[rid].incierta],
        "instantes": {rid: dict(conjunto=conjunto_de.get(rid), **falla_a_dict(fallas[rid])) for rid in orden},
    }


COLUMNAS_TIEMPOS = [
    "corrida", "conjunto", "clase", "familia", "area", "t_falla", "fuente_falla", "incierta", "inicio_validador",
    "t_confirmacion", "primera_familia", "tiempo_diagnostico_s", "tiempo_desde_validador_s", "atws_recomendacion", "t_demanda",
    "tiempo_atws_demanda_s", "tiempo_atws_falla_s", "falsas_alarmas_etapa1",
]


def _celda(valor) -> str:
    return "" if valor is None else str(valor)  # los números ya vienen redondeados a 4 decimales


def serializar_tiempos_csv(datos: Dict) -> str:
    salida = io.StringIO()
    escritor = csv.writer(salida, lineterminator="\n")
    escritor.writerow(COLUMNAS_TIEMPOS)
    for c in datos["corridas"]:
        falla = c["falla"] or {}
        atws = c["atws"] or {}
        alarmas = c["falsas_alarmas_etapa1"]
        fila = {
            "corrida": c["corrida"], "conjunto": c["conjunto"], "clase": c["clase"], "familia": c["familia"],
            "area": c["area"], "t_falla": falla.get("t"), "fuente_falla": falla.get("fuente"),
            "incierta": falla.get("incierta", False) if c["falla"] else "", "inicio_validador": falla.get("inicio_validador"),
            "t_confirmacion": c["t_confirmacion"], "primera_familia": c["primera_familia"],
            "tiempo_diagnostico_s": c["tiempo_diagnostico_s"], "tiempo_desde_validador_s": c["tiempo_desde_validador_s"],
            "atws_recomendacion": atws.get("recomendacion"),
            "t_demanda": atws.get("t_demanda"), "tiempo_atws_demanda_s": atws.get("tiempo_desde_demanda_s"),
            "tiempo_atws_falla_s": atws.get("tiempo_desde_falla_s"),
            "falsas_alarmas_etapa1": alarmas["episodios"] if alarmas is not None else None,
        }
        escritor.writerow([_celda(fila[col]) for col in COLUMNAS_TIEMPOS])
    return salida.getvalue()


COLUMNAS_LINEAS = ["corrida", "conjunto", "tau", "p_norm", "p_loca", "p_trans", "confirmada", "decision_atws"]


def serializar_lineas_csv(lineas: Dict[str, LineaTiempo], orden: Sequence[str],
                          atws: Optional[Dict[str, ResultadoATWS]] = None) -> str:
    """Una fila por corrida y segundo; `decision_atws` solo en el segundo de decisión de la regla."""
    atws = atws or {}
    salida = io.StringIO()
    escritor = csv.writer(salida, lineterminator="\n")
    escritor.writerow(COLUMNAS_LINEAS)
    for rid in orden:
        linea = lineas[rid]
        regla = atws.get(rid)
        decision = regla.t_decision if regla is not None else None
        for i, tau in enumerate(linea.tau):
            p = linea.probabilidades[i]
            escritor.writerow([rid, linea.conjunto, int(tau), f"{p[0]:.4f}", f"{p[1]:.4f}", f"{p[2]:.4f}",
                               linea.confirmada[i], regla.recomendacion if decision == int(tau) else ""])
    return salida.getvalue()


def serializar_json(datos: Dict) -> str:
    return json.dumps(datos, ensure_ascii=False, indent=2) + "\n"


# --- Reporte legible ----------------------------------------------------------------------------

def _t(valor) -> str:
    return "—" if valor is None else f"{valor:g}"


def _cumple(valor) -> str:
    return {True: "CUMPLE", False: "NO CUMPLE"}.get(valor, "sin datos")


def _lista(ids) -> str:
    return ", ".join(ids) if ids else "ninguna"


def _diferencia(c: Dict) -> Optional[float]:
    """Tiempo desde el validador menos tiempo desde la falla (positivo: la medición de 005 daba más)."""
    if c["tiempo_desde_validador_s"] is None or c["tiempo_diagnostico_s"] is None:
        return None
    return round(c["tiempo_desde_validador_s"] - c["tiempo_diagnostico_s"], 4)


def formatear_reporte(datos: Dict) -> str:
    conf = datos["configuracion"]
    lineas = [
        "Tiempo de detección desde la falla — PWR 3L (KAN-25)",
        datos["aviso"],
        "",
        f"Semilla del reparto: {conf['semilla']} | confirmación: probabilidad ≥ {conf['umbral']:.2f} durante "
        f"{conf['confirmacion_s']} s | regla de ATWS: umbral {conf['regla_atws']['umbral_pwnt_pct']:.1f} % del PWNT inicial, "
        f"decisión {conf['regla_atws']['espera_s']:g} s después de la demanda",
        "",
    ]
    instantes = datos["instantes"]
    fuentes = defaultdict(int)
    for i in instantes.values():
        fuentes[i["fuente"]] += 1
    lineas.append(f"Instante de la falla: {len(instantes)} corridas de evento — "
                  + ", ".join(f"{fuente} {n}" for fuente, n in sorted(fuentes.items())))
    lineas.append(f"Inciertas (no cuentan para la meta de diagnóstico): {len(datos['inciertas'])}")
    for i in datos["inciertas"]:
        lineas.append(f"  {i['corrida']} ({NOMBRE_CONJUNTO.get(i['conjunto'], i['conjunto'])}): {i['motivo']}")
    for conjunto in ("test", "val"):
        nombre = "prueba" if conjunto == "test" else "validación (referencia: el clasificador eligió su época con ella)"
        lineas += ["", f"Diagnóstico de la Etapa 1 — {nombre}",
                   "  corrida  clase    área   t_falla  fuente      t_conf  desde falla  desde validador  diferencia  primera"]
        for c in datos["corridas"]:
            if c["conjunto"] != conjunto or c["familia"] == "NORM":
                continue
            falla = c["falla"] or {}
            marca = " (incierta)" if falla.get("incierta") else ""
            lineas.append(
                f"  {c['corrida']:<7}  {c['clase']:<7}  {_t(c['area']):>5}  {_t(falla.get('t')):>7}  "
                f"{falla.get('fuente', ''):<10}  {_t(c['t_confirmacion']):>6}  {_t(c['tiempo_diagnostico_s']):>11}  "
                f"{_t(c['tiempo_desde_validador_s']):>15}  {_t(_diferencia(c)):>10}  "
                f"{c['primera_familia'] or '—'}{marca}"
            )
        diag = datos["resumen"]["diagnostico"][conjunto]
        for familia in ("LOCA", "TRANS", "total"):
            e = diag[familia]
            lineas.append(f"  {familia}: {e['en_meta']} de {e['corridas']} en ≤ {conf['meta_diagnostico_s']:g} s "
                          f"(detectadas {e['detectadas']}; mediana {_t(e['mediana_s'])} s; máximo {_t(e['maximo_s'])} s)")
        if diag["LOCA_por_area"]:
            lineas.append("  LOCA por área (cm²): " + "; ".join(
                f"{area}: {', '.join(_t(t) for t in tiempos)} s" for area, tiempos in diag["LOCA_por_area"].items()))
    lineas += ["", "ATWS — regla de 006 (tiempo desde la demanda de disparo; desde la falla como dato)",
               "  corrida  conjunto  clase    recomendación  t_demanda  t_decisión  desde demanda  desde falla"]
    for c in datos["corridas"]:
        a = c["atws"]
        if a is None or c["clase"] not in ("ATWS", "TRIP_OK"):
            continue
        lineas.append(
            f"  {c['corrida']:<7}  {c['conjunto']:<8}  {c['clase']:<7}  {a['recomendacion']:<13}  {_t(a['t_demanda']):>9}  "
            f"{_t(a['t_decision']):>10}  {_t(a['tiempo_desde_demanda_s']):>13}  {_t(a['tiempo_desde_falla_s']):>11}"
        )
    lineas += ["", "Falsas alarmas"]
    for conjunto in CONJUNTOS_EVALUADOS:
        f = datos["falsas_alarmas"][conjunto]
        e1 = f["etapa1"]
        lineas.append(
            f"  {NOMBRE_CONJUNTO[conjunto]}: Etapa 1 en corridas NORM {e1['corridas_norm']['episodios']} "
            f"({_lista(e1['corridas_norm']['corridas'])}); antes de la falla {e1['tramos_previos']['episodios']} "
            f"({_lista(e1['tramos_previos']['corridas'])}); inciertas no contadas: {_lista(e1['inciertas_no_contadas'])}; "
            f"regla «posible ATWS» sin ATWS {f['regla']['recomendaciones']} ({_lista(f['regla']['corridas'])})"
        )
    lineas.append("Confusiones (primera familia confirmada tras la falla equivocada): " + "; ".join(
        f"{NOMBRE_CONJUNTO[c]} {_lista(ids)}" for c, ids in datos["confusiones"].items()))
    m = datos["metas"]
    lineas += [
        "",
        "Metas",
        f"  Diagnóstico ≤ {conf['meta_diagnostico_s']:g} s: {m['diagnostico_10s']['meta']}.",
        f"    Resultado: {m['diagnostico_10s']['valor']} → {_cumple(m['diagnostico_10s']['cumple'])}",
        f"  ATWS ≤ {conf['meta_atws_s']:g} s: {m['atws_3s']['meta']}.",
        f"    Resultado: {m['atws_3s']['valor']} → {_cumple(m['atws_3s']['cumple'])} "
        f"(solo prueba: {m['atws_3s']['solo_prueba']['valor']})",
    ]
    return "\n".join(lineas) + "\n"
