import json
import os
import re
import signal
import threading
from dotenv import load_dotenv
from pymongo import MongoClient
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

try:
    import services
except (ImportError, ModuleNotFoundError):
    import sys
    path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    sys.path.insert(1, path)

from services.telegram_bot import TelegramBot
from services.weather_forecast import WeatherForecast
from services.auth import AuthService
from utils.db_manager import DBManager
from processing.classification_model import ClassificationModel

load_dotenv()
TB_API_KEY = os.getenv("TB_API_KEY")
OWM_API_KEY = os.getenv("OWN_API_KEY")
MONGO_URL = os.getenv("MONGO_URL")

THREADS = False


def set_threads(signum, frame):
    """
    Manejador para la señal SIGINT (Ctrl + C).
    """
    global THREADS
    THREADS = True


signal.signal(signal.SIGINT, set_threads)


def run_telegram_thread():
    """
    Crea el hilo que contreda la ejecución de TelegramBot.
    """
    thread = threading.Thread(name="Chatbot", target=telegram_bot.start_bot)
    thread.start()
    return thread

def run_auth_thread():
    """
    Crea el hilo que contreda la ejecución del autenticador.
    """
    thread = threading.Thread(name="Auth", target=authenticator.start)
    thread.start()
    return thread

def start_mongo():
    client = MongoClient(MONGO_URL)
    return DBManager(client.weatherwiz)


def build_message(weather_details: dict, type_query: str, location: str) -> tuple:
    """
    Construye el mensaje para el Chatbot basado en los detalles del clima.

    :param weather_details: Detalles del clima.
    :type weather_details: dict
    :param type_query: Tipo de consulta.
    :type type_query: str
    :return: Tupla que contiene el mensaje del chatbot, la URL de la imagen (si está disponible) y el estado del clima.
    :rtype: tuple
    """
    message_parts = [f"{CHATBOT_NAME} 💬\n\n"]

    message_parts.append(f'📍 Ubicación: {location}.\n\n')

    if type_query == "detailed_extended_weather":
        message_parts.append("Día más...\n")

    message_sticker = None

    weather_status = None

    message_mapping = {
        "weather_of_the_day": "{}\n",
        "latest_weather_update": "Última actualización: {}\n",
        "weather_status": "Estado del clima: {}\n",
        "sunset_time": "Atardecer: {}\n",
        "sunrise_time": "Amanecer: {}\n",
        "feels_like": "Sensación térmica: {}\n",
        "temp": "Temperatura: {} 🌡\n",
        "max_temp": "Rango máximo: {}\n",
        "min_temp": "Rango mínimo: {}\n",
        "pressure": "Presión atmosférica: {}\n",
        "visibility": "Visibilidad: {}\n",
        "wind_speed": "Velocidad del viento: {}\n",
        "clouds": "Nubes: {}\n",
        "rain": "Lluvia: {}\n",
        "snow": "Nieve: {}\n",
        "humidity": "Humedad: {}\n",
        "weather_status_icon": None,
        "uvi": "UVI: {}\n",
        "precipitation_probability": "Probabilidad de precipitaciones: {}\n",
        "most_cold": "...frío: {} - {} ❄\n",
        "most_hot": "...cálido: {} - {} ☀\n",
        "most_humid": "...húmedo: {} - {} 🌫\n",
        "most_rainy": "...lluvioso: {} - {} 🌧\n",
        "most_snowy": "...nevado: {} - {} 🌨\n",
        "most_windy": "...ventoso: {} - {} 🌬\n"
    }

    for key, value in weather_details.items():
        if value is None:
            continue

        if type_query == "extended_weather" and \
                key in ("latest_weather_update", "sunset_time", "sunrise_time", "max_temp", "min_temp"):
            continue

        if type_query == "detailed_extended_weather" and \
            key == "weather_status":
            continue

        message_template = message_mapping.get(key)
        if message_template:
            if isinstance(value, tuple):
                message_parts.append(message_template.format(*value))
            else:
                message_parts.append(message_template.format(value))
        if not message_template and key == "weather_status_icon":
            message_sticker = value

        if key == 'weather_status':
            weather_status = value

    return "".join(message_parts), message_sticker, weather_status


