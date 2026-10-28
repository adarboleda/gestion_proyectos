"""Descubrimiento de las corridas PWR 3L: clase, id, archivo, área, gemela y errores."""
import json
import shutil

import pytest

from preparacion_pwr3l.config import CLASES, DESCARTADAS, GEMELAS
from preparacion_pwr3l.descubrimiento import ErrorDatos, clave_id, descubrir_corridas


@pytest.fixture(scope="module")
def corridas(arbol_pwr3l):
    return {c.id: c for c in descubrir_corridas(arbol_pwr3l)}


def test_encuentra_todas_las_carpetas_de_corrida(corridas, ayudantes):
    assert len(corridas) == ayudantes.NUMERO_CORRIDAS


def test_clase_por_carpeta_manual_y_por_sufijo_automatico(corridas):
    esperadas = {
        "R01": "NORM", "R02": "NORM", "R09": "LOCA", "R10": "LOCA", "R03": "LOCAC", "R07": "LOCAC",
        "R21": "ATWS", "R27": "ATWS", "R59": "TRIP_OK", "R20": "OOD",
        "R31": "NORM", "R41": "LOCA", "R07b": "LOCAC", "R47": "ATWS", "R54": "TRIP_OK", "R64": "OOD",
    }
    for rid, clase in esperadas.items():
        assert corridas[rid].clase == clase, rid
    assert corridas["R01"].origen == "manual"
    assert corridas["R31"].origen == "auto"


def test_etiquetas_de_las_cinco_clases():
    assert CLASES == {"NORM": 0, "LOCA": 1, "LOCAC": 2, "ATWS": 3, "TRIP_OK": 4}


def test_etiqueta_de_cada_corrida(corridas):
    assert corridas["R59"].etiqueta == 4
    assert corridas["R07b"].etiqueta == 2
    assert corridas["R20"].etiqueta is None


def test_archivo_de_datos_relativo_al_origen(corridas):
    assert corridas["R01"].archivo == "NORM/R01_NORM/R01_plotdata_NORM.xls"
    assert corridas["R02"].archivo == "NORM/R02_NORM PD 100-90%/R02_plotdata_NORM_t30.csv"
    assert corridas["R07b"].archivo == "auto/R07b_LOCAC/plotdata.csv"


def test_orden_por_etiqueta_y_numero(arbol_pwr3l):
    ids = [c.id for c in descubrir_corridas(arbol_pwr3l)]
    locac = [i for i in ids if i in {"R03", "R07", "R07b", "R46", "R88"}]
    assert locac == ["R03", "R07", "R07b", "R46", "R88"]
    assert ids.index("R01") < ids.index("R09") < ids.index("R03") < ids.index("R21") < ids.index("R59")
    assert ids[-2:] == ["R20", "R64"]  # OOD al final
    assert clave_id("R7") < clave_id("R07b") < clave_id("R10") < clave_id("R100")


def test_ignora_carpetas_con_guion_bajo_y_archivos_sueltos(corridas):
    assert "X01" not in corridas
    assert all(not c.archivo.startswith("auto/_") for c in corridas.values())


def test_descartadas_y_ood_se_marcan_sin_leerse(corridas):
    assert {rid for rid, c in corridas.items() if c.estado == "descartada"} == {"R07", "R27"}
    assert {rid for rid, c in corridas.items() if c.estado == "ood"} == {"R20", "R64"}
    # R27 tiene dos archivos de datos y no da error: se identifica por su carpeta
    assert corridas["R27"].archivo == "ATWS/R27_ATWS_LOFW_tripman_FAILED_t30_op90"
    assert all(corridas[r].serie is None and corridas[r].filas is None for r in ("R07", "R27", "R20", "R64"))
    assert set(DESCARTADAS) == {"R07", "R27", "R28"}


def test_corridas_de_las_cinco_clases_quedan_pendientes_de_leer(corridas):
    pendientes = [c for c in corridas.values() if c.estado == "pendiente"]
    assert len(pendientes) == len(corridas) - 4
    assert all(c.clase in CLASES for c in pendientes)


def test_area_de_rotura_desde_la_carpeta_y_desde_config(corridas):
    assert corridas["R10"].area == 50  # «50cm» en el nombre de la carpeta manual
    assert corridas["R09"].area == 2000
    assert corridas["R07b"].area == 2000  # descripción de config.json
    assert corridas["R86"].area == 1000  # «1000 cm2 + pérdida de energía AC»
    assert corridas["R01"].area is None and corridas["R21"].area is None


def test_gemela_segun_la_tabla(corridas):
    assert corridas["R21"].gemela == "R59" and corridas["R59"].gemela == "R21"
    assert corridas["R92"].gemela == "R100" and corridas["R100"].gemela == "R92"
    assert corridas["R52"].gemela is None
    assert len(GEMELAS) == 19
    assert len({rid for par in GEMELAS for rid in par}) == 38


