"""Evaluación del clasificador de Etapa 2 con abstención (UNCERTAIN), por horizonte, corrida y área (009)."""
from typing import Dict, List, Optional

import numpy as np

from clasificador_etapa1.muestras import Muestras
from clasificador_etapa2.config import (
    AREA_META_CM2,
    AVISO_REPORTE,
    CLASES,
    CONFIRMACION_S,
    ETIQUETA,
    HORIZONTES_S,
    INCIERTO,
    LATENCIA_META_S,
    MIN_CORRIDAS_PRUEBA,
    PRIMEROS_S,
    RANGOS_AREA,
    UMBRAL,
)
from clasificador_etapa2.entrenamiento import predecir
from preparacion_pwr3l.descubrimiento import Corrida


def decidir(probabilidades: np.ndarray, umbral: float = UMBRAL) -> np.ndarray:
    """Devuelve el índice de la rama recomendada (0=LOCA, 1=LOCAC) o -1 (UNCERTAIN) si max(p) < umbral."""
    if len(probabilidades) == 0:
        return np.empty(0, dtype=np.int64)
    mejores = probabilidades.argmax(axis=1).astype(np.int64)
    confianza = probabilidades.max(axis=1)
    return np.where(confianza >= umbral, mejores, -1)


def metricas_segmento(y: np.ndarray, probabilidades: np.ndarray, umbral: float = UMBRAL) -> Dict:
    """Métricas de un subconjunto de muestras incluyendo la abstención UNCERTAIN.

    Matriz 2 x 3: filas = clase real (LOCA, LOCAC), columnas = predicción (LOCA, LOCAC, UNCERTAIN).
    En precisión/exhaustividad/F1 sobre todas las muestras, UNCERTAIN cuenta como no acierto.
    """
    y = np.asarray(y, dtype=np.int64)
    decisiones = decidir(probabilidades, umbral)
    n = int(len(y))
    matriz = [[0, 0, 0], [0, 0, 0]]
    for real, pred in zip(y, decisiones):
        col = int(pred) if pred >= 0 else 2
        matriz[int(real)][col] += 1

    por_clase: Dict[str, Dict[str, float]] = {}
    f1s: List[float] = []
    for idx, nombre in enumerate(CLASES):
        aciertos = matriz[idx][idx]
        predichos = matriz[0][idx] + matriz[1][idx]
        reales = sum(matriz[idx])
        prec = float(aciertos / predichos) if predichos > 0 else 0.0
        exh = float(aciertos / reales) if reales > 0 else 0.0
        f1 = float(2 * prec * exh / (prec + exh)) if (prec + exh) > 0 else 0.0
        por_clase[nombre] = {
            "precision": round(prec, 6),
            "exhaustividad": round(exh, 6),
            "f1": round(f1, 6),
            "soporte": int(reales),
        }
        f1s.append(f1)

    abstenciones = int(matriz[0][2] + matriz[1][2])
    decididas = n - abstenciones
    aciertos_totales = int(matriz[0][0] + matriz[1][1])
    errores_confianza = int(matriz[0][1] + matriz[1][0])
    cobertura = float(decididas / n) if n > 0 else 0.0
    exactitud_decisiones = float(aciertos_totales / decididas) if decididas > 0 else 0.0

    return {
        "muestras": n,
        "matriz": matriz,
        "por_clase": por_clase,
        "f1_macro": round(float(np.mean(f1s)) if n > 0 else 0.0, 6),
        "abstenciones": abstenciones,
        "cobertura": round(cobertura, 6),
        "exactitud_decisiones": round(exactitud_decisiones, 6),
        "errores_confianza": errores_confianza,
    }


def _primer_confirmado(mascara: np.ndarray, ks: np.ndarray, seguidos: int = CONFIRMACION_S) -> Optional[float]:
    racha = 0
    for activo, k in zip(mascara, ks):
        racha = racha + 1 if activo else 0
        if racha >= seguidos:
            return float(k)
    return None


def confirmacion_corrida(
    corrida: Corrida,
    ks: np.ndarray,
    probabilidades: np.ndarray,
    umbral: float = UMBRAL,
) -> Dict:
    """Evalúa la confirmación de rama (≥ 0,80 durante 2 s seguidos) en una corrida."""
    orden = np.argsort(ks)
    ks_ord = ks[orden]
    probs_ord = probabilidades[orden]
    idx_correcta = ETIQUETA[corrida.clase]
    idx_otra = 1 - idx_correcta

    t_correcta = _primer_confirmado(probs_ord[:, idx_correcta] >= umbral, ks_ord)
    t_erronea = _primer_confirmado(probs_ord[:, idx_otra] >= umbral, ks_ord)
    error_confirmado = t_erronea is not None

    if t_correcta is not None and (t_erronea is None or t_correcta <= t_erronea):
        confirmada = corrida.clase
        correcta = True
        tiempo_s: Optional[float] = t_correcta
    elif t_erronea is not None:
        confirmada = CLASES[idx_otra]
        correcta = False
        tiempo_s = t_erronea
    else:
        confirmada = INCIERTO
        correcta = False
        tiempo_s = None

    return {
        "corrida": corrida.id,
        "clase": corrida.clase,
        "area": corrida.area,
        "confirmada": confirmada,
        "correcta": correcta,
        "tiempo_s": tiempo_s,
        "tiempo_correcta_s": t_correcta,
        "error_confirmado": error_confirmado,
    }


