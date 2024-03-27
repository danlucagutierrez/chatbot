import os
import re
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


def build_message(weather_details: dict, type_query: str) -> tuple:
    """
    Construye el mensaje para el Chatbot basado en los detalles del clima.

    :param weather_details: Detalles del clima.
    :type weather_details: dict
    :param type_query: Tipo de consulta.
    :type type_query: str
    :return: Tupla que contiene el mensaje del chatbot y la URL de la imagen (si está disponible).
    :rtype: tuple
    """
    message_parts = ['WeatherWiz 💬\n\n']

    if type_query == 'detailed_extended_weather':
        message_parts.append('Día más...\n')

    message_sticker = None

    message_mapping = {
        'weather_of_the_day': '{}\n',
        'latest_weather_update': 'Última actualización: {}\n',
        'weather_status': 'Estado del clima: {}\n',
        'sunset_time': 'Atardecer: {}\n',
        'sunrise_time': 'Amanecer: {}\n',
        'feels_like': 'Sensación térmica: {}\n',
        'temp': 'Temperatura: {} 🌡\n',
        'max_temp': 'Rango máximo: {}\n',
        'min_temp': 'Rango mínimo: {}\n',
        'pressure': 'Presión atmosférica: {}\n',
        'visibility': 'Visibilidad: {}\n',
        'wind_speed': 'Velocidad del viento: {}\n',
        'clouds': 'Nubes: {}\n',
        'rain': 'Lluvia: {}\n',
        'snow': 'Nieve: {}\n',
        'humidity': 'Humedad: {}\n',
        'weather_status_icon': None,
        'uvi': 'UVI: {}\n',
        'precipitation_probability': 'Probabilidad de precipitaciones: {}\n',
        'most_cold': '...frío: {} - {} ❄\n',
        'most_hot': '...cálido: {} - {} ☀\n',
        'most_humid': '...húmedo: {} - {} 🌫\n',
        'most_rainy': '...lluvioso: {} - {} 🌧\n',
        'most_snowy': '...nevado: {} - {} 🌨\n',
        'most_windy': '...ventoso: {} - {} 🌬\n'
    }

    for key, value in weather_details.items():
        if value is None:
            continue

        if type_query == 'extended_weather' and \
            key in ('latest_weather_update', 'sunset_time', 'sunrise_time', 'max_temp', 'min_temp'):
                continue

        message_template = message_mapping.get(key)
        if message_template:
            if isinstance(value, tuple):
                message_parts.append(message_template.format(*value))
            else:
                message_parts.append(message_template.format(value))
        if not message_template and key == 'weather_status_icon':
            message_sticker = value

    return ''.join(message_parts), message_sticker

# TelegramBot method.
def message_handler(message: Message) -> None:
    """
    Maneja los mensajes enviados por un usuario del Chatbot.

    :param message: El mensaje recibido.
    :type message: telebot.types.Message
    """

    user_id = message.chat.id
    user_first_name = message.from_user.first_name
    user_message = message.text

    type_query = None

    chatbot_message = None

    if re.search(r'pronostico actual|clima actual', user_message, re.IGNORECASE):
        type_query = 'current_weather'
        current_weather = weather_forecast.get_current_weather()
        weather_details = weather_forecast.get_weather_details(
            current_weather)
        chatbot_message, chatbot_message_sticker = build_message(
            weather_details, type_query)

        telegram_bot.send_message_bot(user_id, chatbot_message)
        telegram_bot.send_message_bot(user_id, chatbot_message_sticker)

    if re.search(r'pronostico extendido|clima extendido', user_message, re.IGNORECASE):
        type_query = 'extended_weather'
        forecast = weather_forecast.get_forecast()
        dates = weather_forecast.datetime_manager.generate_next_dates()
        for date in dates:
            weather = weather_forecast.get_weather_at_date(forecast, date)
            weather_details = weather_forecast.get_weather_details(weather)
            chatbot_message, chatbot_message_sticker = build_message(weather_details, type_query)

            telegram_bot.send_message_bot(user_id, chatbot_message)
            telegram_bot.send_message_bot(user_id, chatbot_message_sticker)

    if re.search(r'detalle extendido', user_message, re.IGNORECASE):
        type_query = 'detailed_extended_weather'
        chatbot_message, _ = build_message(
            weather_forecast.get_extended_forecast(), type_query)

        telegram_bot.send_message_bot(user_id, chatbot_message)

    if not chatbot_message:
        chatbot_message = f'Disculpa {user_first_name} no comprendí tu consulta. \
                            \n¿Podrías explicarte mejor? 😀'

        telegram_bot.send_message_bot(user_id, chatbot_message)


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

    CHATBOT_NAME = 'WeatherWiz'
    CHATBOT_START = f'{CHATBOT_NAME} 💬'
    CHATBOT_HELP = f'\n• Clima actual. \
                        \n• Pronostico extendido. \
                        \n• Detalle extendido.'
    CHATBOT_DESCRIPTION = f'{CHATBOT_NAME} 💬 brinda información meteorológica.'

    LOCATION = 'San Miguel, Buenos Aires, Argentina'  # TESTING.

    weather_forecast = WeatherForecast(OWM_API_KEY, LOCATION)

    telegram_bot = TelegramBot(TB_API_KEY, CHATBOT_START, CHATBOT_HELP,
                            CHATBOT_DESCRIPTION, message_handler)

    telegram_bot.start_bot()