def _error(origen):
    with pytest.raises(ErrorDatos) as info:
        descubrir_corridas(origen)
    return info.value


def test_origen_inexistente(tmp_path):
    error = _error(tmp_path / "no-existe")
    assert "no existe la carpeta de origen" in str(error)


def test_carpeta_no_reconocida(copia_pwr3l):
    (copia_pwr3l / "LOCA RARA").mkdir()
    error = _error(copia_pwr3l)
    assert error.archivo == "LOCA RARA" and error.causa == "carpeta no reconocida"


def test_clase_desconocida_en_auto(copia_pwr3l, ayudantes):
    ayudantes.escribir_corrida_auto(copia_pwr3l, "R200", "SGTR")
    error = _error(copia_pwr3l)
    assert error.archivo == "auto/R200_SGTR" and "clase desconocida" in error.causa


def test_nombre_sin_identificador(copia_pwr3l):
    shutil.copytree(copia_pwr3l / "NORM" / "R01_NORM", copia_pwr3l / "NORM" / "corrida_sin_id")
    error = _error(copia_pwr3l)
    assert error.archivo == "NORM/corrida_sin_id" and error.causa == "nombre de corrida no reconocido"


def test_identificador_repetido(copia_pwr3l, ayudantes):
    ayudantes.escribir_corrida_auto(copia_pwr3l, "R01", "NORM")
    error = _error(copia_pwr3l)
    assert "identificador de corrida repetido" in error.causa
    assert "R01" in str(error)


def test_carpeta_sin_archivo_de_datos(copia_pwr3l):
    (copia_pwr3l / "NORM" / "R02_NORM PD 100-90%" / "R02_plotdata_NORM_t30.csv").unlink()
    error = _error(copia_pwr3l)
    assert error.archivo == "NORM/R02_NORM PD 100-90%" and error.causa == "no hay archivo de datos"


def test_carpeta_automatica_sin_plotdata(copia_pwr3l):
    (copia_pwr3l / "auto" / "R31_NORM" / "plotdata.csv").unlink()
    error = _error(copia_pwr3l)
    assert error.archivo == "auto/R31_NORM" and error.causa == "no hay archivo de datos"


def test_carpeta_con_mas_de_un_archivo_de_datos(copia_pwr3l):
    carpeta = copia_pwr3l / "LOCA HOT" / "R10_LOCA_hot_50cm_t60"
    shutil.copy(carpeta / "R10_plotdata_LOCAH50_t60.csv", carpeta / "R10_plotdata_copia.csv")
    error = _error(copia_pwr3l)
    assert error.archivo == "LOCA HOT/R10_LOCA_hot_50cm_t60" and error.causa == "hay más de un archivo de datos"


def test_loca_sin_area_identificable(copia_pwr3l, ayudantes):
    ayudantes.escribir_corrida_auto(copia_pwr3l, "R201", "LOCA", descripcion="LOCA rama caliente")
    error = _error(copia_pwr3l)
    assert error.archivo == "auto/R201_LOCA" and error.causa == "no se pudo determinar el área de rotura"


def test_gemela_declarada_distinta_de_la_tabla(copia_pwr3l):
    ruta = copia_pwr3l / "auto" / "R54_TRIP_OK" / "config.json"
    configuracion = json.loads(ruta.read_text(encoding="utf-8"))
    configuracion["gemelo_de"] = "R49"
    ruta.write_text(json.dumps(configuracion), encoding="utf-8")
    error = _error(copia_pwr3l)
    assert error.archivo == "auto/R54_TRIP_OK/config.json"
    assert "no coincide con la tabla" in error.causa and "R49" in error.causa and "R47" in error.causa


def test_gemela_declarada_que_la_tabla_no_tiene(copia_pwr3l, ayudantes):
    ayudantes.escribir_corrida_auto(copia_pwr3l, "R300", "TRIP_OK", gemela="R31")
    error = _error(copia_pwr3l)
    assert error.archivo == "auto/R300_TRIP_OK/config.json" and "no coincide con la tabla" in error.causa


def test_clase_de_entrenamiento_sin_corridas(copia_pwr3l):
    shutil.rmtree(copia_pwr3l / "TRIP_OK")
    for carpeta in (copia_pwr3l / "auto").glob("R*_TRIP_OK"):
        shutil.rmtree(carpeta)
    error = _error(copia_pwr3l)
    assert error.causa == "no hay corridas de la clase TRIP_OK"


def test_mensaje_con_ruta_causa_y_variable():
    error = ErrorDatos("auto/R31_NORM/plotdata.csv", "falta la variable", "DNBR")
    assert str(error) == "ERROR: auto/R31_NORM/plotdata.csv: falta la variable [variable DNBR]"
