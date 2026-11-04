"""Datos y ayudas sintéticos para las pruebas del tiempo de detección (008)."""
import csv
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

from preparacion_pwr3l.descubrimiento import Corrida

RAIZ_PRUEBAS = Path(__file__).resolve().parents[1]

# id, clase, carpeta relativa, `fallas` de config.json (None = sin config), líneas del registro
# (None = sin .dat), inicio del validador (None = sin dato; «csv» va a validacion_corridas.csv)
CORRIDAS_FALLA = [
    ("R50", "ATWS", "auto/R50_ATWS", "9:0:30;8:0:0",
     [(0.0, "FWIV #4 Position Change: 0%"), (30.0, "FWIV #1 Position Change: 0%"), (30.0, "FWIV #2 Position Change: 0%"),
      (33.5, "Low SG Level 17.0 %")], 31.0),
    ("R51", "TRIP_OK", "auto/R51_TRIP_OK", "4:0:20",
     [(20.5, "RCP-A trip"), (23.0, "Reactor Scram")], 21.0),
    ("R52", "ATWS", "auto/R52_ATWS", "5:0:45;8:0:0",
     [(45.0, "Turbine Trip Control Change: True"), (45.5, "Turbine trip")], 46.0),
    ("R53", "TRIP_OK", "auto/R53_TRIP_OK", "3:0:10",
     [(10.0, "AFW Turbine Valve #1 Position Change: 100%"), (12.0, "Reactor Scram")], 11.0),
    ("R41", "LOCA", "auto/R41_LOCA", "1:100:50", [(0.0, "Malfunction # 1")], 51.0),
    ("R42", "LOCAC", "auto/R42_LOCAC", "1:500:30;6:0:30", [(0.0, "Malfunction # 1"), (0.0, "Malfunction # 2")], 30.5),
    ("R43", "LOCA", "auto/R43_LOCA", "7:0:50;8:0:0",
     [(0.0, "Malfunction # 1"), (60.0, "Turbine Trip Control Change: True")], 50.0),
    ("R10", "LOCA", "LOCA HOT/R10_LOCA_hot_50cm_t60", None, None, "csv:61.0"),
    ("R96", "ATWS", "auto/R96_ATWS", "12:0:40;8:0:0", [(52.0, "Scram High Flux 118.0 %")], 41.0),
    ("R47", "ATWS", "auto/R47_ATWS", "9:0:45;8:0:0", [(0.0, "Malfunction # 1")], 1.0),
    ("R22", "ATWS", "ATWS/R22_ATWS_LOFW_t45", None, [(47.5, "FWIV #1 Position Change: 0%")], "csv:13.0"),
    ("R60", "TRIP_OK", "TRIP_OK/R60_TRIP_OK_sin_fuente", None, [(5.0, "Low SG Level 17.0 %")], None),
    ("R31", "NORM", "auto/R31_NORM", None, None, None),
]

# Resultado esperado: id -> (t, fuente, incierta)
ESPERADO = {
    "R50": (30.0, "registro", False), "R51": (20.5, "registro", False), "R52": (45.0, "registro", False),
    "R53": (10.0, "registro", False), "R41": (50.0, "programado", False), "R42": (30.0, "programado", False),
    "R43": (50.0, "programado", False), "R10": (60.0, "programado", False), "R96": (40.0, "programado", False),
    "R47": (45.0, "programado", True), "R22": (47.5, "registro", True), "R60": (None, "ninguna", True),
}


def _dat(lineas) -> str:
    cuerpo = "".join(f"{t:08.1f} sec, {texto}\n" for t, texto in lineas)
    return "Basic Data Set #1 W 3-Loop TPC #3\nReset to IC #1 100% POWER EOC\n" + cuerpo


def escribir_arbol_fallas(raiz: Path) -> SimpleNamespace:
    raiz = Path(raiz)
    corridas, filas_csv = [], []
    for rid, clase, carpeta, fallas, lineas, inicio in CORRIDAS_FALLA:
        ruta = raiz / carpeta
        ruta.mkdir(parents=True)
        if fallas is not None:
            (ruta / "config.json").write_text(json.dumps({"id": rid, "clase": clase, "fallas": fallas}), encoding="utf-8")
        if lineas is not None:
            (ruta / "transientlist.dat").write_text(_dat(lineas), encoding="latin-1")
        if isinstance(inicio, float):
            (ruta / "validacion.json").write_text(json.dumps({"corrida": rid, "t_inicio_real": inicio}), encoding="utf-8")
        elif isinstance(inicio, str):
            filas_csv.append([Path(carpeta).name, clase, "OK", "", inicio.split(":")[1]])
        origen = "auto" if carpeta.startswith("auto/") else "manual"
        corridas.append(Corrida(rid, clase, origen, f"{carpeta}/plotdata.csv", estado="usable"))
    with open(raiz / "validacion_corridas.csv", "w", encoding="utf-8-sig", newline="") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["corrida", "clase", "estado", "t_plan", "t_inicio_real"])
        escritor.writerows(filas_csv)
    return SimpleNamespace(raiz=raiz, corridas=corridas, por_id={c.id: c for c in corridas})


def cargar_sinteticas_etapa1():
    """`construir_sinteticas` de `tests/etapa1/conftest.py`, cargado por ruta (no es un paquete)."""
    ruta = RAIZ_PRUEBAS / "etapa1" / "conftest.py"
    especificacion = importlib.util.spec_from_file_location("sinteticas_etapa1", ruta)
    modulo = importlib.util.module_from_spec(especificacion)
    especificacion.loader.exec_module(modulo)
    return modulo
