import requests


def obtener_clima():
    url = "https://api.open-meteo.com/v1/forecast"

    parametros = {
        "latitude": -0.1807,
        "longitude": -78.4678,
        "current": "temperature_2m,relative_humidity_2m",
        "timezone": "America/Guayaquil",
    }

    respuesta = requests.get(
        url,
        params=parametros,
        timeout=10,
    )

    respuesta.raise_for_status()
    datos = respuesta.json()

    return {
        "ciudad": "Quito",
        "temperatura": datos["current"]["temperature_2m"],
        "humedad": datos["current"]["relative_humidity_2m"],
        "hora": datos["current"]["time"],
    }