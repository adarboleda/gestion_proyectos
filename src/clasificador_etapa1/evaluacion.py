"""Evaluación del clasificador de Etapa 1 sobre las corridas de prueba.

Definiciones (research.md §6–§8):
- horizonte h: muestras de evento con k = h más todas las muestras de operación normal;
- confirmación: la misma familia con probabilidad ≥ 0,80 en dos segundos seguidos;
- tiempo de confirmación: menor k con τ − 1 ≥ inicio en que se confirma la familia correcta;
- falsa alarma: confirmación de LOCA o TRANS en dos muestras etiquetadas como operación normal.
"""
import math
from collections import defaultdict
from statistics import median
from typing import Dict, Iterable, List, Optional, Set

import numpy as np
from sklearn.metrics import confusion_matrix, f1_score, precision_recall_fscore_support

from clasificador_etapa1.config import (
    AREA_META_CM2,
    AVISO_REPORTE,
    ETIQUETA,
    F1_META,
    FAMILIA_DE_CLASE,
    FAMILIAS,
    HORIZONTES_S,
    LATENCIA_META_S,
    PRIMEROS_S,
    UMBRAL,
)
from clasificador_etapa1.muestras import Muestras, inicio_entero
from preparacion_pwr3l.descubrimiento import Corrida, clave_id

ETIQUETAS = list(range(len(FAMILIAS)))


def _redondear(valor):
    return None if valor is None else round(float(valor), 4)


def _f1_macro(y: np.ndarray, pred: np.ndarray) -> Optional[float]:
    """F1 macro solo sobre las familias presentes (en lo real o en lo predicho): una familia sin
    muestras no se cuenta como F1 = 0."""
    presentes = sorted(set(np.asarray(y).tolist()) | set(np.asarray(pred).tolist()))
    if not presentes:
        return None
    return _redondear(f1_score(y, pred, labels=presentes, average="macro", zero_division=0))


def metricas(y: np.ndarray, pred: np.ndarray) -> Dict:
    """Matriz de confusión, precisión, exhaustividad y F1 por familia y F1 macro."""
    precision, exhaustividad, f1, soporte = precision_recall_fscore_support(
        y, pred, labels=ETIQUETAS, zero_division=0
    )
    por_familia = {}
    for i, familia in enumerate(FAMILIAS):
        hay = int(soporte[i]) > 0
        por_familia[familia] = {
            "precision": _redondear(precision[i]) if hay or (pred == i).any() else None,
            "exhaustividad": _redondear(exhaustividad[i]) if hay else None,
            "f1": _redondear(f1[i]) if hay else None,
            "soporte": int(soporte[i]),
        }
    return {
        "matriz": confusion_matrix(y, pred, labels=ETIQUETAS).tolist(),
        "por_familia": por_familia,
        "f1_macro": _f1_macro(y, pred),
    }


def _normales(m: Muestras) -> np.ndarray:
    return m.y == ETIQUETA["NORM"]


def por_horizonte(m: Muestras, probabilidades: np.ndarray, horizontes: Iterable[int] = HORIZONTES_S) -> List[Dict]:
    pred = probabilidades.argmax(axis=1)
    normales = _normales(m)
    tabla = []
    for h in horizontes:
        en_h = (m.k == h) & ~normales
        exhaustividad = {}
        for familia in ("LOCA", "TRANS"):
            de_familia = en_h & (m.y == ETIQUETA[familia])
            exhaustividad[familia] = _redondear((pred[de_familia] == ETIQUETA[familia]).mean()) if de_familia.any() else None
        seleccion = en_h | normales
        f1 = _f1_macro(m.y[seleccion], pred[seleccion])
        tabla.append({"h": h, "eventos": int(en_h.sum()), "exhaustividad": exhaustividad, "f1_macro": f1})
    return tabla


