"""Pruebas del reporte, la comparación con la referencia y metadata.json (FR-007)."""
import json
import re
from types import SimpleNamespace

import pytest

from preparacion_datos.lectura import Simulacion
from preparacion_datos.particion import repartir
from preparacion_datos.reporte import (
    LIMITACIONES,
    comparar_referencia,
    construir_resumen,
    contar_muestras,
    formatear_reporte,
)
from preparacion_datos.salida import construir_metadata

CONJUNTOS = ("train", "val", "test")
CLASES = ("NORM", "LOCA", "LOCAC", "ATWS")


def construir(n_loca=100, n_locac=100, paso_segundos=10):
    simulaciones = [Simulacion("NORM", 0, None, "Normal/1.csv", paso_segundos=paso_segundos)]
    simulaciones += [
        Simulacion("LOCA", 1, n, f"LOCA/{n}.csv", paso_segundos=paso_segundos)
        for n in range(1, n_loca + 1)
    ]
    simulaciones += [
        Simulacion("LOCAC", 2, n, f"LOCAC/{n}.csv", paso_segundos=paso_segundos)
        for n in range(1, n_locac + 1)
    ]
    simulaciones.append(Simulacion("ATWS", 3, None, "ATWS/1.csv", paso_segundos=paso_segundos))
    return simulaciones


@pytest.fixture
def resumen():
    particion = repartir(construir(), 42)
    escalador = SimpleNamespace(filas_ajuste=142 * 150, variables_sin_varianza=[])
    return construir_resumen("origen/Operation_csv_data", 42, particion, escalador, referencia=None)


def test_paso_medido_y_duracion_en_resumen_metadata_y_reporte(resumen):
    assert resumen.paso_segundos == 10
    assert resumen.duracion_muestra_segundos == 1500
    metadata = construir_metadata(resumen)
    assert metadata["paso_segundos"] == 10
    assert metadata["duracion_muestra_segundos"] == 1500
    texto = formatear_reporte(resumen, artefactos=[])
    seccion = texto.split("1. Origen y configuración")[1].split("2. Muestras por clase y conjunto")[0]
    assert "paso medido de TIME: 10 s" in seccion
    assert "duración: 1500 s" in seccion


def test_paso_medido_distinto_de_10_calcula_duracion_real():
    particion = repartir(construir(paso_segundos=5), 42)
    escalador = SimpleNamespace(filas_ajuste=142 * 150, variables_sin_varianza=[])
    resumen = construir_resumen("o", 42, particion, escalador, referencia=None)
    assert resumen.paso_segundos == 5
    assert resumen.duracion_muestra_segundos == 750
    metadata = construir_metadata(resumen)
    assert metadata["paso_segundos"] == 5 and metadata["duracion_muestra_segundos"] == 750


def test_conteos_suman_los_totales_de_cada_conjunto(resumen):
    conteos = resumen.conteos_muestras
    assert list(conteos) == list(CLASES)
    for conjunto, total in zip(CONJUNTOS, (142, 30, 30)):
        assert sum(conteos[c][conjunto] for c in CLASES) == total == resumen.totales[conjunto]
    assert sum(resumen.totales.values()) == 202
    assert contar_muestras(repartir(construir(), 42)) == conteos


def test_las_cuatro_clases_aparecen_en_los_tres_conjuntos_con_ceros_marcados(resumen):
    texto = formatear_reporte(resumen, artefactos=[])
    tabla = texto.split("2. Muestras por clase y conjunto")[1].split("3. Simulaciones por conjunto")[0]
    for clase in CLASES:
        assert re.search(rf"^\s*{clase}\s", tabla, re.MULTILINE), clase
    assert "Total" in tabla
    # NORM y ATWS no tienen muestras de validación ni de prueba: 4 celdas en cero marcadas.
    assert tabla.count("0*") == 4
    assert "* sin muestras" in tabla


def test_normal_y_atws_llevan_la_advertencia_de_una_sola_simulacion(resumen):
    for clase in ("NORM", "ATWS"):
        coincidencias = [a for a in resumen.advertencias if a.startswith(f"{clase} tiene una sola simulación")]
        assert len(coincidencias) == 1
        assert "asignada completa a entrenamiento" in coincidencias[0]
        assert "no tiene muestras de validación ni de prueba" in coincidencias[0]
    texto = formatear_reporte(resumen, artefactos=[])
    assert "5. Advertencias" in texto
    for advertencia in resumen.advertencias:
        assert advertencia in texto


def test_una_celda_en_cero_de_una_clase_con_varias_simulaciones_se_advierte():
    particion = repartir(construir(n_loca=2, n_locac=2), 42)  # 2 severidades: validación vacía
    escalador = SimpleNamespace(filas_ajuste=4 * 150, variables_sin_varianza=[])
    resumen = construir_resumen("o", 42, particion, escalador, referencia=None)
    assert any(a.startswith("LOCA") and "sin muestras" in a for a in resumen.advertencias)


