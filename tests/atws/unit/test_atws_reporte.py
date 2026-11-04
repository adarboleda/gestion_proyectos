"""Resumen y reporte de la regla de ATWS (US3)."""
import pytest

from regla_atws.config import AVISO
from regla_atws.regla import Regla, Resultado
from regla_atws.reporte import SECCIONES, formatear_reporte, resumir


def _r(rid, clase, conjunto, recomendacion, motivo, pwnt=None, por_defecto=False, demanda=None):
    es_atws = clase == "ATWS"
    detectado = recomendacion == "posible ATWS"
    r = Resultado(rid, clase, conjunto, es_atws, "turbine trip" if motivo != "sin demanda" else None,
                  "registro" if motivo != "sin demanda" else None, 45.5 if motivo != "sin demanda" else None,
                  5.0 if motivo != "sin demanda" else None, por_defecto, demanda, None if demanda is None else 53,
                  pwnt, recomendacion, motivo, detectado == es_atws)
    if detectado and es_atws:
        r.t_deteccion_demanda, r.t_deteccion_senal = 2.5, 7.5
    return r


@pytest.fixture
def regla():
    return Regla(21.4, {"turbine trip": 5.0}, 5.0, 2.0, 37.0, 5.7, False, 0)


@pytest.fixture
def resultados():
    return [
        _r("R47", "ATWS", "train", "posible ATWS", "flujo alto", 55.0, demanda=50.5),
        _r("R54", "TRIP_OK", "train", "sin ATWS", "flujo caído", 6.0, demanda=50.5),
        _r("R31", "NORM", "train", "sin ATWS", "sin demanda"),
        _r("R49", "ATWS", "val", "posible ATWS", "flujo alto", 40.0, por_defecto=True, demanda=34.0),
        _r("R97", "ATWS", "test", "sin ATWS", "sin demanda"),
        _r("R56", "TRIP_OK", "test", "posible ATWS", "flujo alto", 30.0, demanda=34.0),
    ]


def test_tabla_por_conjunto(resultados, regla):
    resumen = resumir(resultados, regla)
    assert resumen["por_conjunto"]["train"] == {"atws_detectados": 1, "atws_omitidos": 0, "falsas_alarmas": 0,
                                               "rechazos_correctos": 2, "total": 3}
    assert resumen["por_conjunto"]["val"]["atws_detectados"] == 1
    assert resumen["por_conjunto"]["test"] == {"atws_detectados": 0, "atws_omitidos": 1, "falsas_alarmas": 1,
                                              "rechazos_correctos": 0, "total": 2}
    assert sum(c["total"] for c in resumen["por_conjunto"].values()) == len(resultados)


def test_errores_nombrados(resultados, regla):
    errores = {(e["id"], e["tipo"]) for e in resumir(resultados, regla)["errores"]}
    assert errores == {("R97", "omision"), ("R56", "falsa_alarma")}


def test_tiempos_y_meta(resultados, regla):
    tiempos = resumir(resultados, regla)["tiempos"]
    assert tiempos["train"] == {"detectados": 1, "min_s": 2.5, "max_s": 2.5, "cumplen_meta": 1}
    assert tiempos["test"]["detectados"] == 0 and tiempos["test"]["min_s"] is None


def test_advertencias(resultados, regla):
    texto = " ".join(resumir(resultados, regla)["advertencias"])
    assert "R49" in texto and "no visto en entrenamiento" in texto
    assert "R97" in texto and "sin demanda" in texto


def test_limitaciones_y_aviso(resultados, regla):
    resumen = resumir(resultados, regla)
    texto = " ".join(resumen["limitaciones"]).lower()
    for palabra in ("experta", "registro de eventos", "ruido", "por construcción", "pocas"):
        assert palabra in texto, palabra
    assert resumen["aviso"] == AVISO


def test_reporte_con_las_ocho_secciones_y_el_aviso(resultados, regla):
    resumen = resumir(resultados, regla)
    texto = formatear_reporte("PWR 3L", 42, regla, resumen, resultados, ["regla.json", "resumen.json"])
    assert texto.startswith("REPORTE DE LA REGLA DE ATWS (PWR 3L)")
    assert "RECOMENDACIÓN PARA EL OPERADOR" in texto.splitlines()[1]
    posiciones = [texto.index(f"== {s} ==") for s in SECCIONES]
    assert posiciones == sorted(posiciones) and len(SECCIONES) == 8
    assert "R97" in texto and "R56" in texto and "21.4" in texto and "resumen.json" in texto
