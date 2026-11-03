"""Reparto de grupos completos en entrenamiento, validación y prueba."""
import pytest

from preparacion_pwr3l.config import CONJUNTOS, PROPORCIONES
from preparacion_pwr3l.descubrimiento import Corrida
from preparacion_pwr3l.grupos import formar_grupos
from preparacion_pwr3l.particion import repartir


def _usable(rid, clase, area=None):
    return Corrida(rid, clase, "auto", f"auto/{rid}_{clase}/plotdata.csv", area=area, estado="usable")


def _sueltas(n, clase="NORM", inicio=1):
    return [_usable(f"R{inicio + i}", clase) for i in range(n)]


def test_cada_grupo_y_cada_corrida_en_un_solo_conjunto():
    corridas = _sueltas(10) + [_usable(f"R{100 + i}", "LOCA", area=a) for i, a in enumerate([2, 2, 5, 10, 10, 10, 50])]
    grupos = formar_grupos(corridas)
    conjunto_de, particion = repartir(grupos, 42)
    assert set(conjunto_de) == {g.clave for g in grupos}
    ids = [c.id for conjunto in CONJUNTOS for c in particion[conjunto]]
    assert sorted(ids) == sorted(c.id for c in corridas) and len(ids) == len(set(ids))
    for grupo in grupos:  # ningún grupo partido
        assert all(c in particion[conjunto_de[grupo.clave]] for c in grupo.corridas)


@pytest.mark.parametrize("n", [1, 7, 10, 20, 33])
def test_grupos_de_tamano_uno_a_menos_de_una_corrida_de_la_meta(n):
    _, particion = repartir(formar_grupos(_sueltas(n)), 42)
    for conjunto in CONJUNTOS:
        assert abs(len(particion[conjunto]) - PROPORCIONES[conjunto] * n) < 1


@pytest.mark.parametrize("semilla", [0, 1, 42, 123])
def test_ningun_conjunto_supera_su_meta_en_un_grupo_completo(semilla):
    areas = [2000] * 8 + [2] * 3 + [10] * 4 + [50] * 4 + [500] * 4 + [5, 5, 20, 20, 100, 100, 1000, 1000, 3000, 7700]
    corridas = [_usable(f"R{200 + i}", "LOCA" if i % 2 else "LOCAC", area=a) for i, a in enumerate(areas)]
    grupos = formar_grupos(corridas)
    _, particion = repartir(grupos, semilla)
    maximo = max(len(g.corridas) for g in grupos)
    for conjunto in CONJUNTOS:
        assert len(particion[conjunto]) - PROPORCIONES[conjunto] * len(corridas) < maximo


def test_reparto_por_familia():
    corridas = _sueltas(10) + _sueltas(10, "ATWS", inicio=50)
    _, particion = repartir(formar_grupos(corridas), 42)
    for clase in ("NORM", "ATWS"):
        conteos = [sum(c.clase == clase for c in particion[conjunto]) for conjunto in CONJUNTOS]
        assert conteos[0] == 7 and sum(conteos) == 10


def test_misma_semilla_mismo_resultado_e_independiente_del_orden():
    corridas = _sueltas(20)
    a = repartir(formar_grupos(corridas), 42)[0]
    b = repartir(formar_grupos(corridas[::-1]), 42)[0]
    assert a == b


def test_semilla_distinta_puede_cambiar_el_reparto():
    corridas = _sueltas(20)
    repartos = {tuple(sorted(repartir(formar_grupos(corridas), s)[0].items())) for s in range(5)}
    assert len(repartos) > 1


def test_orden_de_filas_por_etiqueta_y_numero():
    corridas = [_usable("R100", "NORM"), _usable("R9", "NORM"), _usable("R07b", "LOCAC", area=2), _usable("R30", "LOCA", area=2)]
    _, particion = repartir(formar_grupos(corridas), 42)
    for conjunto in CONJUNTOS:
        claves = [(c.etiqueta, c.id) for c in particion[conjunto]]
        assert claves == sorted(claves, key=lambda x: (x[0], int(x[1][1:].rstrip("b")), x[1]))
