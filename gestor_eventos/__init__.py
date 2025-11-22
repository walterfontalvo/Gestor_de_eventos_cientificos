"""Paquete principal para la gestión de eventos científicos."""

from .models import Ciudad, Evento, Conferencia
from .processing import (
    filtrar_eventos_por_ciudad,
    ordenar_eventos_por_fecha,
    resumen_asistentes,
)
from .storage import (
    RUTA_DB,
    RUTA_JSON,
    cargar_eventos_de_json,
    exportar_eventos_a_json,
    guardar_ciudad_en_db,
    guardar_evento_en_db,
    inicializar_db,
    listar_ciudades_db,
    listar_eventos_db,
)
from .weather import consultar_clima_ciudades

__all__ = [
    "Ciudad",
    "Evento",
    "Conferencia",
    "filtrar_eventos_por_ciudad",
    "ordenar_eventos_por_fecha",
    "resumen_asistentes",
    "RUTA_DB",
    "RUTA_JSON",
    "cargar_eventos_de_json",
    "exportar_eventos_a_json",
    "guardar_ciudad_en_db",
    "guardar_evento_en_db",
    "inicializar_db",
    "listar_ciudades_db",
    "listar_eventos_db",
    "consultar_clima_ciudades",
]