def _agrupar_por_area(resultados_corridas: List[Dict]) -> List[Dict]:
    salida = []
    for etiqueta, minimo, maximo in RANGOS_AREA:
        grupo = [
            r for r in resultados_corridas
            if r["area"] is not None and r["area"] >= minimo and (maximo is None or r["area"] < maximo)
        ]
        correctas = [r for r in grupo if r["correcta"] and not r["error_confirmado"]]
        errores = [r for r in grupo if r["error_confirmado"]]
        sin_dec = [r for r in grupo if r["confirmada"] == INCIERTO]
        tiempos = [r["tiempo_s"] for r in correctas if r["tiempo_s"] is not None]
        salida.append({
            "rango": etiqueta,
            "corridas": len(grupo),
            "correctas": len(correctas),
            "errores": len(errores),
            "sin_decision": len(sin_dec),
            "mediana_s": float(np.median(tiempos)) if tiempos else None,
        })
    return salida


def evaluar_probabilidades(
    muestras: Muestras,
    probabilidades: np.ndarray,
    corridas_prueba: List[Corrida],
) -> Dict:
    """Construye el diccionario completo de evaluación sobre las muestras de prueba."""
    ramas_prueba = [c for c in corridas_prueba if c.clase in CLASES]
    global_m = metricas_segmento(muestras.y, probabilidades)

    mask_30 = (muestras.k >= 0) & (muestras.k <= PRIMEROS_S)
    primeros_30s = metricas_segmento(muestras.y[mask_30], probabilidades[mask_30])

    horizontes = []
    for h in HORIZONTES_S:
        mask_h = muestras.k == h
        seg = metricas_segmento(muestras.y[mask_h], probabilidades[mask_h])
        seg["horizonte_s"] = int(h)
        horizontes.append(seg)

    resultados_corridas = []
    for c in ramas_prueba:
        mask_c = muestras.corrida == c.id
        resultados_corridas.append(
            confirmacion_corrida(c, muestras.k[mask_c], probabilidades[mask_c])
        )

    areas = _agrupar_por_area(resultados_corridas)

    grandes = [r for r in resultados_corridas if (r["area"] or 0) >= AREA_META_CM2]
    grandes_ok = [
        r for r in grandes
        if r["correcta"] and not r["error_confirmado"]
        and r["tiempo_s"] is not None and r["tiempo_s"] <= LATENCIA_META_S
    ]
    sc1_ok = primeros_30s["errores_confianza"] == 0
    sc2_ok = len(grandes) > 0 and len(grandes_ok) == len(grandes)

    advertencias: List[str] = []
    if len(ramas_prueba) < MIN_CORRIDAS_PRUEBA:
        advertencias.append(
            f"El conjunto de prueba tiene solo {len(ramas_prueba)} corridas LOCA/LOCAC: "
            "las métricas tienen alta incertidumbre estadística."
        )
    for nombre in CLASES:
        if global_m["por_clase"][nombre]["soporte"] == 0:
            advertencias.append(f"La rama {nombre} no tiene muestras en el conjunto de prueba.")

    return {
        "aviso": AVISO_REPORTE,
        "global": global_m,
        "primeros_30s": primeros_30s,
        "horizontes": horizontes,
        "corridas": resultados_corridas,
        "areas": areas,
        "metas": {
            "SC-001_sin_errores_confianza_30s": {
                "errores_confianza": primeros_30s["errores_confianza"],
                "exactitud_decisiones": primeros_30s["exactitud_decisiones"],
                "cobertura": primeros_30s["cobertura"],
                "cumple": sc1_ok,
            },
            "SC-002_loca_50cm2_en_10s": {
                "confirmadas_en_10s": len(grandes_ok),
                "total": len(grandes),
                "cumple": sc2_ok,
            },
        },
        "advertencias": advertencias,
    }


