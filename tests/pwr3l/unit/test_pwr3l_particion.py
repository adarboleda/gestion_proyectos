"""Pruebas del reparto de grupos en entrenamiento, validación y prueba (004, historia 2)."""
import random

import pytest

from preparacion_pwr3l.config import CLASES, CONJUNTOS
from preparacion_pwr3l.descubrimiento import clave_orden
from preparacion_pwr3l.grupos import Grupo, formar_grupos
from preparacion_pwr3l.particion import metas, repartir


def grupos_sinteticos(fabricar, tamanos_loca, tamanos_atws=(), n_norm=0):
    """Grupos construidos a mano: LOCA de tamaños dados (una área por grupo), ATWS de 1 o 2 corridas
    (2 = gemelas) y NORM individuales. Los identificadores no chocan con la tabla de gemelas."""
    grupos, numero = [], 1000
    for i, tamano in enumerate(tamanos_loca):
        corridas = []
        for j in range(tamano):
            clase = "LOCA" if j % 2 == 0 else "LOCAC"
            corridas.append(fabricar.corrida(f"R{numero}", clase, area=10_000 + i, gemela=None))
            numero += 1
        grupos.append(Grupo(f"AREA-{10_000 + i}", "LOCA", corridas))
    for tamano in tamanos_atws:
        if tamano == 2:
            a = fabricar.corrida(f"R{numero}", "ATWS", gemela=f"R{numero + 1}")
            b = fabricar.corrida(f"R{numero + 1}", "TRIP_OK", gemela=f"R{numero}")
            grupos.append(Grupo(f"GEMELAS-R{numero}-R{numero + 1}", "ATWS", [a, b]))
            numero += 2
        else:
            grupos.append(Grupo(f"R{numero}", "ATWS", [fabricar.corrida(f"R{numero}", "ATWS", gemela=None)]))
            numero += 1
    for _ in range(n_norm):
        grupos.append(Grupo(f"R{numero}", "NORM", [fabricar.corrida(f"R{numero}", "NORM", gemela=None)]))
        numero += 1
    return grupos


def test_metas_son_70_15_15():
    assert metas(20) == pytest.approx({"train": 14.0, "val": 3.0, "test": 3.0})
    assert metas(36) == pytest.approx({"train": 25.2, "val": 5.4, "test": 5.4})


def test_cada_grupo_en_un_conjunto_y_cada_usable_asignada(fabricar):
    corridas = fabricar.variadas()
    grupos = formar_grupos(corridas)
    reparto = repartir(grupos)
    assert set(reparto.conjunto_de_grupo) == {g.clave for g in grupos}
    assert set(reparto.conjunto_de_grupo.values()) <= set(CONJUNTOS)
    assert sorted(reparto.conjunto_de_corrida) == sorted(c.id for c in corridas if c.estado == "usable")
    for grupo in grupos:
        assert {reparto.conjunto_de_corrida[c.id] for c in grupo.corridas} == {reparto.conjunto_de_grupo[grupo.clave]}


def test_desvio_por_familia_menor_que_el_grupo_mas_grande(fabricar):
    generador = random.Random(2026)
    for _ in range(200):
        tamanos_loca = [generador.randint(1, 8) for _ in range(generador.randint(1, 14))]
        tamanos_atws = [generador.choice((1, 2)) for _ in range(generador.randint(1, 20))]
        grupos = grupos_sinteticos(fabricar, tamanos_loca, tamanos_atws, n_norm=generador.randint(1, 20))
        reparto = repartir(grupos, semilla=generador.randint(0, 10_000))
        for familia in ("NORM", "LOCA", "ATWS"):
            mayor = max(g.tamano for g in grupos if g.familia == familia)
            for conjunto in CONJUNTOS:
                desvio = abs(reparto.asignadas[familia][conjunto] - reparto.metas[familia][conjunto])
                assert desvio < mayor, (familia, conjunto, tamanos_loca, tamanos_atws)


def test_el_grupo_mas_grande_va_a_entrenamiento(fabricar):
    # 8 corridas frente a una meta de validación de 0.15 · 20 = 3
    grupos = grupos_sinteticos(fabricar, [8, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1])
    reparto = repartir(grupos)
    assert reparto.conjunto_de_grupo["AREA-10000"] == "train"


def test_misma_semilla_mismo_reparto_aunque_cambie_el_orden(fabricar):
    grupos = grupos_sinteticos(fabricar, [3, 1, 2, 1, 4, 1], [2, 2, 1, 2, 1], n_norm=7)
    base = repartir(grupos, semilla=7).conjunto_de_corrida
    assert repartir(list(reversed(grupos)), semilla=7).conjunto_de_corrida == base
    barajados = list(grupos)
    random.Random(1).shuffle(barajados)
    assert repartir(barajados, semilla=7).conjunto_de_corrida == base


def test_otra_semilla_puede_cambiar_el_reparto(fabricar):
    grupos = grupos_sinteticos(fabricar, [1] * 10, [2] * 6, n_norm=10)
    base = repartir(grupos, semilla=42).conjunto_de_corrida
    assert any(repartir(grupos, semilla=s).conjunto_de_corrida != base for s in range(1, 30))


def test_conteos_con_cinco_clases_y_tres_conjuntos(fabricar):
    corridas = fabricar.variadas()
    reparto = repartir(formar_grupos(corridas))
    assert set(reparto.conteos) == set(CLASES)
    for clase in CLASES:
        assert set(reparto.conteos[clase]) == set(CONJUNTOS)
    total = sum(n for por_conjunto in reparto.conteos.values() for n in por_conjunto.values())
    assert total == sum(1 for c in corridas if c.estado == "usable")


def test_corridas_de_cada_conjunto_ordenadas(fabricar):
    reparto = repartir(formar_grupos(fabricar.variadas()))
    for conjunto in CONJUNTOS:
        lista = reparto.corridas[conjunto]
        assert lista == sorted(lista, key=clave_orden)
        assert all(reparto.conjunto_de_corrida[c.id] == conjunto for c in lista)


def test_semilla_por_defecto_42(fabricar):
    grupos = formar_grupos(fabricar.variadas())
    reparto = repartir(grupos)
    assert reparto.semilla == 42
    assert repartir(grupos, semilla=42).conjunto_de_corrida == reparto.conjunto_de_corrida


def test_familias_con_uno_y_dos_grupos(fabricar):
    for n_norm in (1, 2):
        grupos = grupos_sinteticos(fabricar, [1, 1, 1, 1], [1], n_norm=n_norm)
        reparto = repartir(grupos)
        asignadas = reparto.asignadas["NORM"]
        assert sum(asignadas.values()) == n_norm
        assert set(asignadas) == set(CONJUNTOS)
        assert asignadas["test"] == 0
        assert reparto.asignadas["ATWS"] == {"train": 1, "val": 0, "test": 0}


def test_clase_sin_corridas_usables_aparece_con_ceros(fabricar):
    grupos = grupos_sinteticos(fabricar, [1, 1, 1], [1, 1], n_norm=3)  # sin TRIP_OK
    reparto = repartir(grupos)
    assert reparto.conteos["TRIP_OK"] == {"train": 0, "val": 0, "test": 0}


def test_repartir_no_modifica_las_corridas(fabricar):
    corridas = fabricar.variadas()
    antes = [(c.estado, c.area, c.gemela, id(c.serie)) for c in corridas]
    repartir(formar_grupos(corridas))
    assert [(c.estado, c.area, c.gemela, id(c.serie)) for c in corridas] == antes