def chatbot_handler(message: Message) -> None:
    """
    Maneja los mensajes enviados y las respuestas
    de la conversación entre el Chatbot y el Usuario.

    :param message: El mensaje recibido.
    :type message: telebot.types.Message
    """
    user_id = int(message.chat.id)
    user_first_name = message.from_user.first_name
    user_message = message.text

    # print(user_id, user_first_name, user_message)

    if is_not_authenticated(user_id, user_first_name): return
    
    type_query = None

    chatbot_message = None

    response_chatbot = classification_model_cw.process_query(user_message)
    if response_chatbot in ('clima actual', 'clima extendido', 'detalle extendido'):
        type_query = response_chatbot
    else:
        telegram_bot.send_message_bot(user_id, response_chatbot)
        return
    
    location = db.get_location(user_id)

    if not location:
        chatbot_message = f"{user_first_name}, {CHATBOT_NAME} 💬 requiere que primero envies una úbicación. \
                            \nPara esto utiliza el comando /location."
        telegram_bot.send_message_bot(user_id, chatbot_message)
        return

    weather_forecast = WeatherForecast(OWM_API_KEY, location)

    if not weather_forecast:
        chatbot_message = f"Disculpa {user_first_name}, {CHATBOT_NAME} 💬 no puede procesar esa información."

        telegram_bot.send_message_bot(user_id, chatbot_message)
        return

    if type_query == 'clima actual':
        type_query = "current_weather"
        current_weather = weather_forecast.get_current_weather()

        if not current_weather:
            chatbot_message = f"Disculpa {user_first_name}, {CHATBOT_NAME} 💬 no puede procesar esa información."

            telegram_bot.send_message_bot(user_id, chatbot_message)
            return

        weather_details = weather_forecast.get_weather_details(
            current_weather)
        chatbot_message, chatbot_message_sticker, weather_status = build_message(
            weather_details, type_query, location)

        telegram_bot.send_message_bot(user_id, chatbot_message)
        telegram_bot.send_message_bot(user_id, chatbot_message_sticker)

        classification_model_w = ClassificationModel(DATASET)
        classification_model_w.set_prepare_model(["weather_status"])
        recomendation_chatbot = classification_model_w.process_query(weather_status)
        telegram_bot.send_message_bot(user_id, recomendation_chatbot)

    if type_query == 'clima extendido':
        type_query = "extended_weather"
        forecast = weather_forecast.get_forecast()

        if not forecast:
            chatbot_message = f"Disculpa {user_first_name}, {CHATBOT_NAME} 💬 no puede procesar esa información."

            telegram_bot.send_message_bot(user_id, chatbot_message)
            return

        dates = weather_forecast.datetime_manager.generate_next_dates()
        for date in dates:
            weather = weather_forecast.get_weather_at_date(forecast, date)
            weather_details = weather_forecast.get_weather_details(weather)
            chatbot_message, chatbot_message_sticker, _ = build_message(
                weather_details, type_query, location)

            telegram_bot.send_message_bot(user_id, chatbot_message)
            telegram_bot.send_message_bot(user_id, chatbot_message_sticker)

    if type_query == 'detalle extendido':
        type_query = "detailed_extended_weather"
        extend_forecast = weather_forecast.get_extended_forecast()
        if not extend_forecast:
            chatbot_message = f"Disculpa {user_first_name}, {CHATBOT_NAME} 💬 no puede procesar esa información."

            telegram_bot.send_message_bot(user_id, chatbot_message)
            return

        chatbot_message, _, _ = build_message(
            extend_forecast, type_query, location)

        telegram_bot.send_message_bot(user_id, chatbot_message)

    if not chatbot_message:
        chatbot_message = f"Disculpa {user_first_name}, {CHATBOT_NAME} 💬 no comprende tu consulta. \
                            \n¿Podrías explicarte mejor? 😀"

        telegram_bot.send_message_bot(user_id, chatbot_message)


def validate_location(text: str) -> bool:
    """
    Valida el formato de la úbicación.

    :param text: Texto de úbiación.
    :param type: str
    :return: True or False.
    :rtype: bool
    """
    regex = r'^\s*[\w\s]+,\s*[\w\s]+,\s*[\w\s]+\s*$'
    return bool(re.match(regex, text, re.IGNORECASE))

def location_handler(message: Message) -> None:
    """
    Maneja los mensajes sobre la ubicación del usuario.

    :param message: El mensaje recibido.
    :type message: telebot.types.Message
    """
    user_id = int(message.chat.id)
    user_first_name = message.from_user.first_name
    user_message = message.text.removeprefix('/location').strip()

    if user_message.lower() == "cancelar":
        telegram_bot.send_message_bot(user_id, "Se canceló la operación. 😊")
        return

    if is_not_authenticated(user_id, user_first_name): return

    locations = db.get_locations(user_id)
    len_loc = len(locations)
    response = ""

    # Si el mensaje es un numero correspondiente a las ubicaciones
    if len_loc and bool(re.match(rf'^[1-{len_loc}]$', user_message)):
        loc_id = int(user_message) - 1
        location = locations.pop(loc_id)
        locations.insert(0, location)
        db.set_locations(user_id, locations)
        return telegram_bot.send_message_bot(user_id, "Ubicación cambiada a:\n" + location)
    
    if validate_location(user_message):
        if len_loc == 5: locations.pop()
        locations.insert(0, user_message)
        db.set_locations(user_id, locations)
        return telegram_bot.send_message_bot(user_id, "Nueva ubicación:\n" + user_message +
                                            "\n\n Utiliza frases como 'clima actual', 'pronostico extendido' o 'detalle extendido' para obtener la información de tu nueva ubicación. 📍")
    
    if len(user_message)>0:
        response += f"No se encontro la ubicación\n'{user_message}'\n\n"

    response += "Para cargar una nueva ubicación ingrese: \
                            \n• Ciudad, Provincia/Estado, País. \
                            \n\n📍 Ejemplo de ubicación: \
                            \nSan Miguel, Buenos Aires, Argentina"
    if len_loc:
        response += "\n\nTambien puedes usar una de tus ultimas ubicaciones escribiendo el numero correspondiente:\n"
        response += "\n".join([f"{i+1}. {location}" for i, location in enumerate(locations)])
    response += "\n\nSi no quieres agregar/cambiar la ubicacion, escribe: cancelar"
    telegram_bot.send_message_bot(user_id, response)
    telegram_bot.bot.register_next_step_handler(message, location_handler)
    