def primeros_s(m: Muestras, probabilidades: np.ndarray, segundos: int = PRIMEROS_S) -> Optional[float]:
    """F1 macro de las muestras de evento con 0 ≤ k ≤ segundos más todas las de operación normal."""
    normales = _normales(m)
    seleccion = normales | ((m.k >= 0) & (m.k <= segundos) & ~normales)
    if not seleccion.any():
        return None
    pred = probabilidades.argmax(axis=1)
    return _f1_macro(m.y[seleccion], pred[seleccion])


def confirmadas(probabilidades: np.ndarray, umbral: float = UMBRAL) -> np.ndarray:
    """(n, 3) booleano: la familia supera el umbral en esa fila y en la anterior (segundos seguidos)."""
    sobre = probabilidades >= umbral
    resultado = np.zeros_like(sobre)
    resultado[1:] = sobre[1:] & sobre[:-1]
    return resultado


def _por_corrida(m: Muestras):
    for rid in dict.fromkeys(m.corrida):
        indices = np.flatnonzero(m.corrida == rid)
        yield rid, indices[np.argsort(m.tau[indices])]


def tiempos_confirmacion(m: Muestras, probabilidades: np.ndarray, corridas: List[Corrida],
                         inicios: Dict[str, Optional[float]]) -> List[Dict]:
    por_id = {c.id: c for c in corridas}
    resultado = []
    for rid, indices in _por_corrida(m):
        corrida = por_id[rid]
        familia = FAMILIA_DE_CLASE[corrida.clase]
        if familia == "NORM":
            continue
        inicio = inicio_entero(inicios[rid])
        conf = confirmadas(probabilidades[indices])[:, ETIQUETA[familia]]
        taus = m.tau[indices]
        consecutivo = np.zeros(len(taus), dtype=bool)
        consecutivo[1:] = np.diff(taus) == 1
        validos = conf & consecutivo & (taus - 1 >= inicio)
        tiempo = float(taus[np.argmax(validos)] - inicio) if validos.any() else None
        resultado.append({
            "corrida": rid, "clase": corrida.clase, "familia": familia, "area": corrida.area,
            "inicio_s": inicios[rid], "tiempo_s": tiempo,
        })
    return sorted(resultado, key=lambda d: (FAMILIAS.index(d["familia"]), clave_id(d["corrida"])))


def resumen_deteccion(deteccion: List[Dict]) -> Dict:
    resumen = {}
    for familia in ("LOCA", "TRANS"):
        tiempos = [d["tiempo_s"] for d in deteccion if d["familia"] == familia]
        detectados = [t for t in tiempos if t is not None]
        resumen[familia] = {
            "corridas": len(tiempos),
            "detectadas": len(detectados),
            "mediana_s": median(detectados) if detectados else None,
            "maximo_s": max(detectados) if detectados else None,
        }
    por_area = defaultdict(list)
    for d in deteccion:
        if d["familia"] == "LOCA":
            por_area[d["area"]].append(d["tiempo_s"])
    resumen["LOCA_por_area"] = {str(area): por_area[area] for area in sorted(por_area, key=lambda a: (a is None, a))}
    return resumen


def falsas_alarmas(m: Muestras, probabilidades: np.ndarray, corridas_norm: Set[str]) -> Dict:
    resultado = {
        "corridas_norm": {"instantes": 0, "episodios": 0, "corridas": []},
        "tramos_previos": {"instantes": 0, "episodios": 0, "corridas": []},
    }
    for rid, indices in _por_corrida(m):
        normales = m.y[indices] == ETIQUETA["NORM"]
        taus = m.tau[indices]
        conf = confirmadas(probabilidades[indices])
        alarma = (conf[:, ETIQUETA["LOCA"]] | conf[:, ETIQUETA["TRANS"]])
        ambos_normales = np.zeros(len(indices), dtype=bool)
        ambos_normales[1:] = normales[1:] & normales[:-1] & (np.diff(taus) == 1)
        alarma &= ambos_normales
        if not alarma.any():
            continue
        destino = resultado["corridas_norm" if rid in corridas_norm else "tramos_previos"]
        destino["instantes"] += int(alarma.sum())
        destino["episodios"] += int(alarma[0]) + int(np.sum(alarma[1:] & ~alarma[:-1]))
        destino["corridas"].append(rid)
    for destino in resultado.values():
        destino["corridas"] = sorted(destino["corridas"], key=clave_id)
    return resultado


