"""Pruebas del instante de inicio del evento de cada corrida (005)."""
import pytest

from clasificador_etapa1.eventos import inicio_evento, inicios_evento
from preparacion_pwr3l.descubrimiento import Corrida, ErrorDatos


def corrida(rid, clase, archivo):
    return Corrida(rid, clase, "manual", archivo, estado="usable")


def test_inicio_desde_validacion_json(arbol_eventos):
    assert inicio_evento(arbol_eventos, corrida("R41", "LOCA", "auto/R41_LOCA/plotdata.csv")) == 25.0


def test_inicio_desde_validacion_corridas_csv(arbol_eventos):
    c = corrida("R10", "LOCA", "LOCA HOT/R10_LOCA_hot_50cm_t60/R10_plotdata.csv")
    assert inicio_evento(arbol_eventos, c) == 61.0


def test_se_ignora_la_fila_mitigation(arbol_eventos):
    c = corrida("R27", "ATWS", "ATWS/R27_ATWS_LOFW_tripman_FAILED_t30_op90/R27_plotdata.csv")
    assert inicio_evento(arbol_eventos, c) == 32.0


def test_inicio_desde_el_nombre_de_la_carpeta(arbol_eventos):
    c = corrida("R60", "TRIP_OK", "TRIP_OK/R60_TRIP_OK_LOFW_t48/R60_plotdata.csv")
    assert inicio_evento(arbol_eventos, c) == 48.0


def test_identificador_que_es_prefijo_de_otro_no_confunde(arbol_eventos):
    # R1 no debe tomar la fila de R10
    c = corrida("R1", "LOCA", "auto/R1_LOCA/plotdata.csv")
    with pytest.raises(ErrorDatos):
        inicio_evento(arbol_eventos, c)


def test_norm_no_tiene_inicio(arbol_eventos):
    assert inicio_evento(arbol_eventos, corrida("R31", "NORM", "auto/R31_NORM/plotdata.csv")) is None


def test_evento_sin_inicio_detiene_con_error(arbol_eventos):
    c = corrida("R42", "LOCA", "auto/R42_LOCA/plotdata.csv")
    with pytest.raises(ErrorDatos) as error:
        inicio_evento(arbol_eventos, c)
    assert "auto/R42_LOCA/plotdata.csv" in str(error.value)
    assert "inicio del evento" in str(error.value)


def test_inicios_evento_cubre_todas_las_usables(arbol_eventos):
    corridas = [
        corrida("R41", "LOCA", "auto/R41_LOCA/plotdata.csv"),
        corrida("R09", "LOCA", "LOCA HOT/R09_LOCA_hot_2000cm2_t0/R09_plotdata.csv"),
        corrida("R31", "NORM", "auto/R31_NORM/plotdata.csv"),
        Corrida("R20", "OOD", "manual", "LOCA PORV/R20", estado="ood"),
    ]
    assert inicios_evento(arbol_eventos, corridas) == {"R41": 25.0, "R09": 1.0, "R31": None}
