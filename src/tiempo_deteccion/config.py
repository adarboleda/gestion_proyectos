"""Constantes de la medición del tiempo de detección desde la falla (008)."""
import re

# Metas del proyecto (plan del Hito 1)
META_DIAGNOSTICO_S = 10.0  # familia del evento confirmada en ≤ 10 s desde la falla
META_ATWS_S = 3.0  # ATWS reconocido en ≤ 3 s desde la demanda de disparo

# Una corrida es «incierta» si el validador ve cambios más de 2 s antes del instante de la falla
TOLERANCIA_INCIERTA_S = 2.0

# Iniciador de la falla en el Transient Report (research.md §1). Solo se busca en estas clases:
# en LOCA y NORM el registro solo trae consecuencias (por ejemplo, el disparo de turbina tras el scram).
CLASES_CON_REGISTRO = ("ATWS", "TRIP_OK")
PATRON_INICIADOR = re.compile(
    r"^(FWIV #\d+ Position Change: 0%"  # pérdida de agua de alimentación (cierre de válvulas)
    r"|RCP-A trip"  # disparo de una bomba del refrigerante
    r"|Turbine Trip Control Change: True"  # disparo de turbina
    r"|AFW Turbine Valve #1 Position Change: 100%)"  # pérdida de energía exterior
)
FALLA_EXCLUIDA = "8"  # «fallo del disparo»: siempre en t = 0, no es el iniciador

FUENTE_REGISTRO = "registro"
FUENTE_PROGRAMADO = "programado"
FUENTE_NINGUNA = "ninguna"

MODELO_POR_DEFECTO = "modelos/etapa1"
SALIDA_POR_DEFECTO = "resultados_tiempo_deteccion"
ARCHIVOS = ("tiempos.json", "tiempos.csv", "lineas_tiempo.csv", "reporte.txt")
CONJUNTOS_EVALUADOS = ("val", "test")

AVISO = (
    "Resultados consultivos: el diagnóstico de Etapa 1 y la regla de ATWS son recomendaciones para el "
    "operador; no actúan sobre la planta ni sustituyen la lógica de protección."
)