def metas(deteccion: List[Dict], falsas: Dict, f1_primeros: Optional[float], hay_corridas_norm: bool) -> Dict:
    grandes = [d for d in deteccion if d["familia"] == "LOCA" and d.get("area") is not None and d["area"] >= AREA_META_CM2]
    if grandes:
        dentro = [d for d in grandes if d["tiempo_s"] is not None and d["tiempo_s"] <= LATENCIA_META_S]
        sc1 = {"valor": f"{len(dentro)} de {len(grandes)} en ≤ {LATENCIA_META_S} s", "cumple": len(dentro) == len(grandes)}
    else:
        sc1 = {"valor": "no hay LOCA ≥ 50 cm² en prueba", "cumple": "sin datos"}
    if hay_corridas_norm:
        n = falsas["corridas_norm"]["episodios"]
        sc2 = {"valor": f"{n} falsas alarmas en corridas NORM", "cumple": n == 0}
    else:
        sc2 = {"valor": "no hay corridas NORM en prueba", "cumple": "sin datos"}
    if f1_primeros is None:
        sc3 = {"valor": "sin muestras", "cumple": "sin datos"}
    else:
        sc3 = {"valor": f"F1 macro = {f1_primeros:.3f}", "cumple": f1_primeros >= F1_META}
    return {
        "SC-001": dict(sc1, meta=f"LOCA ≥ {AREA_META_CM2} cm² confirmada en ≤ {LATENCIA_META_S} s en el 100 %"),
        "SC-002": dict(sc2, meta="0 falsas alarmas en corridas NORM"),
        "SC-003": dict(sc3, meta=f"F1 macro de los primeros {PRIMEROS_S} s ≥ {F1_META:.2f}"),
    }


def evaluar_probabilidades(m: Muestras, probabilidades: np.ndarray, corridas: List[Corrida],
                           inicios: Dict[str, Optional[float]]) -> Dict:
    pred = probabilidades.argmax(axis=1)
    corridas_norm = {c.id for c in corridas if FAMILIA_DE_CLASE[c.clase] == "NORM"}
    deteccion = tiempos_confirmacion(m, probabilidades, corridas, inicios)
    falsas = falsas_alarmas(m, probabilidades, corridas_norm)
    f1_primeros = primeros_s(m, probabilidades)
    conteo = {f: sum(1 for c in corridas if FAMILIA_DE_CLASE[c.clase] == f) for f in FAMILIAS}
    return {
        "aviso": AVISO_REPORTE,
        "conjunto_prueba": {
            "corridas": [c.id for c in corridas],
            "corridas_por_familia": conteo,
            "muestras": int(len(m)),
            "advertencia": f"Conjunto de prueba pequeño ({len(corridas)} corridas): las métricas tienen mucha incertidumbre.",
        },
        "global": metricas(m.y, pred),
        "horizontes": por_horizonte(m, probabilidades),
        "primeros_30s": {"f1_macro": f1_primeros},
        "deteccion": deteccion,
        "resumen_deteccion": resumen_deteccion(deteccion),
        "falsas_alarmas": falsas,
        "metas": metas(deteccion, falsas, f1_primeros, bool(corridas_norm)),
    }


def evaluar(modelo, m: Muestras, corridas: List[Corrida], inicios: Dict[str, Optional[float]]) -> Dict:
    from clasificador_etapa1.entrenamiento import predecir

    return evaluar_probabilidades(m, predecir(modelo, m.x), corridas, inicios)


def _fmt(valor, decimales: int = 3) -> str:
    if valor is None:
        return "—"
    if isinstance(valor, float):
        return f"{valor:.{decimales}f}"
    return str(valor)


