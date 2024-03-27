import os
from typing import Callable
from requests.exceptions import ReadTimeout

# pyTelegramBotAPI library.
import telebot
from telebot.apihelper import ApiTelegramException

try:
    import utils
except (ImportError, ModuleNotFoundError):
    import sys
    path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    sys.path.insert(1, path)

from utils.decorators import retry_on_error


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

    def __init__(self, api_key: str, start_response: str = None, help_response: str = None, description_response: str = None, message_handler: Callable = None) -> None:
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
        self._api_key = api_key
        self.bot = telebot.TeleBot(self._api_key)

        # Importante: Registra los manejadores de mensajes.
        self.register_handlers(start_response, help_response,
                               description_response, message_handler)

    def register_handlers(self, start_response: str = None, help_response: str = None, description_response: str = None, message_handler: Callable = None) -> None:
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
                lambda message: self.reply_to_bot(message, f'¡Hola soy {start_response}!'))
        if help_response:
            self.bot.message_handler(commands=['help'])(
                lambda message: self.reply_to_bot(message, f'{start_response} esta aquí para ayudarte, puedes consultar por: {help_response}'))
        if description_response:
            self.bot.message_handler(commands=['description'])(
                lambda message: self.reply_to_bot(message, description_response))
        if message_handler:
            self.bot.message_handler(content_types=['text'])(message_handler)

    @retry_on_error(exceptions=(ApiTelegramException, ReadTimeout))
    def reply_to_bot(self, message: str, text: str) -> None:
        """
        Responde a un mensaje especifico.

        :param message: El mensaje.
        :type message: str
        :param text: El texto de respuesta.
        :type text: str
        """
        self.bot.reply_to(message=message, text=text, timeout=5)

    @retry_on_error(exceptions=(ApiTelegramException, ReadTimeout))
    def send_message_bot(self, chat_id: int, text: str) -> None:
        """
        Envia un mensaje.

        :param chat_id: El identificador del chat.
        :type chat_id: int
        :param text: El texto de respuesta.
        :type text: str
        """
        self.bot.send_message(chat_id=chat_id, text=text, timeout=5)

    def start_bot(self) -> None:
        """
        Inicia la ejecución del Chatbot de Telegram y comienza a escuchar los mensajes entrantes.
        """
        self.bot.infinity_polling()

    def stop_bot(self) -> None:
        """
        Frena la ejecución del Chatbot de Telegram y comienza a escuchar los mensajes entrantes.
        """
        self.bot.stop_bot()