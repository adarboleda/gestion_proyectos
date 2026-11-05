"""Markdown del Hito 1, listo para la presentación (contracts/cli.md)."""
from typing import Dict, List

SECCIONES = (
    "1. Aviso consultivo",
    "2. Metas del Hito 1",
    "3. Matriz de confusión con abstención (prueba)",
    "4. Abstención y errores con confianza alta",
    "5. Validación cruzada",
    "6. Tiempos de detección por corrida (prueba)",
    "7. Regla de ATWS",
    "8. Etapa 2 (rama caliente o fría)",
    "9. Falsas alarmas",
    "10. Lectura honesta y limitaciones",
    "11. Fuentes y reproducción",
)
CONJUNTOS = {"train": "Entrenamiento", "val": "Validación", "test": "Prueba"}
NOMBRES_VC = {"exactitud_con_abstencion": "Exactitud con abstención", "tasa_abstencion": "Tasa de abstención",
              "tasa_errores_alta_confianza": "Errores con confianza alta", "exactitud_decididas": "Exactitud de las decididas",
              "exactitud_estandar": "Exactitud estándar"}


def _pct(valor) -> str:
    return "—" if valor is None else f"{valor * 100:.1f} %"


def _ic(par) -> str:
    return "—" if not par or par[0] is None else f"[{par[0] * 100:.1f} %, {par[1] * 100:.1f} %]"


def _s(valor) -> str:
    return "—" if valor is None else f"{valor:g} s"


def _seccion(numero: int) -> List[str]:
    return ["", f"## {SECCIONES[numero - 1]}", ""]