def formatear_reporte(reporte: Dict) -> str:
    lineas = ["REPORTE DEL CLASIFICADOR DE ETAPA 1 (PWR 3L)", f"Aviso: {reporte['aviso']}", ""]
    datos = reporte["conjunto_prueba"]
    lineas += ["== 1. Conjunto de prueba ==",
               f"Corridas: {len(datos['corridas'])} ({', '.join(f'{f} {n}' for f, n in datos['corridas_por_familia'].items())})"
               f" | Muestras: {datos['muestras']}",
               f"Advertencia: {datos['advertencia']}", ""]
    if "entrenamiento" in reporte:
        e = reporte["entrenamiento"]
        lineas += ["== 2. Entrenamiento ==",
                   f"Pesos de clase (NORM, LOCA, TRANS): {', '.join(_fmt(p) for p in e['pesos_clase'])}",
                   f"Mejor época: {e['mejor_epoca']} de {e['epocas_ejecutadas']} | F1 macro de validación: {_fmt(e['f1_validacion'])}",
                   ""]
    g = reporte["global"]
    lineas += ["== 3. Métricas globales (todas las muestras de prueba) ==",
               f"{'Familia':<8}{'Precisión':>11}{'Exhaust.':>10}{'F1':>8}{'Muestras':>10}"]
    for familia, v in g["por_familia"].items():
        lineas.append(f"{familia:<8}{_fmt(v['precision']):>11}{_fmt(v['exhaustividad']):>10}{_fmt(v['f1']):>8}{v['soporte']:>10}")
    lineas += [f"F1 macro: {_fmt(g['f1_macro'])}",
               "Matriz de confusión (filas = real, columnas = predicho; NORM, LOCA, TRANS):"]
    lineas += [f"  {fila}" for fila in g["matriz"]]
    lineas += ["", "== 4. Por horizonte (segundos desde el inicio del evento) ==",
               f"{'Horizonte':<11}{'Eventos':>8}{'Exh. LOCA':>11}{'Exh. TRANS':>12}{'F1 macro':>10}"]
    for h in reporte["horizontes"]:
        lineas.append(f"{str(h['h']) + ' s':<11}{h['eventos']:>8}{_fmt(h['exhaustividad']['LOCA']):>11}"
                      f"{_fmt(h['exhaustividad']['TRANS']):>12}{_fmt(h['f1_macro']):>10}")
    lineas += [f"F1 macro de los primeros 30 s (+ operación normal): {_fmt(reporte['primeros_30s']['f1_macro'])}",
               "", "== 5. Tiempo de confirmación por corrida (≥ 0,80 dos segundos seguidos) =="]
    for d in reporte["deteccion"]:
        area = f" {d['area']} cm²" if d["area"] is not None else ""
        tiempo = f"{d['tiempo_s']:.0f} s" if d["tiempo_s"] is not None else "no detectada"
        lineas.append(f"  {d['corrida']:<6}{d['clase']:<8}{area:<11} inicio {_fmt(d['inicio_s'], 1)} s -> {tiempo}")
    r = reporte["resumen_deteccion"]
    for familia in ("LOCA", "TRANS"):
        v = r[familia]
        lineas.append(f"  {familia}: {v['detectadas']} de {v['corridas']} detectadas; mediana {_fmt(v['mediana_s'], 1)} s; "
                      f"máximo {_fmt(v['maximo_s'], 1)} s")
    fa = reporte["falsas_alarmas"]
    lineas += ["", "== 6. Falsas alarmas (confirmación de LOCA o TRANS en operación normal) =="]
    for nombre, clave in (("Corridas NORM", "corridas_norm"), ("Tramos previos al evento", "tramos_previos")):
        v = fa[clave]
        lineas.append(f"  {nombre}: {v['episodios']} episodios, {v['instantes']} instantes, corridas: {', '.join(v['corridas']) or 'ninguna'}")
    lineas += ["", "== 7. Metas =="]
    for sc, v in reporte["metas"].items():
        estado = "sin datos" if v["cumple"] == "sin datos" else ("CUMPLE" if v["cumple"] else "NO CUMPLE")
        lineas.append(f"  {sc} ({v['meta']}): {v['valor']} -> {estado}")
    return "\n".join(lineas) + "\n"
