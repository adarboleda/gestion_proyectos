"""División sin fuga con las corridas reales de PWR 3L (se omite si el dataset no está disponible)."""
import time
from collections import Counter

import pytest

from datos_reales import ruta_pwr3l
from preparacion_pwr3l.config import CONJUNTOS
from preparacion_pwr3l.grupos import formar_grupos
from preparacion_pwr3l.lectura import cargar_corridas
from preparacion_pwr3l.particion import repartir
from preparacion_pwr3l.verificacion import verificar_reparto

ORIGEN = ruta_pwr3l()

pytestmark = pytest.mark.skipif(not ORIGEN.is_dir(), reason="dataset PWR 3L no disponible")


@pytest.fixture(scope="module")
def corridas():
    return cargar_corridas(ORIGEN)


def test_division_sin_fuga_con_las_corridas_reales(corridas):
    estados = Counter(c.estado for c in corridas)
    assert estados == {"usable": 91, "corta": 9, "descartada": 3, "ood": 6}

    inicio = time.perf_counter()
    grupos = formar_grupos(corridas)
    reparto = repartir(grupos)
    verificar_reparto(corridas, reparto)  # con TODAS las corridas, incluidas las 18 excluidas
    duracion = time.perf_counter() - inicio
    assert duracion < 1.0

    tipos = Counter(g.clave.split("-")[0] if "-" in g.clave else "individual" for g in grupos)
    assert tipos == {"AREA": 14, "GEMELAS": 15, "individual": 25}
    assert next(g for g in grupos if g.clave == "AREA-2000").tamano == 8

    excluidas = {c.id for c in corridas if c.estado != "usable"}
    assert not excluidas & set(reparto.conjunto_de_corrida)
    assert len(reparto.conjunto_de_corrida) == 91

    for familia in ("NORM", "LOCA", "ATWS"):
        mayor = max(g.tamano for g in grupos if g.familia == familia)
        for conjunto in CONJUNTOS:
            asignadas = reparto.asignadas[familia][conjunto]
            assert abs(asignadas - reparto.metas[familia][conjunto]) < mayor
            assert asignadas >= 1, (familia, conjunto)


def test_reparto_real_reproducible_e_independiente_del_orden(corridas):
    base = repartir(formar_grupos(corridas)).conjunto_de_corrida
    assert repartir(formar_grupos(corridas)).conjunto_de_corrida == base
    assert repartir(formar_grupos(list(reversed(corridas)))).conjunto_de_corrida == base
