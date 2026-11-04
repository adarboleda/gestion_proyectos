"""Registro de eventos: lectura, tipo de señal, primera señal de disparo e instante del scram."""
import numpy as np
import pytest

from preparacion_pwr3l.descubrimiento import ErrorDatos, descubrir_corridas
from regla_atws.eventos import Senal, instante_scram, leer_eventos, primera_senal, tipo_senal


def _corrida(origen, rid):
    return next(c for c in descubrir_corridas(origen) if c.id == rid)


def test_lee_las_lineas_con_tiempo_y_texto(arbol_atws):
    eventos = leer_eventos(arbol_atws, _corrida(arbol_atws, "R54"))
    assert (0.0, "HPI Pump #3 Position Change: 100%") in eventos
    assert (45.5, "Turbine trip") in eventos and (50.5, "Reactor Scram") in eventos
    assert all(isinstance(t, float) for t, _ in eventos)


@pytest.mark.parametrize(
    "texto, tipo",
    [
        ("Low SG Level 17.0 %", "low sg level"),
        ("Turbine Trip Control Change: True", "turbine trip"),
        ("Turbine trip  ", "turbine trip"),
        ("Scram High Prz Level93.4 %", "scram high prz level"),
        ("Scram Lo RX Press  1890.0 psia", "scram lo rx press"),
        ("RCP-A trip", "rcp-a trip"),
    ],
)
def test_tipo_normalizado(texto, tipo):
    assert tipo_senal(texto) == tipo


def test_primera_senal_sin_contar_reactor_scram():
    eventos = [(0.0, "HPI Pump #3 Position Change: 100%"), (20.0, "Reactor Scram"), (31.5, "RCP-A trip")]
    senal = primera_senal(eventos, np.full(301, 100.0))
    assert senal == Senal(31.5, "rcp-a trip", "registro")


def test_alto_flujo_sin_senal_en_el_registro():
    pwnt = np.full(301, 100.0)
    pwnt[56:] = 118.5
    assert primera_senal([(0.0, "PZR Spray Valve #1 Position Change: 0%")], pwnt) == Senal(56.0, "scram high flux", "alto flujo")


def test_alto_flujo_antes_que_la_senal_del_registro():
    pwnt = np.full(301, 100.0)
    pwnt[40:] = 119.0
    assert primera_senal([(45.5, "Turbine trip")], pwnt).fuente == "alto flujo"
    assert primera_senal([(39.5, "Turbine trip")], pwnt).fuente == "registro"


def test_sin_demanda():
    assert primera_senal([(30.0, "TBV Valve #1 Position Change: 100%")], np.full(301, 100.0)) is None


def test_instante_del_scram():
    assert instante_scram([(45.5, "Turbine trip"), (50.5, "Reactor Scram")]) == 50.5
    assert instante_scram([(45.5, "Turbine trip")]) is None


def test_sin_registro_de_eventos(copia_atws):
    corrida = _corrida(copia_atws, "R54")
    (copia_atws / "auto" / "R54_TRIP_OK" / "transientlist.dat").unlink()
    with pytest.raises(ErrorDatos) as info:
        leer_eventos(copia_atws, corrida)
    assert info.value.archivo == "auto/R54_TRIP_OK" and "no hay registro de eventos" in info.value.causa


def test_dos_registros_de_eventos(copia_atws):
    corrida = _corrida(copia_atws, "R54")
    carpeta = copia_atws / "auto" / "R54_TRIP_OK"
    (carpeta / "otro.dat").write_text("x", encoding="latin-1")
    with pytest.raises(ErrorDatos, match="más de un registro de eventos"):
        leer_eventos(copia_atws, corrida)


def test_registro_ilegible(arbol_atws, monkeypatch):
    corrida = _corrida(arbol_atws, "R54")

    def falla(*args, **kwargs):
        raise PermissionError("sin permiso")

    monkeypatch.setattr("pathlib.Path.read_text", falla)
    with pytest.raises(ErrorDatos) as info:
        leer_eventos(arbol_atws, corrida)
    assert info.value.archivo == "auto/R54_TRIP_OK/transientlist.dat"
    assert info.value.causa == "registro ilegible (PermissionError)"