def formatear_markdown(hito: Dict) -> str:
    d, prueba = hito["diagnostico"], hito["diagnostico"]["prueba"]
    l = ["# Hito 1 — Resultados preliminares del diagnóstico rápido (PWR 3L)", "",
         f"> **{hito['aviso']}**", "", "KAN-27 · Fase 2 · consolidado de KAN-22, KAN-23, KAN-24, KAN-25 y KAN-26."]
    l += _seccion(1) + [hito["aviso"]]

    l += _seccion(2) + ["| Meta | Fuente | Definición | Conjunto | Valor | Estado |", "|---|---|---|---|---|---|"]
    l += [f"| {m['id']} | {m['fuente']} | {m['definicion']} | {m['conjunto']} | {m['valor']} | **{m['estado']}** |"
          for m in hito["metas"]]

    l += _seccion(3) + [f"Fuente: KAN-26 (011), {prueba['n_muestras']} segundos de prueba, umbral de confianza {d['umbral']}. "
                        "Filas: familia verdadera; columnas: recomendación.", "",
                        "| Verdadera \\ Recomendada | " + " | ".join(prueba["columnas"]) + " |",
                        "|---" * (len(prueba["columnas"]) + 1) + "|"]
    l += [f"| {fila} | " + " | ".join(str(v) for v in valores) + " |" for fila, valores in zip(prueba["filas"], prueba["matriz"])]
    l += ["", "F1 por familia de la Etapa 1 (KAN-23, 005, prueba): "
          + ", ".join(f"{f} {v['f1']:.3f}" for f, v in (hito["etapa1"]["por_familia"] or {}).items())
          + f"; F1 macro {hito['etapa1']['f1_macro']:.3f}; F1 macro de los primeros 30 s {hito['etapa1']['f1_primeros_30s']:.3f}."]

    l += _seccion(4) + ["Fuente: KAN-26 (011). Intervalos de Wilson al 95 %. Las tres primeras filas suman 100 %.", "",
                        "| Medida | Prueba | IC 95 % | Validación | IC 95 % |", "|---|---|---|---|---|"]
    val = d["validacion"]
    for nombre, clave in (("Exactitud con abstención", "exactitud_con_abstencion"), ("Tasa de abstención", "tasa_abstencion"),
                          ("Errores con confianza alta", "tasa_errores_alta_confianza"), ("Exactitud de las decididas", "exactitud_decididas")):
        l.append(f"| {nombre} | {_pct(prueba[clave])} | {_ic(prueba.get(clave + '_ci'))} | {_pct(val[clave])} | {_ic(val.get(clave + '_ci'))} |")

    vc = d["validacion_cruzada"]
    l += _seccion(5) + [f"Fuente: KAN-26 (011). Group K-Fold, k = {vc['k']}, sin partir áreas ni gemelas. La validación cruzada "
                        f"**reentrena** la Etapa 1 en cada fold ({vc['epocas_por_fold']} épocas), mientras que prueba y validación "
                        "(secciones 3 y 4) usan el **modelo publicado** por `entrenar-etapa1`.", "",
                        "| Medida | Media | Desv. típ. | IC 95 % (t de Student) |", "|---|---|---|---|"]
    for clave, v in vc["resumen"].items():
        l.append(f"| {NOMBRES_VC.get(clave, clave)} | {_pct(v['media'])} | {_pct(v['std'])} | {_ic(v['ci_95'])} |")

    l += _seccion(6) + ["Fuente: KAN-25 (008). Tiempo desde la falla hasta la familia confirmada (Etapa 1) y, en los ATWS, "
                        "desde la demanda de disparo hasta «posible ATWS» (regla de 006).", "",
                        "| Corrida | Clase | Área (cm²) | Falla | Diagnóstico | ATWS desde la demanda |", "|---|---|---|---|---|---|"]
    for t in hito["tiempos"]:
        falla = "—" if t["falla_s"] is None else f"{t['falla_s']:g} s ({t['falla_fuente']}{', incierta' if t['incierta'] else ''})"
        l.append(f"| {t['corrida']} | {t['clase']} | {t['area'] if t['area'] is not None else '—'} | {falla} | "
                 f"{_s(t['tiempo_diagnostico_s']) if t['tiempo_diagnostico_s'] is not None else 'no confirmado'} | "
                 f"{_s(t['tiempo_atws_desde_demanda_s'])} |")

    r = hito["regla"]
    l += _seccion(7) + [f"Fuente: KAN-22 (006). Umbral calibrado solo con entrenamiento: PWNT > {r['umbral_pwnt_pct']:.1f} % "
                        f"del inicial (ATWS mínimo {r['margen']['minimo_atws_pct']:.1f} %, no-ATWS máximo "
                        f"{r['margen']['maximo_no_atws_pct']:.1f} %).", "",
                        "| Conjunto | ATWS detectados | Omitidos | Falsas alarmas | Rechazos correctos | ATWS en ≤ 3 s |",
                        "|---|---|---|---|---|---|"]
    for conjunto, c in r["por_conjunto"].items():
        t = r["tiempos"][conjunto]
        l.append(f"| {CONJUNTOS[conjunto]} | {c['atws_detectados']} | {c['atws_omitidos']} | {c['falsas_alarmas']} | "
                 f"{c['rechazos_correctos']} | {t['cumplen_meta']} de {t['detectados']} |")

    e2 = hito["etapa2"]
    l += _seccion(8) + [f"Fuente: KAN-24 (009), prueba ({e2['muestras']} segundos de LOCA/LOCAC). Abstenciones: "
                        f"{e2['abstenciones']} ({_pct(e2['abstenciones'] / e2['muestras'] if e2['muestras'] else None)}); "
                        f"cobertura {_pct(e2['cobertura'])}; F1 macro {e2['f1_macro']:.3f}; errores con confianza "
                        f"{e2['errores_confianza']}."]

    f = hito["falsas_alarmas"]
    l += _seccion(9) + [
        f"- Etapa 1 en corridas NORM de prueba (KAN-23, 005): {f['etapa1_prueba']['episodios']} episodios "
        f"({', '.join(f['etapa1_prueba']['corridas']) or 'ninguna'}); en tramos previos al evento: "
        f"{f['etapa1_tramos_previos']['episodios']}.",
        "- Regla de ATWS (KAN-22, 006): " + (", ".join(f"{e['id']} ({CONJUNTOS[e['conjunto']].lower()})" for e in f["regla"]) or "ninguna") + ".",
        "- Medidas desde la falla (KAN-25, 008): validación " + str(f["tiempos"]["val"]["etapa1"]["corridas_norm"]["episodios"])
        + " de la Etapa 1 y " + str(f["tiempos"]["val"]["regla"]["recomendaciones"]) + " de la regla; prueba "
        + str(f["tiempos"]["test"]["etapa1"]["corridas_norm"]["episodios"]) + " y " + str(f["tiempos"]["test"]["regla"]["recomendaciones"]) + "."]

    no_cumplen = [m for m in hito["metas"] if m["estado"] != "cumple"]
    l += _seccion(10) + ["Metas que no se cumplen o se cumplen sin decisiones:", ""]
    l += [f"- **{m['id']}** ({m['estado']}): {m['valor']}." for m in no_cumplen] or ["- Ninguna."]
    l += ["", "Limitaciones:", ""] + [f"- {x}" for x in hito["limitaciones"]]

    l += _seccion(11) + ["| Tarea | Responsable | Comando | Archivo | SHA-256 |", "|---|---|---|---|---|"]
    l += [f"| {x['kan']} | {x['responsable']} | `{x['comando']}` | `{x['archivo']}` | `{x['sha256'][:12]}…` |"
          for x in hito.get("fuentes", [])]
    l += ["", "Para regenerarlo: ejecutar los comandos de la tabla en este orden y después `informe-hito1` "
          "(ver `specs/007-hito1-resultados/quickstart.md`)."]
    return "\n".join(l) + "\n"
