"""Resumen por conjunto y reporte impreso de la regla de ATWS (contracts/cli.md y salidas.md)."""
import json
from typing import Dict, List, Sequence

from preparacion_pwr3l.config import CONJUNTOS
from regla_atws.config import AVISO, ESPERA_S, META_S, PUNTO_ALTO_FLUJO
from regla_atws.regla import Regla, Resultado

SECCIONES = (
    "1. Configuración",
    "2. Regla calibrada",
    "3. Resultados por conjunto",
    "4. Tiempos de detección",
    "5. Errores",
    "6. Advertencias",
    "7. Limitaciones",
    "8. Artefactos escritos",
)

LIMITACIONES = [
    "La señal de demanda de disparo (primera señal del sistema de protección o PWNT ≥ 118 %) y sus "
    "retardos salen del simulador; están pendientes de validar con la experta, como pide KAN-22.",
    "En los ATWS el registro de eventos de PCTran puede omitir la señal real de disparo (R91 no registra "
    "«Scram High Prz Level», que sí aparece en su gemela R99): la demanda puede salir más tarde de lo real.",
    "El tiempo de detección medido desde la demanda queda entre 2 y 3 s por construcción (espera de 2 s y "
    "muestreo de 1 s); el tiempo informativo es el que se mide desde la señal del anunciador.",
    "Pocas corridas: unas 3 ATWS en validación y 3 en prueba, así que las cifras tienen mucha incertidumbre.",
    "Datos de un único simulador, sin ruido de sensores: en planta el flujo y las señales tendrían ruido y retardos.",
]


def resumir(resultados: Sequence[Resultado], regla: Regla) -> dict:
    por_conjunto: Dict[str, Dict[str, int]] = {}
    tiempos: Dict[str, dict] = {}
    errores: List[dict] = []
    for conjunto in CONJUNTOS:
        propios = [r for r in resultados if r.conjunto == conjunto]
        detectados = [r for r in propios if r.es_atws and r.recomendacion == "posible ATWS"]
        por_conjunto[conjunto] = {
            "atws_detectados": len(detectados),
            "atws_omitidos": sum(1 for r in propios if r.es_atws and r.recomendacion != "posible ATWS"),
            "falsas_alarmas": sum(1 for r in propios if not r.es_atws and r.recomendacion == "posible ATWS"),
            "rechazos_correctos": sum(1 for r in propios if not r.es_atws and r.recomendacion != "posible ATWS"),
            "total": len(propios),
        }
        valores = [r.t_deteccion_demanda for r in detectados]
        tiempos[conjunto] = {
            "detectados": len(detectados),
            "min_s": min(valores) if valores else None,
            "max_s": max(valores) if valores else None,
            "cumplen_meta": sum(1 for v in valores if v <= META_S),
        }
        for r in propios:
            if not r.acierto:
                errores.append({"id": r.id, "conjunto": conjunto, "tipo": "omision" if r.es_atws else "falsa_alarma",
                                "pwnt_decision_pct": None if r.pwnt_decision is None else round(r.pwnt_decision, 4)})
    advertencias = [
        f"{r.id} ({r.conjunto}): tipo de señal «{r.tipo_senal}» no visto en entrenamiento; se usó el mayor retardo "
        f"({r.retardo:g} s)."
        for r in resultados if r.retardo_por_defecto
    ]
    advertencias += [f"{r.id} ({r.conjunto}): ATWS sin demanda de disparo; queda como omisión."
                     for r in resultados if r.es_atws and r.motivo == "sin demanda"]
    advertencias += [f"{r.id} ({r.conjunto}): la decisión cae fuera de la ventana de 300 s."
                     for r in resultados if r.motivo == "decisión fuera de la ventana"]
    if regla.solape:
        advertencias.append(
            f"En entrenamiento los flujos de ATWS y no-ATWS se solapan: {regla.falsas_alarmas_entrenamiento} "
            "falsas alarmas de entrenamiento con el umbral elegido."
        )
    return {
        "version_formato": 1,
        "por_conjunto": por_conjunto,
        "errores": errores,
        "tiempos": tiempos,
        "advertencias": advertencias,
        "limitaciones": list(LIMITACIONES),
        "aviso": AVISO,
    }


def serializar_resumen(resumen: dict) -> str:
    return json.dumps(resumen, indent=2, ensure_ascii=False) + "\n"


def _titulo(numero: int) -> str:
    return f"\n== {SECCIONES[numero - 1]} =="


def formatear_reporte(origen, semilla, regla: Regla, resumen: dict, resultados, artefactos) -> str:
    lineas = [
        "REPORTE DE LA REGLA DE ATWS (PWR 3L)",
        "RECOMENDACIÓN PARA EL OPERADOR: la regla no actúa sobre la planta ni sustituye la protección.",
    ]
    lineas += [_titulo(1), f"Origen: {origen}",
               f"Semilla: {semilla} (reparto de 004) | espera {ESPERA_S:g} s | alto flujo {PUNTO_ALTO_FLUJO:g} % | "
               f"meta: ≤ {META_S:g} s desde la demanda de disparo"]
    lineas += [_titulo(2), f"Calibrada solo con entrenamiento. Umbral: PWNT > {regla.umbral:.1f} % del inicial.",
               "Retardos de la lógica (s): " + ", ".join(f"{t} {v:g}" for t, v in regla.retardos.items())
               + f" | tipo no visto: {regla.retardo_por_defecto:g}",
               f"Margen: ATWS mínimo {regla.minimo_atws:.1f} %, no-ATWS máximo {regla.maximo_no_atws:.1f} %"
               + (" (SOLAPE)" if regla.solape else f", separación {regla.minimo_atws - regla.maximo_no_atws:.1f} puntos")]
    lineas += [_titulo(3), f"{'Conjunto':<10}{'Detect.':>9}{'Omit.':>7}{'F. alarm.':>11}{'Rech. ok':>10}{'Total':>7}"]
    for conjunto, c in resumen["por_conjunto"].items():
        lineas.append(f"{conjunto:<10}{c['atws_detectados']:>9}{c['atws_omitidos']:>7}{c['falsas_alarmas']:>11}"
                      f"{c['rechazos_correctos']:>10}{c['total']:>7}")
    lineas += [_titulo(4)]
    for r in resultados:
        if r.es_atws and r.recomendacion == "posible ATWS":
            lineas.append(f"- {r.id} ({r.conjunto}): {r.tipo_senal} [{r.fuente_senal}] a {r.t_senal:g} s, demanda "
                          f"{r.t_demanda:g} s, decisión {r.t_decision} s → {r.t_deteccion_demanda:g} s desde la demanda, "
                          f"{r.t_deteccion_senal:g} s desde la señal (PWNT {r.pwnt_decision:.1f} %)")
    for conjunto, t in resumen["tiempos"].items():
        lineas.append(f"  {conjunto}: {t['cumplen_meta']} de {t['detectados']} detectados en ≤ {META_S:g} s")
    lineas += [_titulo(5)]
    lineas += [f"- {e['id']} ({e['conjunto']}): {e['tipo'].replace('_', ' ')}, PWNT en la decisión "
               f"{'—' if e['pwnt_decision_pct'] is None else format(e['pwnt_decision_pct'], '.1f') + ' %'}"
               for e in resumen["errores"]] or ["Ninguno."]
    lineas += [_titulo(6)] + ([f"- {a}" for a in resumen["advertencias"]] or ["Ninguna."])
    lineas += [_titulo(7)] + [f"- {x}" for x in resumen["limitaciones"]]
    lineas += [_titulo(8)] + [f"- {a}" for a in artefactos]
    return "\n".join(lineas) + "\n"
