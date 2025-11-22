"""Pruebas unitarias para los modelos de eventos."""

from __future__ import annotations

import unittest
from datetime import datetime

from gestor_eventos.models import Ciudad, Conferencia, Evento


class TestCiudad(unittest.TestCase):
    def test_normaliza_campos_y_descripcion(self) -> None:
        ciudad = Ciudad(" bogotá ", " colombia ", 4.7, -74.0, _descripcion="  capital ")
        self.assertEqual(ciudad.nombre, "Bogotá")
        self.assertEqual(ciudad.pais, "Colombia")
        self.assertEqual(ciudad.descripcion, "capital")

    def test_to_dict_y_desde_dict(self) -> None:
        original = Ciudad("Medellín", "Colombia", 6.2, -75.5, _descripcion="ciudad")
        copia = Ciudad.desde_dict(original.to_dict())
        self.assertEqual(copia.nombre, original.nombre)
        self.assertEqual(copia.descripcion, original.descripcion)


class TestEvento(unittest.TestCase):
    def setUp(self) -> None:
        self.ciudad = Ciudad("Quito", "Ecuador", -0.18, -78.46)

    def test_capacidad_positiva(self) -> None:
        with self.assertRaises(ValueError):
            Evento("Evento", datetime.now(), self.ciudad, 0)

    def test_asistentes_no_superan_capacidad(self) -> None:
        evento = Evento("Evento", datetime.now(), self.ciudad, 100)
        evento.registrar_asistentes(40)
        self.assertEqual(evento.asistentes_registrados, 40)
        with self.assertRaises(ValueError):
            evento.registrar_asistentes(70)


class TestConferencia(unittest.TestCase):
    def test_agrega_ponentes_sin_duplicar(self) -> None:
        conferencia = Conferencia(
            "Conferencia",
            datetime.now(),
            Ciudad("Lima", "Perú", -12.04, -77.03),
            capacidad_maxima=200,
            tematica="IA",
            ponentes=["Dr. A"],
        )
        conferencia.agregar_ponente("Dr. B")
        conferencia.agregar_ponente("Dr. A")
        self.assertEqual(conferencia.ponentes, ["Dr. A", "Dr. B"])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
