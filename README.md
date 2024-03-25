<!-- README --->

<div align="center">
    <img src="./resources/weatherwiz_logo.jpg" height="250">
</div>
<div align="center">
   <a href="https://github.com/danlucagutierrez/*Chatbot*">
      <img src="https://img.shields.io/badge/WeatherWiz-blue" height="20">
   </a>
</div>
<div align="center">
   <a>
      <img src="https://img.shields.io/badge/Estado-En%20Desarrollo-green" height="20">
   </a>
</div>
<hr>

# WeatherWiz 💬

## Descripción

### **WeatherWiz** - *Chatbot* para Consultas Meteorológicas en Telegram

**WeatherWiz** es un ingenioso *Chatbot* diseñado específicamente para brindar información meteorológica precisa y oportuna a través de la popular plataforma de mensajería, Telegram. Al aprovechar la inteligencia artificial (IA) y el aprendizaje automático (ML), **WeatherWiz** no solo responde a consultas sobre el clima actual, sino que también ofrece recomendaciones pertinentes basadas en datos en tiempo real.


## Objetivo

El propósito fundamental de **WeatherWiz** es proporcionar a los usuarios una herramienta de consulta simplificada y eficaz para acceder a información meteorológica precisa en cualquier momento. Además, se enfoca en garantizar una experiencia de usuario fluida y segura, haciendo hincapié en la protección de los datos personales a través de una autenticación segura por huella digital. 

El *Chatbot* se convierte en un recurso valioso para quienes desean planificar sus actividades diarias según las condiciones climáticas y para aquellos que buscan prepararse adecuadamente ante eventos meteorológicos adversos.

## Uso

Para comenzar a utilizar **WeatherWiz**, simplemente inicie una conversación con el *Chatbot* en Telegram, recuerde que si es la primer vez debera ingresar sus datos personales junto a su huella digital para un registro seguro. Una vez realizado esto, envíe su consulta sobre el clima. 

Puede proporcionar la ubicación especifica para recibir información precisa sobre el clima en esa área, recuerde que si no especfica una ubicación el *Chatbot* respondera basandose en su información de registro.

## Equipo de desarrollo

- Dan Luca Gutierrez
- Fernando Mossier
- Tobias Rumiz

## Herramientas

- Python 🐍
- Jupyter Notebook 📕 

   Si utiliza VS Code se recomienda instalar la extensión Jupyter:
   [VS Marketplace Link](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter)

<!-- Agregar otras herramientas aquí. -->

## Librerias

- python-dotenv==1.0.1
- scikit-learn==1.4.1.post1
- pyowm==3.3.0
- pyTelegramBotAPI==4.16.1

<!-- Agregar otras librerias aquí. -->

## Instrucciones de instalación

1. Clonar el repositorio via HTTP:
   ```bash
   git clone https://github.com/danlucagutierrez/*Chatbot*
   ```

2. Instalar Python:

    Linux:
    ```bash
    sudo apt update && sudo apt upgrade
    sudo apt install python3
    python3 --version
    ```

    Windows:
    ```bash
    https://www.python.org/downloads/
    python --version
    ```

2. Generar un envirorment (env) dentro del repositorio:
    ```bash
    python -m venv env
    ```

3. Posteriormente activar el envirorment (env):

    Linux:
    ```bash
    source env/bin/activate
    ```
    Windows:
    ```bash
    .\env\Scripts\Activate.ps1
    ```

4. Instalar las librerias:
   ```bash
   pip install -r requirements.txt
    ```

<!-- Agregar otros pasos aquí. -->

## Licencia

Software libre.