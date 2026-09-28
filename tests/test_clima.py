from unittest.mock import Mock, patch

import pytest
import requests

from app import app


@pytest.fixture
def cliente():
    app.config["TESTING"] = True

    with app.test_client() as cliente:
        yield cliente


def test_clima_exitoso(cliente):
    respuesta_simulada = Mock()
    respuesta_simulada.json.return_value = {
        "current": {
            "temperature_2m": 18.5,
            "relative_humidity_2m": 70,
            "time": "2026-09-28T09:30",
        }
    }

    with patch(
        "services.clima_service.requests.get",
        return_value=respuesta_simulada,
    ) as peticion:
        respuesta = cliente.get("/api/clima")

    assert respuesta.status_code == 200
    assert respuesta.get_json() == {
        "ciudad": "Quito",
        "temperatura": 18.5,
        "humedad": 70,
        "hora": "2026-09-28T09:30",
    }

    peticion.assert_called_once_with(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": -0.1807,
            "longitude": -78.4678,
            "current": "temperature_2m,relative_humidity_2m",
            "timezone": "America/Guayaquil",
        },
        timeout=10,
    )
    respuesta_simulada.raise_for_status.assert_called_once()


def test_clima_timeout(cliente):
    with patch(
        "services.clima_service.requests.get",
        side_effect=requests.exceptions.Timeout,
    ):
        respuesta = cliente.get("/api/clima")

    assert respuesta.status_code == 504
    assert respuesta.get_json() == {
        "error": "El servicio del clima tardó demasiado."
    }


def test_clima_error_http(cliente):
    respuesta_simulada = Mock()
    respuesta_simulada.raise_for_status.side_effect = (
        requests.exceptions.HTTPError("Error del proveedor")
    )

    with patch(
        "services.clima_service.requests.get",
        return_value=respuesta_simulada,
    ):
        respuesta = cliente.get("/api/clima")

    assert respuesta.status_code == 502
    assert respuesta.get_json() == {
        "error": "No se pudo consultar el servicio del clima."
    }