def test_limitaciones_conocidas_presentes(resumen):
    texto = formatear_reporte(resumen, artefactos=[])
    for limitacion in LIMITACIONES:
        assert limitacion in texto
    unidas = " ".join(LIMITACIONES).lower()
    assert "una sola simulación" in unidas
    assert "desbalance" in unidas
    assert "simulador" in unidas
    assert "datos no vistos" in unidas


def test_el_reporte_lista_las_simulaciones_de_cada_conjunto(resumen):
    particion = repartir(construir(), 42)
    seccion = formatear_reporte(resumen, artefactos=[]).split("3. Simulaciones por conjunto")[1]
    seccion = seccion.split("4. Escalador")[0]
    bloques = re.split(r"^(train|val|test) \(\d+\)", seccion, flags=re.MULTILINE)
    por_conjunto = dict(zip(bloques[1::2], bloques[2::2]))
    for conjunto in CONJUNTOS:
        listado = {}
        for clase, numeros in re.findall(r"^\s*(NORM|LOCAC|LOCA|ATWS): ([\d ]+)$", por_conjunto[conjunto], re.MULTILINE):
            listado[clase] = {int(n) for n in numeros.split()}
        esperado = {}
        for s in particion[conjunto]:
            esperado.setdefault(s.clase, set()).add(s.severidad or 1)
        assert listado == esperado


def escribir_referencia(ruta, loca, locac):
    ruta.write_text(
        json.dumps({"sample_counts": {"NORM": {"train": 1, "val": 1, "test": 0}, "LOCA": loca, "LOCAC": locac,
                                      "ATWS": {"train": 10, "val": 3, "test": 3}}})
    )
    return ruta


def test_referencia_coincide_aunque_normal_y_atws_difieran(resumen, tmp_path):
    ruta = escribir_referencia(
        tmp_path / "ref.json",
        {"train": 70, "val": 15, "test": 15},
        {"train": 70, "val": 15, "test": 15},
    )
    resultado = comparar_referencia(ruta, resumen.conteos_muestras)
    assert resultado["estado"] == "COINCIDE"
    assert resultado["diferencias"] == []


def test_referencia_difiere_indica_las_celdas(resumen, tmp_path):
    ruta = escribir_referencia(
        tmp_path / "ref.json",
        {"train": 69, "val": 16, "test": 15},
        {"train": 70, "val": 15, "test": 15},
    )
    resultado = comparar_referencia(ruta, resumen.conteos_muestras)
    assert resultado["estado"] == "DIFIERE"
    assert {(d["clase"], d["conjunto"]) for d in resultado["diferencias"]} == {("LOCA", "train"), ("LOCA", "val")}
    assert {"obtenido": 70, "referencia": 69}.items() <= next(
        d for d in resultado["diferencias"] if d["conjunto"] == "train"
    ).items()


def test_referencia_no_disponible_u_omitida(resumen, tmp_path):
    assert comparar_referencia(tmp_path / "no_existe.json", resumen.conteos_muestras)["estado"] == "NO DISPONIBLE"
    (tmp_path / "roto.json").write_text("{no es json")
    assert comparar_referencia(tmp_path / "roto.json", resumen.conteos_muestras)["estado"] == "NO DISPONIBLE"
    assert comparar_referencia(None, resumen.conteos_muestras)["estado"] == "OMITIDA"


def test_metadata_cumple_los_invariantes(resumen):
    metadata = construir_metadata(resumen)
    listas = [set(metadata["simulaciones"][c]) for c in CONJUNTOS]
    assert listas[0].isdisjoint(listas[1]) and listas[0].isdisjoint(listas[2]) and listas[1].isdisjoint(listas[2])
    for conjunto in CONJUNTOS:
        assert metadata["totales"][conjunto] == sum(metadata["conteos_muestras"][c][conjunto] for c in CLASES)
        assert metadata["totales"][conjunto] == len(metadata["simulaciones"][conjunto])
    assert metadata["escalador"]["ajustado_con"] == "train"
    assert metadata["escalador"]["filas_ajuste"] == 142 * 150
    assert metadata["conteos_archivos"] == {"NORM": 1, "LOCA": 100, "LOCAC": 100, "ATWS": 1}
    assert metadata["advertencias"] == resumen.advertencias
    assert metadata["limitaciones"] == LIMITACIONES
    json.dumps(metadata)  # serializable


def test_variables_sin_varianza_se_informan_en_reporte_y_metadata():
    particion = repartir(construir(), 42)
    escalador = SimpleNamespace(filas_ajuste=142 * 150, variables_sin_varianza=["WLR"])
    resumen = construir_resumen("o", 42, particion, escalador, referencia=None)
    assert "WLR" in formatear_reporte(resumen, artefactos=[]).split("4. Escalador")[1].split("5. Advertencias")[0]
    assert construir_metadata(resumen)["escalador"]["variables_sin_varianza"] == ["WLR"]
