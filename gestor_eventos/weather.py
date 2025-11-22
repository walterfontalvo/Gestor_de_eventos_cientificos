"""Consulta de clima usando concurrencia y la API pública de Open-Meteo."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from typing import Dict, Iterable

from .models import Ciudad

API_URL = "https://api.open-meteo.com/v1/forecast"


def _construir_url(ciudad: Ciudad) -> str:
    query = urllib.parse.urlencode(
        {
            "latitude": ciudad.latitud,
            "longitude": ciudad.longitud,
            "current_weather": "true",
        }
    )
    return f"{API_URL}?{query}"


def _consultar_ciudad(ciudad: Ciudad, timeout: float = 10.0) -> Dict:
    url = _construir_url(ciudad)
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:  # nosec B310
            data = json.loads(response.read().decode("utf-8"))
            actual = data.get("current_weather", {})
            return {
                "ciudad": ciudad.nombre,
                "pais": ciudad.pais,
                "temperatura": actual.get("temperature"),
                "viento": actual.get("windspeed"),
                "hora": actual.get("time"),
            }
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
        return {
            "ciudad": ciudad.nombre,
            "pais": ciudad.pais,
            "error": str(exc),
        }


def consultar_clima_ciudades(
    ciudades: Iterable[Ciudad],
    max_workers: int = 5,
) -> Dict[str, Dict]:
    """Consulta concurrente del clima para cada ciudad."""

    resultados: Dict[str, Dict] = {}
    ciudades_lista = list(ciudades)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futuro_por_ciudad = {
            executor.submit(_consultar_ciudad, ciudad): ciudad for ciudad in ciudades_lista
        }
        for futuro in as_completed(futuro_por_ciudad):
            ciudad = futuro_por_ciudad[futuro]
            resultado = futuro.result()
            resultados[f"{ciudad.nombre}|{ciudad.pais}"] = resultado
    return resultados


__all__ = ["consultar_clima_ciudades", "_construir_url"]
