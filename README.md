
# Marvin - Chatbot con Integraciones de AI

## Descripción

Marvin es un chatbot construido con **Flask** que integra múltiples modelos de inteligencia artificial para proporcionar respuestas personalizadas a los usuarios. Utiliza **Google Gemini** y **ChatGPT** para el análisis de intenciones y generación de respuestas. Marvin es ideal para interactuar con usuarios a través de plataformas como **Telegram**, donde puede interpretar mensajes, generar respuestas y manejar múltiples tipos de payloads.

## Características Principales

- **Análisis de Intenciones**: Usa modelos AI para detectar la intención de los mensajes, como saludos, despedidas y pedidos de ayuda.
- **Generación de Respuestas**: Responde a los usuarios con mensajes generados por AI, incluyendo personalizaciones como respuestas en tono sarcástico estilo Marvin el robot de "La guía del viajero intergaláctico".
- **Manejo de Mensajes en Telegram**: Soporte para múltiples tipos de mensajes, incluidos texto, fotos, voz, stickers y documentos.
- **Resiliencia con Reintentos**: Implementación de reintentos automáticos para manejar errores de las API de AI (Gemini, ChatGPT) y evitar fallos por limitaciones de tasa.

## Requisitos

### Dependencias

- Python 3.12+
- Flask
- openai
- google-generativeai
- requests
- Otros módulos indicados en `requirements.txt`

Instala las dependencias con:

```bash
pip install -r requirements.txt
```

### Configuración

1. Clonar el repositorio:

```bash
git clone https://github.com/tuusuario/marvin.git
cd marvin
```

1. Ajustar la configuracion en los archivos que se encuentran en la carpeta `config` dentro del raíz del proyecto y configurar las claves de API necesarias:

```bash
GEMINI_API_KEY=your_gemini_api_key
CHATGPT_API_KEY=your_chatgpt_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

3. Configurar el archivo `configXXX.py` para manejar otros ajustes relevantes de la aplicación.

## Estructura del Proyecto

```bash
marvin/
├── src/
│   ├── controllers/
│   │   ├── telegramController.py
│   │   ├── chatGPTController.py
│   │   ├── geminiController.py
│   │   └── __init__.py
│   ├── models/
│   │   ├── intentsModel.py
│   │   └── __init__.py
│   ├── services/
│   │   ├── MarvinService.py
│   │   └── __init__.py
│   ├── utils/
│   │   └── command.py
│   └── __init__.py
├── instance/
│   └── marvin_development.db
├── resources/
│   └── ngrok.exe
├── config/
│   ├── configDEV.py
│   └── configPROD.py
├── main.py
├── ngrok_manager.py
├── requirements.txt
└── README.md
```

- `src/controllers/`: Controladores para gestionar las interacciones con los diferentes servicios de AI y la plataforma Telegram.
- `src/services/`: Servicios adicionales que complementan las operaciones del bot.
- `src/utils/`: Utilidades para procesamiento de mensajes y otras tareas comunes.

## Uso

### Ejecución en Local

1. Asegúrate de que todas las dependencias estén instaladas y el archivo `.configDEV` esté configurado correctamente.
2. Ejecuta la aplicación:

```bash
python main.py
```

3. En caso de necesitar correr el productivo el comando seria el siguiente:

```bash
python main.py prod
```
### Uso en Telegram

Para crear el bot en telegram utiliza BotFather, una vez que el bot esté ejecutándose, conéctalo a Telegram utilizando el **Telegram Bot Token** que configuraste. Envía mensajes al bot y este responderá utilizando sus capacidades de AI.

## Desarrollo

### Estilo de Código

Este proyecto sigue el estándar **PEP 8** para Python. Es recomendable utilizar un linter como **Flake8** para asegurarse de que el código cumpla con este estilo.

## Contribuciones

Las contribuciones son bienvenidas. Para contribuir:

1. Haz un fork del repositorio.
2. Crea una rama con tu nueva característica (`git checkout -b feature/nueva-caracteristica`).
3. Realiza el commit de tus cambios (`git commit -am 'Agrega nueva característica'`).
4. Haz push a la rama (`git push origin feature/nueva-caracteristica`).
5. Abre un **Pull Request**.

## Licencia

Este proyecto está licenciado bajo la licencia MIT. Consulta el archivo [LICENSE](LICENSE) para obtener más detalles.
