import os
from time import sleep
from functools import wraps

# pyowm library.
from pyowm.owm import OWM
from pyowm.weatherapi25.weather import Weather
from pyowm.weatherapi25.forecast import Forecast
from pyowm.utils.config import get_default_config
from pyowm.commons.exceptions import ConfigurationError, APIRequestError, APIResponseError

try:
    import utils
except (ImportError, ModuleNotFoundError):
    import sys
    path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    sys.path.insert(1, path)

from utils.datetime_manager import DatetimeManager


def retry_on_error(max_retries=3, delay=5):
    """
    Decorador para manejar errores de la libreria pyowm.

    Reintenta la función decorada en caso de un error de lectura de tiempo,
    hasta un número máximo de intentos, con un retraso entre intentos.

    :param max_retries: Número máximo de intentos antes de fallar.
    :type max_retries: int
    :param delay: Tiempo de espera entre reintentos en segundos.
    :type delay: int
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            error = None
            attempts = 0
            while attempts < max_retries:
                try:
                    return func(*args, **kwargs)
                except (ConfigurationError, APIRequestError, APIResponseError) as e:
                    error = e
                    print(f"Error: {e}. Retrying in {delay} seconds...")
                    sleep(delay)
                    attempts += 1
            raise RuntimeError(
                f"Failed after {max_retries} retries. Type error: {type(error)}.")
        return wrapper
    return decorator


class WeatherForecast:
    """
    Clase destinada a gestionar consultas sobre el pronósticos del clima utilizando la libreria pyowm, 
    que facilita el acceso a la API de OpenWeatherMap.

    pyowm es una libreria Python que proporciona una interfaz fácil de usar para acceder a la API de OpenWeatherMap y
    obtener información meteorológica, incluidos datos como el clima actual,
    pronósticos de 3 horas para 5 días, mapas básicos del clima y otros servicios relacionados.

    Para utilizar esta clase, es necesario instalar la libreria pyowm. 
    Puede encontrar más información y documentación
    sobre pyowm en los siguientes enlaces:
    - PyPI: https://pypi.org/project/pyowm/
    - Documentación: https://pyowm.readthedocs.io/en/latest/

    Para utilizar esta clase, es necesario obtener una clave de API (API key) gratuita de OpenWeatherMap, la cual
    permite realizar hasta 60 llamadas por minuto y un máximo de 1,000,000 llamadas al mes.

    API de OpenWeatherMap en su sitio web oficial: https://openweathermap.org/

    - API's:
        - https://openweathermap.org/current
        - https://openweathermap.org/forecast5

    Atributos:
        api_key (str): Clave de API (API key) proporcionada por OpenWeatherMap para acceder a la API.
        location (str): Ubicación para la cual se desea obtener el pronóstico del clima.
    """

    @retry_on_error()
    def __init__(self, api_key: str, location: str) -> None:
        """
        Inicializa la clase WeatherForecast.

        :param api_key: Clave de API de OpenWeatherMap.
        :type api_key: str
        :param location: Ubicación para la cual se desea obtener el pronóstico del tiempo.
        :type location: str
        """
        self.api_key = api_key
        self.location = location
        self.config_dict = get_default_config()
        self.config_dict['language'] = 'es'
        self.config_dict['timeout_secs'] = 5
        self.config_dict['max_retries'] = 3
        self.owm = OWM(api_key)
        self.weather_manager = self.owm.weather_manager()
        self.datetime_manager = DatetimeManager()

    @retry_on_error()
    def get_forecast(self, interval: str = '3h') -> Forecast:
        """
        Obtiene el pronóstico del tiempo para la ubicación especificada, para
        un rango de 5 días, con intervalos de pronóstico cada 3 horas.

        :param interval: Intervalo de tiempo para el pronóstico (predeterminado: 3 horas).
        :type interval: str
        :return: Pronóstico del tiempo.
        :rtype: pyowm.weatherapi25.forecast.Forecast
        """
        forecast = self.weather_manager.forecast_at_place(
            self.location, interval=interval)
        return forecast

    @retry_on_error()
    def get_weather_at_date(self, forecast: Forecast, date: str) -> Weather:
        """
        Obtiene el estado del tiempo en una fecha específica del pronóstico.

        :param forecast: Pronóstico del tiempo.
        :type forecast: pyowm.weatherapi25.forecast.Forecast
        :param date: Fecha para la cual se desea obtener el estado del tiempo.
        :type date: str
        :return: Estado del tiempo en la fecha especificada.
        :rtype: pyowm.weatherapi25.weather.Weather
        """
        weather = forecast.get_weather_at(date)
        return weather

    @retry_on_error()
    def get_current_weather(self) -> Weather:
        """
        Obtiene el estado del tiempo actual para la ubicación especificada.

        :return: Estado del tiempo actual.
        :rtype: pyowm.weatherapi25.weather.Weather
        """
        observation = self.weather_manager.weather_at_place(self.location)
        weather = observation.weather
        # Importante: reception_time del object observation define el momento en el que se consulta, pero reference_time del object weather define la ultima actualización del tiempo para la úbicación.
        return weather

    def get_weather_details(self, weather: Weather) -> dict:
        """
        Obtiene detalles específicos del estado del tiempo.

        :param weather: Estado del tiempo.
        :type weather: pyowm.weatherapi25.weather.Weather
        :return: Detalles del estado del tiempo.
        :rtype: dict
        """
        details = dict()
        details['weather_of_the_day'], details['latest_weather_update'] = self.datetime_manager.build_day_and_time(
            weather.reference_time())
        details["weather_status"] = weather.detailed_status.capitalize()
        details["sunset_time"] = self._get_sunset_time(weather)
        details["sunrise_time"] = self._get_sunrise_time(weather)
        details.update(self._get_temperature_details(weather))
        details["pressure"] = self._get_pressure(weather)
        details["visibility"] = self._get_visibility(weather)
        details["wind_speed"] = self._get_wind_speed(weather)
        details["clouds"] = self._get_clouds(weather)
        details["rain"] = self._get_rain(weather)
        details["snow"] = self._get_snow(weather)
        details["humidity"] = self._get_humidity(weather)
        details["weather_icon_url"] = self._get_weather_icon_url(weather)
        details["uvi"] = self._get_uvi(weather)
        details["precipitation_probability"] = self._get_precipitation_probability(
            weather)
        return details

    def get_extended_forecast(self) -> dict:
        """
        Obtiene el pronóstico extendido para la ubicación especificada.

        :return: Pronóstico extendido.
        :rtype: dict
        """
        forecast = self.get_forecast()
        details = dict()
        details["most_cold"] = self._get_most_cold(forecast)
        details["most_hot"] = self._get_most_hot(forecast)
        details["most_humid"] = self._get_most_humid(forecast)
        details["most_rainy"] = self._get_most_rainy(forecast)
        details["most_snowy"] = self._get_most_snowy(forecast)
        details["most_windy"] = self._get_most_windy(forecast)
        return details

    def _get_sunset_time(self, weather: Weather) -> str or None:
        """
        Obtiene la hora de la puesta del sol.

        :param weather: Estado del tiempo.
        :type weather: pyowm.weatherapi25.weather.Weather
        :return: Hora de la puesta del sol en formato HH:MM:SS o None si no está disponible.
        :rtype: str or None
        """
        sunset_time = None
        weather_sunset = weather.sunset_time()
        if weather_sunset:
            sunset_time = self.datetime_manager.convert_utc_to_arg(
                weather_sunset)
        return sunset_time

    def _get_sunrise_time(self, weather: Weather) -> str or None:
        """
        Obtiene la hora de la salida del sol.

        :param weather: Estado del tiempo.
        :type weather: pyowm.weatherapi25.weather.Weather
        :return: Hora de la salida del sol en formato HH:MM:SS o None si no está disponible.
        :rtype: str or None
        """
        sunrise_time = None
        weather_sunrise = weather.sunrise_time()
        if weather_sunrise:
            sunrise_time = self.datetime_manager.convert_utc_to_arg(
                weather_sunrise)
        return sunrise_time

    def _get_temperature_details(self, weather: Weather) -> dict:
        """
        Obtiene los detalles de temperatura del estado del tiempo.

        :param weather: Estado del tiempo.
        :type weather: pyowm.weatherapi25.weather.Weather
        :return: Detalles de temperatura (por defecto en celsius).
        :rtype: dict
        """

        """
        Atención:
        Temperatura mínima/máxima en la API meteorológica actual y API de previsión
        No confunda los parámetros mínimos y máximos en nuestras API meteorológicas.
        En API de pronóstico de 5 días / 3 horas , API de pronóstico por hora y API de clima actual : 
        temp_min y temp_max son parámetros opcionales que significan la temperatura mínima / máxima en 
        la ciudad en el momento actual solo para su referencia. Para grandes ciudades y megalópolis 
        geográficamente expandidas podría ser aplicable. En la mayoría de los casos, los parámetros 
        temp_min y temp_max tienen el mismo volumen que 'temp'. Utilice opcionalmente los parámetros 
        temp_min y temp_max en la API meteorológica actual.

        Example of Current Weather API response:
        "main":{
        "temp":306.15, //current temperature
        "pressure":1013,
        "humidity":44,
        "temp_min":30.15, //min current temperature in the city
        "temp_max":306.15 //max current temperature in the city
        },

        Fuente: https://openweathermap.org/forecast5
        """

        temperature = weather.temperature(unit='celsius')
        details = dict()
        if temperature:
            details["feels_like"] = f'{temperature.get("feels_like")}°' if temperature.get(
                "feels_like") else None
            details["temp"] = f'{temperature.get("temp")}°' if temperature.get(
                "temp") else None
            details["max_temp"] = f'{temperature.get("temp_max")}°' if temperature.get(
                "temp_max") else None
            details["min_temp"] = f'{temperature.get("temp_min")}°' if temperature.get(
                "temp_min") else None
        return details

    def _get_pressure(self, weather: Weather) -> str or None:
        """
        Obtiene la presión atmosférica del estado del tiempo.

        :param weather: Estado del tiempo.
        :type weather: pyowm.weatherapi25.weather.Weather
        :return: Presión atmosférica.
        :rtype: str or None
        """
        pressure = None
        weather_pressure = weather.barometric_pressure()
        if weather.barometric_pressure():
            pressure = weather_pressure.get("press")
            if not pressure:
                return pressure
            else:
                if pressure < 500:
                    level_pressure = 'Baja'
                elif pressure >= 500 and pressure <= 1500:
                    level_pressure = 'Media'
                elif level_pressure > 1500:
                    level_pressure = 'Alta'
            pressure = f'{pressure}hPa - {level_pressure}'
        return pressure

    def _get_visibility(self, weather: Weather) -> str or None:
        """
        Obtiene la visibilidad del estado del tiempo.

        :param weather: Estado del tiempo.
        :type weather: pyowm.weatherapi25.weather.Weather
        :return: Visibilidad (por defecto en kilómetros por hora km/h).
        :rtype: str or None
        """
        visibility = None
        weather_visibily = weather.visibility(unit='kilometers')
        if weather_visibily:
            visibility = f'{weather_visibily}km'
        return visibility

    def _get_wind_speed(self, weather: Weather) -> str or None:
        """
        Obtiene la velocidad del viento del estado del tiempo.

        :param weather: Estado del tiempo.
        :type weather: pyowm.weatherapi25.weather.Weather
        :return: Velocidad del viento (por defecto en kilómetros por hora km/h).
        :rtype: str or None
        """
        weather_wind = weather.wind(unit='km_hour')
        if weather_wind:
            return f'{round(weather_wind.get("speed"), 2)}km/h' if weather_wind.get("speed") else None

    def _get_clouds(self, weather: Weather) -> str or None:
        """
        Obtiene la cobertura de nubes del estado del tiempo.

        :param weather: Estado del tiempo.
        :type weather: pyowm.weatherapi25.weather.Weather
        :return: Cobertura de nubes en porcentaje.
        :rtype: str or None
        """
        return None if not weather.clouds else f'{weather.clouds}%'

    def _get_rain(self, weather: Weather) -> str or None:
        """
        Obtiene la cantidad de lluvia del estado del tiempo.

        :param weather: Estado del tiempo.
        :type weather: pyowm.weatherapi25.weather.Weather
        :return: Cantidad de lluvia en milímetros.
        :rtype: str or None
        """
        return None if not weather.rain else f'{weather.rain}mm'

    def _get_snow(self, weather: Weather) -> str or None:
        """
        Obtiene la cantidad de nieve del estado del tiempo.

        :param weather: Estado del tiempo.
        :type weather: pyowm.weatherapi25.weather.Weather
        :return: Cantidad de nieve en milímetros.
        :rtype: str or None
        """
        return None if not weather.snow else f'{weather.snow}mm'

    def _get_humidity(self, weather: Weather) -> int:
        """
        Obtiene la humedad relativa del estado del tiempo.

        :param weather: Estado del tiempo.
        :type weather: pyowm.weatherapi25.weather.Weather
        :return: Humedad relativa en porcentaje.
        :rtype: int
        """
        return None if not weather.humidity else f'{weather.humidity}%'

    def _get_weather_icon_url(self, weather: Weather) -> str:
        """
        Obtiene la url del ícono del estado del tiempo.

        :param weather: Estado del tiempo.
        :type weather: pyowm.weatherapi25.weather.Weather
        :return: Nombre del ícono del clima.
        :rtype: str
        """
        return weather.weather_icon_url()

    def _get_uvi(self, weather: Weather) -> float:
        """
        Obtiene el índice de radiación ultravioleta (UVI) del estado del tiempo.

        :param weather: Estado del tiempo.
        :type weather: pyowm.weatherapi25.weather.Weather
        :return: Índice de radiación ultravioleta.
        :rtype: float
        """
        return weather.uvi

    def _get_precipitation_probability(self, weather: Weather) -> int:
        """
        Obtiene la probabilidad de precipitación del estado del tiempo.

        :param weather: Estado del tiempo.
        :type weather: pyowm.weatherapi25.weather.Weather
        :return: Probabilidad de precipitación en porcentaje.
        :rtype: int
        """
        return None if not weather.precipitation_probability else f'{weather.precipitation_probability}%'

    def _get_most_cold(self, forecast: Forecast) -> tuple:
        """
        Obtiene el momento más frío del pronóstico del tiempo.

        :param forecast: Pronóstico del tiempo.
        :type forecast: pyowm.weatherapi25.forecast.Forecast
        :return: Fecha y hora del momento más frío.
        :rtype: tuple
        """
        most_cold = forecast.most_cold()
        if most_cold:
            seconds = most_cold.reference_time()
            if seconds:
                return self.datetime_manager.build_day_and_time(seconds)

    def _get_most_hot(self, forecast: Forecast) -> tuple:
        """
        Obtiene el momento más caluroso del pronóstico del tiempo.

        :param forecast: Pronóstico del tiempo.
        :type forecast: pyowm.weatherapi25.forecast.Forecast
        :return: Fecha y hora del momento más caluroso.
        :rtype: tuple
        """
        most_hot = forecast.most_hot()
        if most_hot:
            seconds = most_hot.reference_time()
            if seconds:
                return self.datetime_manager.build_day_and_time(seconds)

    def _get_most_humid(self, forecast: Forecast) -> tuple:
        """
        Obtiene el momento más húmedo del pronóstico del tiempo.

        :param forecast: Pronóstico del tiempo.
        :type forecast: pyowm.weatherapi25.forecast.Forecast
        :return: Fecha y hora del momento más húmedo.
        :rtype: tuple
        """
        most_humid = forecast.most_humid()
        if most_humid:
            seconds = most_humid.reference_time()
            if seconds:
                return self.datetime_manager.build_day_and_time(seconds)

    def _get_most_rainy(self, forecast: Forecast) -> tuple:
        """
        Obtiene el momento más lluvioso del pronóstico del tiempo.

        :param forecast: Pronóstico del tiempo.
        :type forecast: pyowm.weatherapi25.forecast.Forecast
        :return: Fecha y hora del momento más lluvioso.
        :rtype: tuple
        """
        most_rainy = forecast.most_rainy()
        if most_rainy:
            seconds = most_rainy.reference_time()
            if seconds:
                return self.datetime_manager.build_day_and_time(seconds)

    def _get_most_snowy(self, forecast: Forecast) -> tuple:
        """
        Obtiene el momento más nevado del pronóstico del tiempo.

        :param forecast: Pronóstico del tiempo.
        :type forecast: pyowm.weatherapi25.forecast.Forecast
        :return: Fecha y hora del momento más nevado.
        :rtype: tuple
        """
        most_snowy = forecast.most_snowy()
        if most_snowy:
            seconds = most_snowy.reference_time()
            if seconds:
                return self.datetime_manager.build_day_and_time(seconds)

    def _get_most_windy(self, forecast: Forecast) -> tuple:
        """
        Obtiene el momento más ventoso del pronóstico del tiempo.

        :param forecast: Pronóstico del tiempo.
        :type forecast: pyowm.weatherapi25.forecast.Forecast
        :return: Fecha y hora del momento más ventoso.
        :rtype: tuple
        """
        most_windy = forecast.most_windy()
        if most_windy:
            seconds = most_windy.reference_time()
            if seconds:
                return self.datetime_manager.build_day_and_time(seconds)