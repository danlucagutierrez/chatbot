from time import sleep
from functools import wraps
from requests.exceptions import ReadTimeout

# pyTelegramBotAPI library.
import telebot
from telebot.apihelper import ApiTelegramException


def retry_on_error(max_retries=3, delay=5):
    """
    Decorador para manejar errores de la libreria pyTelegramBotAPI.

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
                except (ConnectionError, ReadTimeout, ApiTelegramException) as e:
                    error = e
                    print(f"Error: {e}. Retrying in {delay} seconds...")
                    sleep(delay)
                    attempts += 1
            raise RuntimeError(
                f"Failed after {max_retries} retries. Type error: {type(error)}.")
        return wrapper
    return decorator


class TelegramBot:
    """
    Clase para manejar la funcionalidad del Chatbot de Telegram.

    Permite interactuar con los usuarios que utilicen el Chatbot.

    Para utilizar esta clase, es necesario instalar la libreria pyTelegramBotAPI. 
    Puede encontrar más información y documentación
    sobre pyTelegramBotAPI en los siguientes enlaces:
    - PyPI: https://pypi.org/project/pyTelegramBotAPI/
    - Documentación: https://pytba.readthedocs.io/en/latest/index.html

    Es necesario previamente haber creado un Chatbot mediante la aplicación Telegram
    ingresando al administrador de Chatbots @BotFather.
    Este proporcionara una clave API (API key) gratuita.
    Documentación:
        - https://core.telegram.org/bots
        - https://core.telegram.org/api

    Atributos:
        api_key (str): Clave de API (API key) proporcionada por Telegram para acceder a la API.
        start_response (str): Respuesta al comando /start.
        help_response (str): Respuesta al comando /help.
        description_response (str): Respeusta al comando /description.
        message_handler (str): Respuesta a consultas de texto (sin comando).
    """

    def __init__(self, api_key: str, start_response: str = None, help_response: str = None, description_response: str = None, message_handler: str = None) -> None:
        """
        Inicializa el bot de Telegram con la clave de API proporcionada.

        :param api_key: La clave de API del bot de Telegram.
        :type api_key: str
        :param start_response: La respuesta para el comando /start.
        :type start_response: str
        :param help_response: La respuesta para el comando /help.
        :type help_response: str
        :param description_response: La respuesta para el comando /description.
        :type description_response: str
        :param message_handler: La función para manejar mensajes de texto.
        :type message_handler: callable
        """
        self.bot = telebot.TeleBot(api_key)

        # Importante: Registra los manejadores de mensajes.
        self.register_handlers(start_response, help_response,
                               description_response, message_handler)

    def register_handlers(self, start_response: str = None, help_response: str = None, description_response: str = None, message_handler: str = None) -> None:
        """
        Registra los manejadores de mensajes para los comandos del Chatbot.

        :param start_response: La respuesta para el comando /start.
        :type start_response: str
        :param help_response: La respuesta para el comando /help.
        :type help_response: str
        :param description_response: La respuesta para el comando /description.
        :type description_response: str
        :param message_handler: La función para manejar mensajes de texto.
        :type message_handler: callable
        """
        if start_response:
            self.bot.message_handler(commands=['start'])(
                lambda message: self.bot.reply_to(message, f'¡Hola soy {start_response}!'))
        if help_response:
            self.bot.message_handler(commands=['help'])(
                lambda message: self.bot.reply_to(message, f'¿Necesitas ayuda? Puedes consultar por: {help_response}'))
        if description_response:
            self.bot.message_handler(commands=['description'])(
                lambda message: self.bot.reply_to(message, description_response))
        if message_handler:
            self.bot.message_handler(content_types=['text'])(message_handler)

    def start_bot(self) -> None:
        """
        Inicia el Chatbot de Telegram y comienza a escuchar los mensajes entrantes.
        """
        self.bot.infinity_polling()