def registeration_handler(message: Message) -> None:
    """
    Maneja los mensajes sobre el registro del usuario.

    :param message: El mensaje recibido.
    :type message: telebot.types.Message
    """
    user_id = int(message.chat.id)
    user_first_name = message.from_user.first_name
    if is_not_authenticated(user_id, user_first_name):
        telegram_bot.send_message_bot(user_id, "Primero debes autenticarte desde un dispositivo registrado.\
                                      \nSi no tienes un dispositivo registrado ignora este mensaje.\
                                      \nLuego de autentificarte podras registrar otro dispositivo.")
        return
    link = authenticator.gen_temp_link(user_id, user_first_name, 'register')
    chatbot_message = f"{user_first_name}, presiona el boton de abajo desde el dispositivo que quieras registrar\.\n"
    send_auth_link(user_id, chatbot_message, 'Autenticar', link)

def is_not_authenticated(user_id: int, user_first_name: str) -> bool:
    if authenticator.is_authenticated(user_id):
        return False
    link = authenticator.gen_temp_link(user_id, user_first_name)
    chatbot_message = f"{user_first_name}, tus datos son sensibles\. Primero autentificate con el boton de abajo\.\n"
    send_auth_link(user_id, chatbot_message, 'Autenticar', link)
    return True

def send_auth_link(user_id: int, chatbot_message: str, button_text: str, link: str) -> None:
    print(chatbot_message)
    keyboard = InlineKeyboardMarkup()
    button = InlineKeyboardButton(text=button_text, url=link)
    keyboard.add(button)
    telegram_bot.send_message_bot(user_id, chatbot_message, "MarkdownV2", keyboard)

if __name__ == "__main__":
    """
    Este script sirve como punto de entrada principal para el Chatbot de WeatherWiz.
    Configura el bot de Telegram y maneja los mensajes enviados por los usuarios.

    Antes de ejecutar este script, asegúrate de haber configurado las variables de entorno
    TB_API_KEY y OWN_API_KEY en tu archivo .env con las claves de la API de Telegram y OpenWeatherMap, respectivamente.

    El bot responde a diferentes comandos de usuario para proporcionar información meteorológica, incluyendo
    el clima actual, el pronóstico extendido y detalles adicionales del clima.

    Ejemplo de uso:
        python main.py
    """
    CHATBOT_NAME = "WeatherWiz"

    print(f"\n\tInicia servicio {CHATBOT_NAME}. ")

    COMMAND_START = f"{CHATBOT_NAME} 💬"
    COMMAND_HELP = f"\n• Clima actual. \
                        \n• Pronostico extendido. \
                        \n• Detalle extendido."
    COMMAND_DSCRIPTION = f"{CHATBOT_NAME} 💬 brinda información meteorológica."

    DATASET = 'processing/dataset.yml'

    classification_model_cw = ClassificationModel(DATASET)
    classification_model_cw.set_prepare_model(["conversation", "weather"])

    telegram_bot = TelegramBot(TB_API_KEY, COMMAND_START, COMMAND_HELP,
                               COMMAND_DSCRIPTION, location_handler,
                               chatbot_handler, registeration_handler)

    telegram_thread = run_telegram_thread()
    telegram_thread_id = telegram_thread.native_id
    print(f"\n\t\tEjecución Telegram Thread ID: {telegram_thread_id}")

    db = start_mongo()
    print("\n\t\tStarted mongoDB")


    authenticator = AuthService(db)
    auth_thread = run_auth_thread()
    auth_thread_id = auth_thread.native_id
    print(f"\n\t\tEjecución Auth Thread ID: {auth_thread_id}")

    while not THREADS: pass

    print(f"\n\t\t\tFinalizando Telegram Thread ID: {telegram_thread_id}, aguarde unos segundos...")

    telegram_bot.stop_bot()
    telegram_thread.join()

    print(f"\n\t\tEjecución de Telegram Thread ID: {telegram_thread_id} finalizada.")

    print(f"\n\tFinaliza servicio {CHATBOT_NAME}.\n")

    authenticator.stop()
    auth_thread.join()

    print(f"\n\tEjecución de Auth Thread ID: {auth_thread_id} finalizada.")