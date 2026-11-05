"""Consolidación: metas, matriz con abstención, validación cruzada, tiempos, regla, Etapa 2 y falsas alarmas."""
import pytest

from informe_hito1.consolidar import consolidar


def _meta(hito, identificador):
    return next(m for m in hito["metas"] if m["id"] == identificador)


def test_metas_del_hito_copiadas_de_008(datos):
    hito = consolidar(datos)
    diag = _meta(hito, "KAN-25 diagnóstico ≤ 10 s")
    assert diag["valor"] == "10 de 10 (100 %)" and diag["estado"] == "cumple" and diag["conjunto"] == "prueba"
    assert diag["definicion"].startswith("familia del evento confirmada en ≤ 10 s")
    atws = _meta(hito, "KAN-25 ATWS ≤ 3 s")
    assert atws["estado"] == "cumple" and atws["conjunto"] == "validación y prueba"


def test_metas_de_005_y_009(datos):
    hito = consolidar(datos)
    assert _meta(hito, "KAN-23 SC-002")["estado"] == "no cumple"
    assert _meta(hito, "KAN-23 SC-002")["valor"] == "3 falsas alarmas en corridas NORM"
    assert _meta(hito, "KAN-24 SC-002")["estado"] == "no cumple"


def test_meta_cumplida_sin_decisiones_se_marca(datos):
    meta = _meta(consolidar(datos), "KAN-24 SC-001")
    assert meta["estado"] == "cumple sin decisiones (cobertura 0 %)"


def test_meta_de_falsas_alarmas_de_la_regla(datos):
    meta = _meta(consolidar(datos), "KAN-22 falsas alarmas")
    assert meta["estado"] == "no cumple" and "1" in meta["valor"] and "R54" in meta["valor"]


def test_matriz_con_abstencion_y_tasas_que_suman_uno(datos):
    diagnostico = consolidar(datos)["diagnostico"]["prueba"]
    assert diagnostico["matriz"] == [[1107, 0, 12, 74], [12, 1285, 0, 2], [0, 92, 1250, 1]]
    assert diagnostico["columnas"] == ["NORM", "LOCA", "TRANS", "UNCERTAIN"]
    suma = diagnostico["exactitud_con_abstencion"] + diagnostico["tasa_abstencion"] + diagnostico["tasa_errores_alta_confianza"]
    assert suma == pytest.approx(1.0, abs=1e-3)
    assert diagnostico["tasa_abstencion_ci"] == [0.016, 0.025]


def test_tasas_que_no_suman_uno_detienen(datos):
    datos["diagnostico"]["evaluacion"]["prueba"]["tasa_abstencion"] = 0.5
    with pytest.raises(ValueError, match="no suman 1"):
        consolidar(datos)


def test_validacion_cruzada(datos):
    vc = consolidar(datos)["diagnostico"]["validacion_cruzada"]
    assert vc["k"] == 5 and vc["resumen"]["tasa_abstencion"]["media"] == 0.3281


def test_tiempos_solo_de_prueba(datos):
    tiempos = consolidar(datos)["tiempos"]
    assert [t["corrida"] for t in tiempos] == ["R44", "R29"]
    assert tiempos[1]["tiempo_atws_desde_demanda_s"] == 2.0 and tiempos[0]["tiempo_diagnostico_s"] == 4.0


def test_regla_por_conjunto(datos):
    regla = consolidar(datos)["regla"]
    assert regla["por_conjunto"]["val"]["falsas_alarmas"] == 1
    assert regla["umbral_pwnt_pct"] == pytest.approx(19.291046)


def test_etapa2_con_su_cobertura(datos):
    etapa2 = consolidar(datos)["etapa2"]
    assert etapa2["cobertura"] == 0.0 and etapa2["abstenciones"] == 1299 and etapa2["muestras"] == 1299


def test_falsas_alarmas(datos):
    falsas = consolidar(datos)["falsas_alarmas"]
    assert falsas["etapa1_prueba"]["corridas"] == ["R33", "R36", "R40"]
    assert falsas["regla"] == [{"id": "R54", "conjunto": "val"}]


def test_aviso_y_limitaciones(datos):
    hito = consolidar(datos)
    assert "consultiv" in hito["aviso"].lower()
    assert any("máquina" in x for x in hito["limitaciones"])
