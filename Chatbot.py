import json                        # Libreria para trabajar con datos en formato JSON
import requests                    # Libreria para hacer peticiones HTTP (llamar a la API de Groq)
import serial                      # Libreria "pyserial" para comunicarse con la ESP32
import speech_recognition as sr    # Libreria para reconocimiento de voz

# Aquí voy a usar mi APIKEY
API_KEY = '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'
API_URL = 'https://api.groq.com/openai/v1/chat/completions'

# Configuración del puerto serie hacia la ESP32
# En Windows suele ser algo como 'COM3', en Linux/Mac '/dev/ttyUSB0'
PUERTO_ESP32 = 'COM3'
BAUDIOS = 115200

esp32 = None
try:
    esp32 = serial.Serial(PUERTO_ESP32, BAUDIOS, timeout=2)
    print(f"Conectado a la ESP32 en {PUERTO_ESP32}")
except Exception as e:
    print(f"No se pudo conectar a la ESP32: {e}")
    print("El chatbot seguira funcionando, pero no podra controlar los LEDs.")


def escuchar_voz():   # Funcion: captura audio del microfono y lo convierte a texto
    """Captura audio del micrófono y lo convierte a texto usando reconocimiento de voz de Google."""
    reconocedor = sr.Recognizer()
    with sr.Microphone() as fuente:
        print("Escuchando... hable ahora.")
        reconocedor.adjust_for_ambient_noise(fuente)
        audio = reconocedor.listen(fuente)
    try:
        texto = reconocedor.recognize_google(audio, language='es-ES')
        print(f"Tú (voz): {texto}")
        return texto
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        print(f"Error del servicio de reconocimiento de voz: {e}")
        return None


def enviar_mensaje(mensaje, modelo='openai/gpt-oss-120b'):   # Funcion: envia el mensaje del usuario a la IA de Groq y devuelve su respuesta
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    # Instrucción de sistema: el modelo solo puede encender/apagar los LEDs
    # y debe responder en un JSON estricto para que el codigo lo pueda usar.
    system_prompt = (
        'Eres un chatbot domestico que solo puede encender o apagar dos LEDs: '
        'uno azul y uno naranja. El usuario puede pedir una accion para cada '
        'LED en el mismo mensaje (por ejemplo "apaga el naranja y enciende el '
        'azul"), asi que debes incluir UNA ENTRADA POR CADA LED mencionado. '
        'Analiza el mensaje del usuario y responde UNICAMENTE con un JSON '
        'valido, sin texto adicional ni backticks, con este formato exacto: '
        '{"acciones": [{"accion": "encender" | "apagar", '
        '"led": "azul" | "naranja"}, ...], '
        '"respuesta": "una frase corta y natural en espanol confirmando o '
        'explicando todo lo que se hizo"}. '
        'Si el usuario dice "todo" o "ambos", incluye una entrada para azul '
        'y otra para naranja con la misma accion. '
        'Si no pide ninguna accion, responde con "acciones": [].'
    )
    data = {
        'model': modelo,
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': mensaje}
        ]
    }
    try:
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()  # Lo que nos dice esta línea es si existe un posible error HTTP
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.HTTPError as err:
        return f"Error de la API: {err}"
    except Exception as e:
        return f"Error Inesperado: {e}"


def controlar_led(accion, led):   # Funcion: traduce UNA decision (accion + led) en un comando serie y lo envia a la ESP32
    """Traduce una accion individual del chatbot en un comando serie para la ESP32."""
    if esp32 is None:
        return

    destino = led.upper()  # AZUL o NARANJA
    orden = "ON" if accion == "encender" else "OFF"
    comando = f"{destino} {orden}\n"

    try:
        esp32.write(comando.encode('utf-8'))
    except Exception as e:
        print(f"No se pudo enviar el comando a la ESP32: {e}")


def procesar_respuesta(respuesta_json_texto):   # Funcion: interpreta el JSON de la IA y ejecuta TODAS las acciones que traiga
    """Extrae la lista de acciones y la respuesta del JSON devuelto por la IA."""
    try:
        datos = json.loads(respuesta_json_texto)
        acciones = datos.get('acciones', [])
        respuesta = datos.get('respuesta', 'No entendi bien, podrias repetirlo?')
    except Exception:
        # Si el modelo no devolvió un JSON válido, se muestra tal cual
        acciones, respuesta = [], respuesta_json_texto

    for item in acciones:   # Recorre cada accion pedida (puede ser una o varias) y la ejecuta
        controlar_led(item.get('accion'), item.get('led'))

    return respuesta


def main():   # Funcion principal: maneja el bucle de conversacion con el usuario
    print("Bienvenido al chatbot domestico con Groq.")
    print("Presiona Enter para hablar por voz, o escribi el comando directamente.")
    print("Escribi 'salir' para terminar.")
    while True:
        entrada = input("\nTú (Enter para hablar, o escribi el comando): ")

        if entrada.lower() == 'salir':
            print("Chatbot: Hasta Luego!")
            break

        if entrada.strip() == '':
            mensaje_usuario = escuchar_voz()
            if mensaje_usuario is None:
                print("Chatbot: No entendi lo que dijiste, intenta de nuevo.")
                continue
        else:
            mensaje_usuario = entrada

        respuesta_cruda = enviar_mensaje(mensaje_usuario)
        respuesta_final = procesar_respuesta(respuesta_cruda)
        print(f"Chatbot: {respuesta_final}")
        # Nota: si la respuesta cruda no es un JSON valido (por ejemplo, un
        # error de la API de Groq), procesar_respuesta la muestra tal cual.


if __name__ == "__main__":
    main()