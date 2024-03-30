from time import sleep
from functools import wraps
from typing import Callable


class DecoratorManager:
    """
    Clase que contiene la lógica de los diferentes métodos
    que funcionaran como @decoradores en los distintos modulos del proyecto.

    Estos decoradores pueden utilizarse para modificar el comportamiento de las funciones, 
    como agregar registro de tiempo de ejecución, manejar errores de manera específica, 
    o realizar tareas pre o post ejecución.
    """

    def retry_on_error(exceptions: tuple, max_retries: int = 3, delay: int = 5) -> Callable:
        """
        Decorador para manejar errores y reintentos.

        Reintenta la función decorada en caso de un error de lectura de tiempo,
        hasta un número máximo de intentos, con un retraso entre intentos.

        :param max_retries: Número máximo de intentos antes de fallar.
        :type max_retries: int
        :param delay: Tiempo de espera entre reintentos en segundos.
        :type delay: int
        :return: Función decorada.
        :rtype: callable
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                error = None
                attempts = 0
                while attempts < max_retries:
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        error = e
                        print(f"Error: {e}. Retrying in {delay} seconds...")
                        sleep(delay)
                        attempts += 1
                print(error)
                return None
            return wrapper
        return decorator