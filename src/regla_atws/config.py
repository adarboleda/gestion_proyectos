"""Constantes de la regla determinista de ATWS (KAN-22)."""

# Señales del sistema de protección en el registro de eventos de PCTran (validador del proyecto).
# «Reactor Scram» no es una señal de demanda: es el resultado del disparo.
SENALES_DISPARO = (
    "Scram ", "Low SG Level", "Turbine trip", "Turbine Trip", "RCP-A trip",
    "Hi RX", "High RX", "Lo RX", "low RX", "OTDT", "OPDT", "Hi Flux", "High Flux",
)
TEXTO_SCRAM = "Reactor Scram"
TIPO_ALTO_FLUJO = "scram high flux"

PUNTO_ALTO_FLUJO = 118.0  # % del nominal: punto de disparo por alto flujo neutrónico
ESPERA_S = 2.0  # s tras la demanda de disparo (KAN-22)
META_S = 3.0  # s: detectar el ATWS en 3 s o menos desde la demanda

SALIDA_POR_DEFECTO = "resultados_regla_atws"

AVISO = (
    "Recomendación para el operador: la regla no actúa sobre la planta ni sustituye la lógica de "
    "protección; el operador valida y ejecuta cualquier acción."
)
