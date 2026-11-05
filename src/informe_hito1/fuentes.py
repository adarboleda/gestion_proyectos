"""Lectura de los archivos de resultados de cada tarea, con su SHA-256 para la trazabilidad."""
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Tuple

from informe_hito1.config import FUENTES


class ErrorFuente(Exception):
    """Archivo de resultados ausente o ilegible: nombra el archivo y el comando que lo genera."""

    def __init__(self, archivo: str, causa: str, comando: str):
        self.archivo, self.causa, self.comando = archivo, causa, comando
        super().__init__(f"ERROR: {archivo}: {causa} (genéralo con: {comando})")


def cargar_fuentes(rutas: Dict[str, Path]) -> Tuple[Dict[str, Dict], List[Dict]]:
    """Lee las cinco fuentes. Devuelve (datos por clave y alias, registro de fuentes con SHA-256)."""
    datos: Dict[str, Dict] = {}
    registro: List[Dict] = []
    for clave, fuente in FUENTES.items():
        carpeta = Path(rutas[clave])
        datos[clave] = {}
        for alias, (nombre, requeridas) in fuente["archivos"].items():
            ruta = carpeta / nombre
            mostrado = f"{fuente['carpeta']}/{nombre}"
            if not ruta.is_file():
                raise ErrorFuente(str(ruta), "no existe el archivo de resultados", fuente["comando"])
            contenido = ruta.read_bytes()
            try:
                objeto = json.loads(contenido.decode("utf-8"))
            except (UnicodeDecodeError, ValueError) as error:
                raise ErrorFuente(str(ruta), f"archivo ilegible ({error.__class__.__name__})", fuente["comando"]) from None
            faltan = [k for k in requeridas if not isinstance(objeto, dict) or k not in objeto]
            if faltan:
                raise ErrorFuente(str(ruta), f"faltan las claves {', '.join(faltan)}", fuente["comando"])
            datos[clave][alias] = objeto
            registro.append({"clave": clave, "kan": fuente["kan"], "responsable": fuente["responsable"],
                             "funcionalidad": fuente["funcionalidad"], "comando": fuente["comando"],
                             "archivo": mostrado, "sha256": hashlib.sha256(contenido).hexdigest()})
    return datos, registro
