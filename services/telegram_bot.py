import os
from typing import Callable
from requests.exceptions import ReadTimeout

# pyTelegramBotAPI library.
import telebot
from telebot.types import Message, InlineKeyboardMarkup
from telebot.apihelper import ApiTelegramException

try:
    import utils
except (ImportError, ModuleNotFoundError):
    import sys
    path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    sys.path.insert(1, path)

from utils.decorator_manager import DecoratorManager


class TelegramBot:
    """
    Clase para manejar la funcionalidad del Chatbot de Telegram.

    Permite interactuar con los usuarios que utilicen el Chatbot.

    pyTelegramBotAPI es una libreria Python que proporciona una interfaz fácil de 
    usar para acceder a la API de Telegram.

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

    Para evitar alcanzar los límites de la API al enviar mensajes con tu bot, sigue estas recomendaciones:
        - Enviar mensajes en un chat específico: Evita enviar más de un mensaje por segundo en un chat particular. 
        Aunque se pueden permitir ráfagas breves que superen este límite, es importante evitar alcanzar el límite 
        de errores 429.

        - Notificaciones masivas a múltiples usuarios: La API no permitirá más de aproximadamente 30 mensajes 
        por segundo al enviar notificaciones masivas a varios usuarios. Para evitar errores 429, distribuye 
        las notificaciones en intervalos amplios de 8 a 12 horas.

        - Límite de mensajes por minuto en un grupo: Ten en cuenta que tu bot no podrá enviar más de 20 mensajes 
        por minuto al mismo grupo. Es importante mantener este límite para evitar problemas con la API.

    Atributos:
        api_key (str): Clave de API (API key) proporcionada por Telegram para acceder a la API.
        start_response (str): Respuesta al comando /start.
        help_response (str): Respuesta al comando /help.
        description_response (str): Respeusta al comando /description.
        message_handler (str): Respuesta a consultas de texto (sin comando).
    """

    def __init__(self, api_key: str, command_start: str, command_help: str, command_description: str, location_handler: Callable, chatbot_handler: Callable, registration_handler: Callable) -> None:
        """
        Inicializa el bot de Telegram con la clave de API proporcionada.

        :param api_key: La clave de API del bot de Telegram.
        :type api_key: str
        :param command_start: La respuesta para el comando /start.
        :type command_start: str
        :param command_help: La respuesta para el comando /help.
        :type command_help: str
        :param command_description: La respuesta para el comando /description.
        :type command_description: str
        :param location_handler: La función para manejar el comando /location.
        :type location_handler: callable
        :param chatbot_handler: La función para manejar mensajes de texto.
        :type chatbot_handler: callable
        :param location_handler: La función para manejar el comando /register.
        :type location_handler: callable
        """
        self._api_key = api_key
        self.bot = telebot.TeleBot(self._api_key)

        self.command_start = command_start
        self.command_help = command_help
        self.command_description = command_description
        self.location_handler = location_handler
        self.chatbot_handler = chatbot_handler
        self.registration_handler = registration_handler

        self.text_response_user = None

        self.register_handlers()

    @DecoratorManager.retry_on_error(exceptions=(ApiTelegramException, ReadTimeout))
    def register_handlers(self) -> None:
        """
        Registra los manejadores de mensajes para los comandos del Chatbot.
        """
        self.bot.message_handler(commands=["start"])(
            lambda message: self.reply_to_bot(message, f"¡Hola soy {self.command_start}!"))
        self.bot.message_handler(commands=["help"])(
            lambda message: self.reply_to_bot(message, f"{self.command_start} esta aquí para ayudarte, puedes consultar por: {self.command_help}"))
        self.bot.message_handler(commands=["description"])(
            lambda message: self.reply_to_bot(message, self.command_description))
        self.bot.message_handler(commands=["location"])(self.location_handler)
        self.bot.message_handler(commands=["register"])(self.registration_handler)

        self.bot.message_handler(content_types=["text"])(self.chatbot_handler)

    @DecoratorManager.retry_on_error(exceptions=(ApiTelegramException, ReadTimeout))
    def handle_text_response_user(self, message: Message) -> None:
        """
        Maneja la respuesta de texto del Usuario después de un comando.

        :param message: El mensaje recibido.
        :type message: Message
        :param text: Texto del mensaje.
        :rtype text: str
        """
        self.text_response_user = message.text
        self.bot.reply_to(message, f"Ingresó {self.text_response_user}. \nAhora puede realizar su consulta. 😉")

    def get_text_response_user(self) -> str or None:
        """
        Retorna el mensaje de respuesta a un comando almacenado.

        :param text_response_user: Texto ingresado por el usuario despues de un comando.
        :rtype text_response_user: str or None
        """
        return self.text_response_user

    @DecoratorManager.retry_on_error(exceptions=(ApiTelegramException, ReadTimeout))
    def reply_to_bot(self, message: Message, text: str) -> None:
        """
        Responde a un mensaje especifico.

        :param message: El mensaje.
        :type message: Message
        :param text: El texto de respuesta.
        :type text: str
        """
        self.bot.reply_to(message, text, timeout=5)

    @DecoratorManager.retry_on_error(exceptions=(ApiTelegramException, ReadTimeout))
    def send_message_bot(self, chat_id: int, text: str, parse_mode: str = None, reply_markup: InlineKeyboardMarkup = None) -> None:
        """
        Envia un mensaje.

        :param chat_id: El identificador del chat.
        :type chat_id: int
        :param text: El texto de respuesta.
        :type text: str
        """
        self.bot.send_message(chat_id, text, parse_mode, reply_markup=reply_markup, timeout=5)

    def start_bot(self) -> None:
        """
        Inicia la ejecución del Chatbot de Telegram y comienza a escuchar los mensajes entrantes.
        """
        self.bot.infinity_polling()

    def stop_bot(self) -> None:
        """
        Frena la ejecución del Chatbot de Telegram.
        """
        self.bot.stop_bot()