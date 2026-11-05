"""Consolidación de los resultados de la Fase 2 en el contenido del Hito 1 (sin recalcular métricas)."""
from typing import Dict, List

from informe_hito1.config import AVISO, LIMITACIONES

NOMBRE_CONJUNTO = {"train": "entrenamiento", "val": "validación", "test": "prueba"}


def _estado(cumple) -> str:
    if cumple is True:
        return "cumple"
    if cumple is False:
        return "no cumple"
    return "sin datos"


def _meta(identificador, fuente, definicion, valor, conjunto, estado) -> Dict:
    return {"id": identificador, "fuente": fuente, "definicion": definicion, "valor": valor,
            "conjunto": conjunto, "estado": estado}


def _metas(datos) -> List[Dict]:
    tiempos = datos["tiempos"]["tiempos"]["metas"]
    etapa1 = datos["etapa1"]["reporte"]["metas"]
    etapa2 = datos["etapa2"]["reporte"]["metas"]
    regla = datos["regla"]["resumen"]
    metas = [
        _meta("KAN-25 diagnóstico ≤ 10 s", "KAN-25 (008)", tiempos["diagnostico_10s"]["meta"],
              tiempos["diagnostico_10s"]["valor"], "prueba", _estado(tiempos["diagnostico_10s"]["cumple"])),
        _meta("KAN-25 ATWS ≤ 3 s", "KAN-25 (008)", tiempos["atws_3s"]["meta"], tiempos["atws_3s"]["valor"],
              "validación y prueba", _estado(tiempos["atws_3s"]["cumple"])),
    ]
    for codigo in sorted(etapa1):
        m = etapa1[codigo]
        metas.append(_meta(f"KAN-23 {codigo}", "KAN-23 (005)", m["meta"], m["valor"], "prueba", _estado(m["cumple"])))
    sc1 = etapa2["SC-001_sin_errores_confianza_30s"]
    estado = _estado(sc1["cumple"])
    if sc1["cumple"] is True and not sc1.get("cobertura"):
        estado = "cumple sin decisiones (cobertura 0 %)"
    metas.append(_meta("KAN-24 SC-001", "KAN-24 (009)", "0 errores con confianza alta en los primeros 30 s (rama caliente o fría)",
                       f"{sc1['errores_confianza']} errores; cobertura {sc1['cobertura'] * 100:.0f} %", "prueba", estado))
    sc2 = etapa2["SC-002_loca_50cm2_en_10s"]
    metas.append(_meta("KAN-24 SC-002", "KAN-24 (009)", "LOCA ≥ 50 cm² con su rama confirmada en ≤ 10 s en el 100 %",
                       f"{sc2['confirmadas_en_10s']} de {sc2['total']}", "prueba", _estado(sc2["cumple"])))
    falsas = [e for e in regla["errores"] if e["tipo"] == "falsa_alarma" and e["conjunto"] in ("val", "test")]
    valor = f"{len(falsas)} falsas alarmas" + (f" ({', '.join(e['id'] for e in falsas)})" if falsas else "")
    metas.append(_meta("KAN-22 falsas alarmas", "KAN-22 (006)", "0 «posible ATWS» en corridas que no son ATWS",
                       valor, "validación y prueba", _estado(not falsas)))
    return metas


def _diagnostico(datos) -> Dict:
    evaluacion = datos["diagnostico"]["evaluacion"]
    resultado = {}
    for clave, conjunto in (("prueba", "prueba"), ("validacion", "validacion")):
        c = evaluacion[conjunto]
        suma = c["exactitud_con_abstencion"] + c["tasa_abstencion"] + c["tasa_errores_alta_confianza"]
        if abs(suma - 1.0) > 1e-3:
            raise ValueError(f"Las tasas de {conjunto} de KAN-26 no suman 1 ({suma:.4f}).")
        resultado[clave] = {
            "n_muestras": c["n_muestras"], "matriz": c["matriz_confusion_3x4"], "filas": c["row_class_names"],
            "columnas": c["col_class_names"],
            **{k: c[k] for k in ("exactitud_con_abstencion", "exactitud_con_abstencion_ci", "abstenciones",
                                 "tasa_abstencion", "tasa_abstencion_ci", "errores_alta_confianza",
                                 "tasa_errores_alta_confianza", "tasa_errores_alta_confianza_ci",
                                 "exactitud_decididas", "exactitud_decididas_ci", "exactitud_estandar")},
        }
    vc = evaluacion["validacion_cruzada"]
    resultado["validacion_cruzada"] = {"k": vc["k_folds"], "epocas_por_fold": vc.get("epocas_por_fold"),
                                       "resumen": vc["resumen"]}
    resultado["umbral"] = evaluacion.get("umbral_abstencion")
    return resultado


def _tiempos(datos) -> List[Dict]:
    filas = []
    for c in datos["tiempos"]["tiempos"]["corridas"]:
        if c["conjunto"] != "test" or c["familia"] == "NORM":
            continue
        atws = c.get("atws") or {}
        falla = c.get("falla") or {}
        filas.append({"corrida": c["corrida"], "clase": c["clase"], "area": c.get("area"), "falla_s": falla.get("t"),
                      "falla_fuente": falla.get("fuente"), "incierta": falla.get("incierta"),
                      "tiempo_diagnostico_s": c.get("tiempo_diagnostico_s"),
                      "tiempo_atws_desde_demanda_s": atws.get("tiempo_desde_demanda_s") if atws.get("es_atws") else None})
    return filas


def consolidar(datos: Dict) -> Dict:
    """Contenido del Hito 1 a partir de los datos de `cargar_fuentes` (solo copia y ordena)."""
    etapa1 = datos["etapa1"]["reporte"]
    etapa2 = datos["etapa2"]["reporte"]
    regla_resumen, regla = datos["regla"]["resumen"], datos["regla"]["regla"]
    tiempos = datos["tiempos"]["tiempos"]
    return {
        "version_formato": 1,
        "aviso": AVISO,
        "metas": _metas(datos),
        "diagnostico": _diagnostico(datos),
        "etapa1": {"f1_macro": etapa1["global"]["f1_macro"], "por_familia": etapa1["global"].get("por_familia"),
                   "f1_primeros_30s": etapa1["primeros_30s"]["f1_macro"],
                   "mejor_epoca": etapa1["entrenamiento"].get("mejor_epoca"), "reparto": etapa1.get("reparto")},
        "tiempos": _tiempos(datos),
        "regla": {"por_conjunto": regla_resumen["por_conjunto"], "tiempos": regla_resumen["tiempos"],
                  "umbral_pwnt_pct": regla["umbral_pwnt_pct"], "margen": regla["margen"],
                  "errores": regla_resumen["errores"]},
        "etapa2": {k: etapa2["global"].get(k) for k in ("muestras", "abstenciones", "cobertura", "f1_macro",
                                                        "exactitud_decisiones", "errores_confianza", "matriz")},
        "falsas_alarmas": {
            "etapa1_prueba": etapa1["falsas_alarmas"]["corridas_norm"],
            "etapa1_tramos_previos": etapa1["falsas_alarmas"]["tramos_previos"],
            "tiempos": tiempos["falsas_alarmas"],
            "regla": [{"id": e["id"], "conjunto": e["conjunto"]} for e in regla_resumen["errores"] if e["tipo"] == "falsa_alarma"],
        },
        "limitaciones": list(LIMITACIONES),
    }