def evaluar(modelo, muestras_prueba: Muestras, corridas_prueba: List[Corrida]) -> Dict:
    """Predice con `modelo` y evalúa sobre las corridas LOCA/LOCAC de prueba."""
    probabilidades = predecir(modelo, muestras_prueba.x)
    return evaluar_probabilidades(muestras_prueba, probabilidades, corridas_prueba)


def formatear_reporte(reporte: Dict) -> str:
    """Genera el reporte legible en texto plano para la consola y `reporte.txt`."""
    lineas = [
        "========================================================================",
        "REPORTE DE EVALUACIÓN - CLASIFICADOR ETAPA 2 (RAMA CALIENTE O FRÍA)",
        "========================================================================",
        reporte["aviso"],
        "",
    ]
    g = reporte["global"]
    p30 = reporte["primeros_30s"]
    lineas.append("1. MÉTRICAS GLOBALES Y PRIMEROS 30 S (CON ABSTENCIÓN UNCERTAIN < 0.80)")
    lineas.append(
        f"   Global ({g['muestras']} muestras): F1 macro={g['f1_macro']:.3f} | "
        f"cobertura={g['cobertura']:.3f} | exactitud decisiones={g['exactitud_decisiones']:.3f} | "
        f"errores con confianza={g['errores_confianza']}"
    )
    lineas.append(
        f"   Primeros 30 s ({p30['muestras']} muestras): F1 macro={p30['f1_macro']:.3f} | "
        f"cobertura={p30['cobertura']:.3f} | exactitud decisiones={p30['exactitud_decisiones']:.3f} | "
        f"errores con confianza={p30['errores_confianza']}"
    )
    for nombre in CLASES:
        c = g["por_clase"][nombre]
        lineas.append(
            f"   - {nombre:<5}: P={c['precision']:.3f}  R={c['exhaustividad']:.3f}  "
            f"F1={c['f1']:.3f}  (soporte={c['soporte']})"
        )
    m = g["matriz"]
    lineas.append("   Matriz (filas=real [LOCA, LOCAC], columnas=[LOCA, LOCAC, UNCERTAIN]):")
    lineas.append(f"     LOCA : {m[0]}")
    lineas.append(f"     LOCAC: {m[1]}")
    lineas.append("")

    lineas.append("2. DESEMPEÑO POR HORIZONTE DESDE EL INICIO DEL EVENTO")
    lineas.append("   h(s) | muestras | F1 macro | cobertura | exactitud dec. | errores conf.")
    for h in reporte["horizontes"]:
        lineas.append(
            f"   {h['horizonte_s']:>4} | {h['muestras']:>8} | {h['f1_macro']:>8.3f} | "
            f"{h['cobertura']:>9.3f} | {h['exactitud_decisiones']:>14.3f} | {h['errores_confianza']:>13}"
        )
    lineas.append("")

    lineas.append("3. RESULTADO POR CORRIDA DE PRUEBA")
    for c in reporte["corridas"]:
        tiempo = "sin decisión" if c["tiempo_s"] is None else f"{c['tiempo_s']:.0f} s"
        err = " [ERROR CONFIRMADO]" if c["error_confirmado"] else ""
        lineas.append(
            f"   - {c['corrida']} ({c['clase']}, {c['area']} cm²): "
            f"confirmada={c['confirmada']} ({tiempo}){err}"
        )
    lineas.append("")

    lineas.append("4. AGRUPACIÓN POR TAMAÑO DE ROTURA")
    for a in reporte["areas"]:
        med = "-" if a["mediana_s"] is None else f"{a['mediana_s']:.1f} s"
        lineas.append(
            f"   - {a['rango']:<12}: corridas={a['corridas']}, correctas={a['correctas']}, "
            f"errores={a['errores']}, sin decisión={a['sin_decision']} (mediana={med})"
        )
    lineas.append("")

    lineas.append("5. METAS DE ÉXITO")
    sc1 = reporte["metas"]["SC-001_sin_errores_confianza_30s"]
    sc2 = reporte["metas"]["SC-002_loca_50cm2_en_10s"]
    lineas.append(
        f"   - SC-001 (0 errores con confianza en primeros 30 s): "
        f"{sc1['errores_confianza']} errores -> {'CUMPLE' if sc1['cumple'] else 'NO CUMPLE'}"
    )
    lineas.append(
        f"   - SC-002 (roturas >= 50 cm² confirmadas en <= 10 s): "
        f"{sc2['confirmadas_en_10s']}/{sc2['total']} -> {'CUMPLE' if sc2['cumple'] else 'NO CUMPLE'}"
    )
    if reporte["advertencias"]:
        lineas.append("")
        lineas.append("6. ADVERTENCIAS")
        for adv in reporte["advertencias"]:
            lineas.append(f"   * {adv}")
    lineas.append("")
    return "\n".join(lineas)

