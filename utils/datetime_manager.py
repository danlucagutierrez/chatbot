import locale
from datetime import datetime, timedelta, timezone

# Establecer el localismo para el formato de fecha y hora en español.
locale.setlocale(locale.LC_TIME, 'spanish')


class DatetimeManager:
    """
    Clase para manejar fechas y horas, con la libreria datetime.
    """

    def __init__(self):
        """
        Inicializa un objeto DatetimeManager con la zona horaria UTC y el desfase horario para Argentina (GMT-3).
        """
        self.utc_timezone = timezone.utc
        self.arg_timezone = timezone(timedelta(hours=-3))
        self.format_time = "%H:%Mhs"

    def generate_utc_now(self) -> datetime:
        """
        Genera el datetime actual en UTC.
        """
        return datetime.now(self.utc_timezone)

    def convert_utc_to_arg(self, date: datetime or int) -> datetime:
        """
        Convierte un datetime o segundos (int) UTC a la zona horaria de Argentina (GMT-3).

        :param date: El datetime o segundos (int) en la zona horaria UTC.
        :type date: datetime or int
        :return: El datetime convertido a la zona horaria de Argentina.
        :rtype: datetime
        """
        if isinstance(date, int):
            return datetime.fromtimestamp(date, tz=self.utc_timezone).astimezone(self.arg_timezone).strftime(self.format_time)
        return date.astimezone(self.arg_timezone)

    def generate_next_dates(self, number_of_dates: int = 5) -> list:
        """
        Genera una lista de fechas futuras a partir de la fecha actual en la zona horaria de Argentina (GMT-3).

        :param number_of_dates: Número de fechas futuras a generar.
        :type number_of_dates: int (por defecto es 5).
        :return: Lista de fechas futuras en formato 'YYYY-MM-DD'.
        :rtype: list
        """
        arg_now = self.convert_utc_to_arg(self.generate_utc_now())
        next_dates = [arg_now + timedelta(days=i)
                      for i in range(1, number_of_dates + 1)]
        return [date.strftime("%Y-%m-%d") for date in next_dates]

    def build_day_and_time(self, seconds: int) -> tuple:
        """
        Obtiene el día de la semana y la hora en formato 'hh:mmhs' para un timestamp dado en la zona horaria de Argentina (GMT-3).

        :param seconds: El timestamp en segundos.
        :type seconds: int

        :return: El día de la semana y la hora en Argentina.
        :rtype: tuple
        """
        arg_time = self.convert_utc_to_arg(
            datetime.fromtimestamp(seconds, tz=self.utc_timezone))
        return arg_time.strftime("%A").capitalize(), arg_time.strftime(self.format_time)