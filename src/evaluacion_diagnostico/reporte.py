"""Formateo y serialización del reporte de evaluación diagnóstica en JSON y texto."""
from typing import Dict, List, Optional

from evaluacion_diagnostico.config import AVISO, UMBRAL_DEFAULT


def _fmt_ci(ci: Optional[List[Optional[float]]], decimales: int = 3) -> str:
    if not ci or ci[0] is None or ci[1] is None:
        return "—"
    return f"[{ci[0]:.{decimales}f}, {ci[1]:.{decimales}f}]"


def _fmt(val: Optional[float], decimales: int = 3) -> str:
    if val is None:
        return "—"
    return f"{val:.{decimales}f}"


def construir_reporte_json(
    val_metrics: Dict,
    test_metrics: Dict,
    cv_summary: Dict,
    umbral: float = UMBRAL_DEFAULT,
) -> Dict:
    """Consolida las métricas de validación, prueba y validación cruzada en el diccionario canónico."""
    return {
        "aviso": AVISO,
        "umbral_abstencion": umbral,
        "nivel_confianza_intervalos": 0.95,
        "validacion": val_metrics,
        "prueba": test_metrics,
        "validacion_cruzada": cv_summary,
    }


def _tabla_matriz(cm: List[List[int]], row_names: List[str], col_names: List[str]) -> List[str]:
    lineas = []
    encabezado = f"{'Real \\ Pred':<14}" + "".join(f"{c:>12}" for c in col_names) + f"{'Total':>10}"
    lineas.append(encabezado)
    for r_idx, r_name in enumerate(row_names):
        fila = cm[r_idx]
        total_fila = sum(fila)
        fila_str = f"{r_name:<14}" + "".join(f"{v:>12}" for v in fila) + f"{total_fila:>10}"
        lineas.append(fila_str)
    return lineas


def formatear_reporte_texto(reporte: Dict) -> str:
    """Genera la representación en texto legible del reporte consolidado de evaluación."""
    lineas = [
        "================================================================================",
        "             REPORTE DE EVALUACIÓN DEL DIAGNÓSTICO (PWR 3L)",
        "================================================================================",
        f"Aviso: {reporte['aviso']}",
        f"Criterio de abstención: confianza softmax mínima < {reporte['umbral_abstencion']:.2f} -> UNCERTAIN",
        f"Intervalos de confianza: 95 % (Wilson score interval para proporciones)",
        "",
    ]

    for nombre_bloque, clave in [("1. Conjunto de Validación (val)", "validacion"), ("2. Conjunto de Prueba (test)", "prueba")]:
        b = reporte.get(clave, {})
        lineas += [
            f"== {nombre_bloque} ==",
            f"Muestras evaluadas: {b.get('n_muestras', 0)}",
            "",
            f"  Exactitud con abstención (UNCERTAIN = error): {_fmt(b.get('exactitud_con_abstencion'))}  IC 95%: {_fmt_ci(b.get('exactitud_con_abstencion_ci'))}",
            f"  Tasa de abstención (UNCERTAIN):              {_fmt(b.get('tasa_abstencion'))}  IC 95%: {_fmt_ci(b.get('tasa_abstencion_ci'))} ({b.get('abstenciones', 0)} muestras)",
            f"  Errores con confianza alta (>= {reporte['umbral_abstencion']:.2f}):          {_fmt(b.get('tasa_errores_alta_confianza'))}  IC 95%: {_fmt_ci(b.get('tasa_errores_alta_confianza_ci'))} ({b.get('errores_alta_confianza', 0)} muestras)",
            f"  Exactitud sobre muestras decididas:          {_fmt(b.get('exactitud_decididas'))}  IC 95%: {_fmt_ci(b.get('exactitud_decididas_ci'))}",
            f"  Exactitud estándar (argmax sin abstención):   {_fmt(b.get('exactitud_estandar'))}",
            "",
            "  Matriz de confusión rectangular con abstención:",
        ]
        if b.get("matriz_confusion_3x4"):
            lineas += ["  " + l for l in _tabla_matriz(b["matriz_confusion_3x4"], b["row_class_names"], b["col_class_names"])]

        err_list = b.get("lista_errores_alta_confianza", [])
        if err_list:
            lineas += ["", f"  Detalle de errores cometidos con confianza alta ({len(err_list)}):"]
            for err in err_list:
                lineas.append(f"    - Muestra #{err['indice']}: Real={err['clase_real']} -> Predicho={err['clase_predicha']} (Confianza={_fmt(err['confianza'])})")
        else:
            lineas += ["", "  Detalle de errores cometidos con confianza alta: 0 errores."]
        lineas.append("")

    # Validación cruzada
    cv = reporte.get("validacion_cruzada", {})
    resumen_cv = cv.get("resumen", {})
    k = cv.get("k_folds", 5)
    lineas += [
        f"== 3. Validación Cruzada Agrupada (Group K-Fold, k={k}) ==",
        "Garantía de no fuga: severidades pareadas y gemelos ATWS agrupados íntegramente por fold.",
        "",
        f"{'Métrica':<35}{'Media':>10}{'Std':>10}{'IC 95% (t-Student)':>22}",
        "-" * 77,
    ]

    for etiqueta, clave in [
        ("Exactitud con abstención", "exactitud_con_abstencion"),
        ("Tasa de abstención", "tasa_abstencion"),
        ("Tasa errores alta confianza", "tasa_errores_alta_confianza"),
        ("Exactitud sobre decididas", "exactitud_decididas"),
        ("Exactitud estándar (argmax)", "exactitud_estandar"),
    ]:
        item = resumen_cv.get(clave, {})
        lineas.append(f"{etiqueta:<35}{_fmt(item.get('media')):>10}{_fmt(item.get('std')):>10}{_fmt_ci(item.get('ci_95')):>22}")

    lineas.append("")
    lineas.append("  Detalle por fold:")
    for f in cv.get("folds", []):
        lineas.append(
            f"    - Fold {f.get('fold')}: Exactitud={_fmt(f.get('exactitud_con_abstencion'))} | "
            f"Abstención={_fmt(f.get('tasa_abstencion'))} | Errores alta conf={_fmt(f.get('tasa_errores_alta_confianza'))} "
            f"({f.get('n_muestras', 0)} muestras, {f.get('n_corridas_test', 0)} corridas)"
        )

    lineas.append("")
    lineas.append("================================================================================")
    return "\n".join(lineas) + "\n"
