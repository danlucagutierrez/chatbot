import os
import re
import requests
from dotenv import load_dotenv
from telebot.types import Message

try:
    import services
except (ImportError, ModuleNotFoundError):
    import sys
    path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    sys.path.insert(1, path)

from services.telegram_bot import TelegramBot
from services.weather_forecast import WeatherForecast


load_dotenv()
TB_API_KEY = os.getenv('TB_API_KEY')
OWM_API_KEY = os.getenv('OWN_API_KEY')


def build_message_chatbot(weather_details: dict) -> tuple:
    """
    Construye el mensaje para el Chatbot basado en los detalles del clima.

    :param weather_details: Detalles del clima.
    :type weather_details: dict
    :return: Tupla que contiene el mensaje del chatbot y la URL de la imagen (si está disponible).
    :rtype: tuple
    """
    chatbot_message = 'WeatherWiz 💬\n\n'
    chatbot_message_imagen = None

    for key, value in weather_details.items():
        if not value:
            continue
        if key == 'weather_of_the_day':
            chatbot_message += f'{value}\n'
        elif key == 'latest_weather_update':
            chatbot_message += f'Última actualización: {value}\n'
        elif key == 'weather_of_the_day':
            chatbot_message += f'Estado del clima: {value}\n'
        elif key == 'sunset_time':
            chatbot_message += f'Atardecer: {value}\n'
        elif key == 'sunrise_time':
            chatbot_message += f'Amanacer: {value}\n'
        elif key == 'feels_like':
            chatbot_message += f'Sensación térmica: {value}\n'
        elif key == 'temp':
            chatbot_message += f'Temperatura: {value}\n'
        elif key == 'max_temp':
            chatbot_message += f'Rango máximo: {value}\n'
        elif key == 'min_temp':
            chatbot_message += f'Rango mínimo: {value}\n'
        elif key == 'pressure':
            chatbot_message += f'Presión: {value}\n'
        elif key == 'visibility':
            chatbot_message += f'Visibilidad: {value}\n'
        elif key == 'wind_speed':
            chatbot_message += f'Velocidad del viento: {value}\n'
        elif key == 'clouds':
            chatbot_message += f'Nubes: {value}\n'
        elif key == 'rain':
            chatbot_message += f'Lluvia: {value}\n'
        elif key == 'snow':
            chatbot_message += f'Nieve: {value}\n'
        elif key == 'humidity':
            chatbot_message += f'Humedad: {value}\n'
        elif key == 'weather_icon_url':
            chatbot_message_imagen = value
        elif key == 'uvi':
            chatbot_message += f'UVI: {value}\n'
        elif key == 'precipitation_probability':
            chatbot_message += f'Probabilidad de precipitaciones: {value}\n'

        if key == 'most_cold':
            chatbot_message += f'Día más frío: {value[0]} a las {value[1]}\n'
        elif key == 'most_hot':
            chatbot_message += f'Día más cálido: {value[0]} a las {value[1]}\n'
        elif key == 'most_humid':
            chatbot_message += f'Día más humedo: {value[0]} a las {value[1]}\n'
        elif key == 'most_rainy':
            chatbot_message += f'Día más lluvioso: {value[0]} a las {value[1]}\n'
        elif key == 'most_snowy':
            chatbot_message += f'Día más nevado: {value[0]} a las {value[1]}\n'
        elif key == 'most_windy':
            chatbot_message += f'Día más ventoso: {value[0]} a las {value[1]}\n'

    return chatbot_message, chatbot_message_imagen


if __name__ == '__main__':
    """
    Este script sirve como punto de entrada principal para el Chatbot de WeatherWiz.
    Configura el bot de Telegram y maneja los mensajes enviados por los usuarios.

    Antes de ejecutar este script, asegúrate de haber configurado las variables de entorno
    TB_API_KEY y OWN_API_KEY en tu archivo .env con las claves de la API de Telegram y OpenWeatherMap, respectivamente.

    Para iniciar el Chatbot, se crea una instancia de WeatherForecast con la clave de API de OpenWeatherMap
    y la ubicación deseada. Luego, se crea una instancia de TelegramBot con la clave de API de Telegram,
    el nombre del bot, su uso y funcionalidad, así como el controlador de mensajes. Finalmente, se inicia
    el bot de Telegram.

    El bot responde a diferentes comandos de usuario para proporcionar información meteorológica, incluyendo
    el clima actual, el pronóstico extendido y detalles adicionales del clima.

    Ejemplo de uso:
        python main.py
    """

    chatbot_name = 'WeatherWiz 💬'
    chatbot_use = '\n.Clima actual. \n.Pronostico extendido. \n.Detalle extendido.'
    chatbot_funcionality = 'WeatherWiz brinda información meteorológica.'

    location = 'San Miguel, Buenos Aires, Argentina'  # TESTING.

    def message_handler(message: Message) -> None:
        """
        Maneja los mensajes enviados por un usuario del Chatbot.

        :param message: El mensaje recibido.
        :type message: telebot.types.Message
        """

        user_id = message.chat.id
        user_first_name = message.from_user.first_name
        user_message = message.text

        chatbot_message = None
        chatbot_message_imagen = None

        if re.search(r'pronostico actual|clima actual', user_message, re.IGNORECASE):
            current_weather = weather_forecast.get_current_weather()
            weather_details = weather_forecast.get_weather_details(
                current_weather)
            chatbot_message, chatbot_message_imagen = build_message_chatbot(
                weather_details)

            telegram_bot.bot.send_message(user_id, chatbot_message)

        if re.search(r'pronostico extendido|clima extendido', user_message, re.IGNORECASE):
            forecast = weather_forecast.get_forecast()
            dates = weather_forecast.datetime_manager.generate_next_dates()
            for date in dates:
                weather = weather_forecast.get_weather_at_date(forecast, date)
                weather_details = weather_forecast.get_weather_details(weather)
                chatbot_message, _ = build_message_chatbot(weather_details)

                telegram_bot.bot.send_message(user_id, chatbot_message)

        if re.search(r'detalle extendido', user_message, re.IGNORECASE):
            chatbot_message, _ = build_message_chatbot(
                weather_forecast.get_extended_forecast())

            telegram_bot.bot.send_message(user_id, chatbot_message)

        if not chatbot_message:
            chatbot_message = f'Disculpa {user_first_name} no comprendí tu consulta. \n¿Podrías explicarte mejor? 😀'

            telegram_bot.bot.send_message(user_id, chatbot_message)

        if chatbot_message_imagen:
            response_url = requests.get(chatbot_message_imagen).content
            telegram_bot.bot.send_photo(user_id, response_url)

    weather_forecast = WeatherForecast(
        OWM_API_KEY, location)

    telegram_bot = TelegramBot(TB_API_KEY, chatbot_name, chatbot_use,
                               chatbot_funcionality, message_handler)

    telegram_bot.start_bot()