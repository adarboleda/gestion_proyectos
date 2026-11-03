"""Resumen y reporte: conteos, grupos, corridas excluidas, advertencias y limitaciones (US3)."""
from types import SimpleNamespace

import pytest

from preparacion_pwr3l.config import CLASES, CONJUNTOS
from preparacion_pwr3l.descubrimiento import Corrida
from preparacion_pwr3l.grupos import formar_grupos
from preparacion_pwr3l.particion import repartir
from preparacion_pwr3l.reporte import SECCIONES, construir_resumen, formatear_reporte


def _c(rid, clase, estado="usable", area=None, gemela=None, filas=301):
    archivo = f"auto/{rid}_{clase}" if estado in ("descartada", "ood") else f"auto/{rid}_{clase}/plotdata.csv"
    return Corrida(rid, clase, "auto", archivo, area=area, gemela=gemela, estado=estado,
                   filas=None if estado in ("descartada", "ood") else filas)


@pytest.fixture
def corridas():
    return (
        [_c(f"R{n}", "NORM") for n in range(31, 41)]
        + [_c("R41", "LOCA", area=5), _c("R46", "LOCAC", area=5), _c("R42", "LOCA", area=10)]
        + [_c("R47", "ATWS", gemela="R54"), _c("R54", "TRIP_OK", gemela="R47")]
        + [_c("R55", "TRIP_OK", estado="corta", gemela="R48", filas=295)]
        + [_c("R07", "LOCAC", estado="descartada"), _c("R64", "OOD", estado="ood")]
    )


def _resumen(corridas, sin_varianza=()):
    usables = [c for c in corridas if c.estado == "usable"]
    grupos = formar_grupos(usables)
    conjunto_de, particion = repartir(grupos, 42)
    escalador = SimpleNamespace(filas_ajuste=300 * len(particion["train"]), variables_sin_varianza=list(sin_varianza))
    return construir_resumen("PWR 3L", 42, corridas, grupos, conjunto_de, particion, escalador)


def test_cinco_clases_en_los_tres_conjuntos_y_totales(corridas):
    resumen = _resumen(corridas)
    assert list(resumen.conteos_muestras) == list(CLASES)
    for clase in CLASES:
        assert list(resumen.conteos_muestras[clase]) == list(CONJUNTOS)
    total = sum(sum(v.values()) for v in resumen.conteos_muestras.values())
    assert total == sum(resumen.totales.values()) == 15
    assert sum(len(ids) for ids in resumen.corridas.values()) == 15


def test_corridas_encontradas_suman_todas_las_descubiertas(corridas):
    resumen = _resumen(corridas)
    encontradas = resumen.corridas_encontradas
    assert set(encontradas) == set(CLASES) | {"OOD"}
    assert sum(sum(v.values()) for v in encontradas.values()) == len(corridas)
    assert encontradas["TRIP_OK"] == {"usable": 1, "corta": 1, "descartada": 0, "ood": 0}
    assert encontradas["OOD"]["ood"] == 1 and encontradas["LOCAC"]["descartada"] == 1


def test_cada_exclusion_con_motivo_y_detalle(corridas):
    excluidas = {e["id"]: e for e in _resumen(corridas).excluidas}
    assert set(excluidas) == {"R55", "R07", "R64"}
    assert excluidas["R55"]["motivo"] == "corta" and "295 filas" in excluidas["R55"]["detalle"]
    assert excluidas["R07"]["motivo"] == "descartada" and "R07b" in excluidas["R07"]["detalle"]
    assert excluidas["R64"]["motivo"] == "ood" and excluidas["R64"]["clase"] == "OOD"
    assert all({"id", "clase", "archivo", "motivo", "detalle"} <= set(e) for e in excluidas.values())


def test_advertencias_por_corrida_corta_y_celdas_en_cero(corridas):
    resumen = _resumen(corridas)
    texto = "\n".join(resumen.advertencias)
    assert "R55" in texto and "auto/R55_TRIP_OK/plotdata.csv" in texto and "295" in texto
    nombres = {"train": "entrenamiento", "val": "validación", "test": "prueba"}
    ceros = 0
    for clase, por_conjunto in resumen.conteos_muestras.items():
        if sum(por_conjunto.values()) == 0:
            continue
        for conjunto, n in por_conjunto.items():
            if n == 0:
                ceros += 1
                assert f"{clase}: sin muestras de {nombres[conjunto]}." in resumen.advertencias
    assert ceros > 0  # el ejemplo tiene clases con una o dos corridas


def test_clase_con_todas_sus_corridas_cortas(corridas):
    corridas = [c for c in corridas if c.clase != "TRIP_OK"] + [_c("R54", "TRIP_OK", estado="corta", filas=290)]
    corridas = [c for c in corridas if c.id != "R47"] + [_c("R47", "ATWS")]
    resumen = _resumen(corridas)
    assert sum(resumen.conteos_muestras["TRIP_OK"].values()) == 0
    assert any(a.startswith("TRIP_OK:") and "ninguna corrida usable" in a for a in resumen.advertencias)


def test_grupos_por_conjunto(corridas):
    resumen = _resumen(corridas)
    grupos = {clave: (conjunto, ids) for conjunto in CONJUNTOS for clave, ids in resumen.grupos[conjunto].items()}
    assert grupos["AREA-5"][1] == ["R41", "R46"]
    assert grupos["GEMELAS-R47-R54"][1] == ["R47", "R54"]


def test_limitaciones_declaradas(corridas):
    texto = " ".join(_resumen(corridas).limitaciones)
    for palabra in ("pocas corridas", "etiqueta", "2000 cm²", "NORM", "ruido", "OOD"):
        assert palabra.lower() in texto.lower(), palabra


def test_reporte_con_las_nueve_secciones_en_orden(corridas):
    texto = formatear_reporte(_resumen(corridas, sin_varianza=["RM1"]), ["X_train.npy", "metadata.json"])
    posiciones = [texto.index(f"== {seccion} ==") for seccion in SECCIONES]
    assert posiciones == sorted(posiciones) and len(SECCIONES) == 9
    assert texto.startswith("REPORTE DE PREPARACIÓN DE DATOS PWR 3L")
    assert "R55" in texto and "R07" in texto and "R64" in texto
    assert "RM1" in texto and "metadata.json" in texto
    assert "*" in texto  # celdas en cero marcadas
