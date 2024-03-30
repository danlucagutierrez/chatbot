import re
import yaml
import random
import unicodedata

"""
Modelo Clasificación supervisada - Machine Learning.

Un modelo de aprendizaje automático (ML) que es de clasificación supervisada es un tipo de modelo diseñado 
para predecir la clase o categoría a la que pertenece una observación, basándose en características o atributos
conocidos como variables predictoras. La supervisión se refiere a que durante el entrenamiento del modelo, 
se proporciona un conjunto de datos etiquetados, es decir, datos para los cuales ya se conoce la clase a la
que pertenecen.

El proceso de entrenamiento de un modelo de clasificación supervisada implica ajustar los parámetros del modelo 
para minimizar la discrepancia entre las predicciones del modelo y las etiquetas reales proporcionadas en los 
datos de entrenamiento. Una vez entrenado, el modelo puede usarse para hacer predicciones sobre nuevas 
observaciones cuyas clases son desconocidas.

Ejemplos comunes de algoritmos de clasificación supervisada incluyen:

- Regresión logística
- Árboles de decisión
- Máquinas de vectores de soporte (SVM)
- Vecinos más cercanos (K-Nearest Neighbors)
- Redes neuronales artificiales

Estos modelos se utilizan en una amplia gama de aplicaciones, desde la clasificación de correos electrónicos como 
spam o no spam hasta la detección de fraudes en transacciones financieras, diagnóstico médico y mucho más. 
La supervisión en este contexto se refiere a la necesidad de tener etiquetas de clase conocidas durante el proceso
de entrenamiento del modelo.
"""

from sklearn.feature_extraction.text import CountVectorizer
# CountVectorizer es una clase en scikit-learn que se utiliza para convertir una
# colección de documentos de texto en una matriz de recuento de términos o tokens.
# Básicamente, convierte el texto en una representación numérica que los algoritmos de
# aprendizaje automático pueden entender.

from sklearn.naive_bayes import MultinomialNB
# MultinomialNB es una implementación del algoritmo de Naive Bayes multinomial.
# Es particularmente útil cuando se trabaja con datos categóricos, como el conteo
# de palabras en documentos de texto. En el contexto de la clasificación de texto,
# se puede utilizar para clasificar textos en categorías basadas en la frecuencia de las palabras.

from sklearn.pipeline import Pipeline
# Pipeline es una herramienta en scikit-learn que se utiliza para encadenar varios pasos de procesamiento
# de datos juntos. Esto es útil para crear un flujo de trabajo completo donde los datos pueden pasar a través
# de múltiples transformaciones antes de ser ingresados a un modelo de aprendizaje automático.


class ClassificationModel:
    """
    Clase que implementa un modelo de clasificación de texto.

    :param dataset_path: Ruta al archivo YAML que contiene los datos de entrenamiento.
    :type dataset_path: str
    """

    def __init__(self, dataset_path: str):
        """
        Inicializa el modelo cargando los datos y entrenando el clasificador.

        :param dataset_path: Ruta al archivo YAML que contiene los datos de entrenamiento.
        :type dataset_path: str
        """
        self.dataset_path = dataset_path
        self.threshold_probability = 0.5 # Mejorar el umbral de probabilidad.
        self.pipeline = None

    def set_prepare_model(self, sections: list):
        """
        Carga el modelo con los datos de la sección especificada.

        :param sections: Sección o secciones del dataset.yml.
        :type sections: list
        """
        with open(self.dataset_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)

        sections_default = ["conversation", "weather", "weather_status"]

        for section in sections:
            if section not in sections_default:
                raise ValueError(f"Not found section: {section}.")

        self.total_data_input = dict()
        self.total_data_output = dict()

        for section in sections:
            if section == "conversation":
                data_input = "user_conversation"
                data_output = "chatbot_conversation"
            elif section == "weather":
                data_input = "weather_user_inquiries"
                data_output = "weather_chatbot_answers"
            elif section == "weather_status":
                data_input = "weather_status"
                data_output = "chatbot_recomendations"

            self.total_data_input.update(data[section][data_input])
            self.total_data_output.update(data[section][data_output])

        self.pipeline = None

        self._prepare_model()

    def _prepare_model(self) -> None:
        """
        Prepara y entrena el modelo de clasificación de texto.
        """
        if not self.total_data_input:
            raise Exception("Not data input.")

        queries = list()
        labels = list()

        for category, q in self.total_data_input.items():
            for query in q:
                query = ClassificationModel.preprocess_text(query)
                queries.append(query)
                labels.append(category)

        pipeline = Pipeline([
            ('vectorizer', CountVectorizer()),
            ('classifier', MultinomialNB())
        ])
        pipeline.fit(queries, labels)

        self.pipeline = pipeline

    def process_query(self, query: str) -> str:
        """
        Procesa la consulta del usuario y devuelve una respuesta adecuada.

        :param query: La consulta del usuario.
        :type query: str
        :return: La respuesta del modelo.
        :rtype: str
        """
        query = ClassificationModel.preprocess_text(query)
        predictions = self.pipeline.predict([query])
        predicted_probabilities = self.pipeline.predict_proba(
            [query]).flatten().tolist()

        if all(pp < self.threshold_probability for pp in predicted_probabilities):
            return "Lo siento, no entendí bien tu consulta."

        label = predictions[0]
        if label in self.total_data_output:
            response = self.total_data_output[label]
        return random.choice(response)

    @staticmethod
    def preprocess_text(text: str) -> str:
        """
        Realiza el preprocesamiento de texto en una cadena dada.

        Esto implica convertir el texto a minúsculas, remover acentos,
        y remover puntuación y otros caracteres especiales.

        :param text: El texto a ser preprocesado.
        :type text: str
        :return: El texto preprocesado.
        :rtype: str
        """
        # Convertir el texto a minúsculas.
        text = text.lower()
        # Quitar acentos.
        text = ''.join(c for c in unicodedata.normalize(
            'NFD', text) if unicodedata.category(c) != 'Mn')
        # Sacar puntuación y otros caracteres especiales.
        text = re.sub(r'[^\w\s]', '', text)
        return text