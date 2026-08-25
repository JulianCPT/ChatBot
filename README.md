<div align="center">

![Header](https://capsule-render.vercel.app/api?type=waving&color=0:2C5364,50:203A43,100:0F2027&height=220&section=header&text=ChatBot%20Doméstico&fontSize=48&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=Control%20de%20LEDs%20por%20Voz%20o%20Texto&descAlignY=58&descSize=18)

*Ingeniería Mecatrónica · Universidad Militar Nueva Granada*

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=20&duration=3000&pause=800&color=3AAFFF&center=true&vCenter=true&width=560&lines=%22enciende+el+azul+y+el+naranja%22;%22apaga+el+naranja+y+prende+el+azul%22;%22enciende+todo%22" alt="Typing SVG" />

<br/>

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![ESP32](https://img.shields.io/badge/ESP32-Arduino-E7352C?style=for-the-badge&logo=espressif&logoColor=white)
![Groq](https://img.shields.io/badge/LLM-Groq-F55036?style=for-the-badge&logo=lightning&logoColor=white)
![Voice](https://img.shields.io/badge/Voz-Google%20Speech-4285F4?style=for-the-badge&logo=googleassistant&logoColor=white)
![Status](https://img.shields.io/badge/estado-académico-6E40C9?style=for-the-badge)

</div>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0F2027,100:203A43&height=3&section=header" width="100%"/>

## ✨ ¿Qué hace este proyecto?

Un chatbot en **Python** que enciende o apaga dos LEDs — 🔵 **azul** y 🟠 **naranja** —
a partir de lo que el usuario **habla o escribe** en lenguaje natural.

<div align="center">

| 🎙️ Voz | 🧠 Groq (LLM) | 🔌 Serie (USB) | 💡 ESP32 |
|:---:|:---:|:---:|:---:|
| Transcribe el audio a texto | Interpreta la intención → JSON | Envía comandos ya decididos | Mueve los pines GPIO |

</div>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0F2027,100:203A43&height=3&section=header" width="100%"/>

## 📐 Arquitectura general

```
🗣️  Usuario habla o escribe
        │
        ▼
┌─────────────────────────┐
│   chatbot.py  (PC)       │
│                          │
│  1️⃣  Sin texto + Enter → │
│      graba y transcribe  │
│      la voz               │
│                          │
│  2️⃣  Envía el texto a    │
│      la API de Groq       │
└────────────┬─────────────┘
             │ JSON: { "acciones": [...], "respuesta": "..." }
             ▼
┌─────────────────────────┐
│  procesar_respuesta()    │  → interpreta el JSON
│  controlar_led()         │  → arma el comando de texto
└────────────┬─────────────┘
             │ Puerto serie (USB) — ej. "AZUL ON\n"
             ▼
┌─────────────────────────┐
│        ESP32              │
│    (esp32_leds.ino)       │
│  enciende/apaga GPIO      │
└─────────────────────────┘
```

> 💡 **Idea clave:** la ESP32 **no interpreta lenguaje natural**. Toda la
> inteligencia vive en la PC, apoyada en la API de Groq. La ESP32 solo
> recibe comandos ya decididos y simples (`"AZUL ON"`, `"TODO OFF"`) por
> cable USB y mueve pines. A diferencia de un proyecto con MQTT/WiFi,
> aquí la comunicación es **directa por cable**, no por red.

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0F2027,100:203A43&height=3&section=header" width="100%"/>

## 📁 Estructura del repositorio

```
ChatBot/
├── chatbot.py         # Programa principal en Python (PC)
├── esp32_leds.ino      # Firmware del ESP32
├── requirements.txt
├── .gitignore
└── README.md
```

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0F2027,100:203A43&height=3&section=header" width="100%"/>

## ⚙️ Requisitos

<div align="center">
<img src="https://skillicons.dev/icons?i=python,arduino,cpp&theme=dark" />
</div>

- ✅ Python 3.10+
- ✅ Cuenta gratuita en [Groq](https://console.groq.com/) (API key)
- ✅ Un ESP32 con:
  - LED 🔵 azul → resistencia → **GPIO 26**
  - LED 🟠 naranja → resistencia → **GPIO 27**
  - Cátodo de ambos LEDs → GND
- ✅ Arduino IDE o PlatformIO (para subir `esp32_leds.ino`)
- ✅ Micrófono en la PC (modo voz)

**Instalar dependencias de Python:**

```bash
pip install requests pyserial SpeechRecognition pyaudio
```

> ⚠️ `pyaudio` es necesario para el micrófono. En Windows a veces falla
> con `pip` normal; si eso pasa:
> ```bash
> pip install pipwin
> pipwin install pyaudio
> ```

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0F2027,100:203A43&height=3&section=header" width="100%"/>

## 🔑 Configurar la API key de Groq

```python
API_KEY = 'Aca debe ir tu Api'
```

O, mejor aún, léela desde una variable de entorno para no dejarla escrita en el código:

```python
import os
API_KEY = os.environ.get("GROQ_API_KEY")
```

```powershell
$env:GROQ_API_KEY = "tu_api_key_aqui"
```

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0F2027,100:203A43&height=3&section=header" width="100%"/>

## ▶️ Cómo correrlo

1. **Sube** `esp32_leds.ino` a la ESP32 desde Arduino IDE.
2. **Anota el puerto** (`COM3` en Windows, `/dev/ttyUSB0` en Linux/Mac) y ajústalo:
   ```python
   PUERTO_ESP32 = 'COM3'
   ```
3. **Corre** el chatbot:
   ```bash
   python chatbot.py
   ```
4. En la consola:

   | Acción | Cómo |
   |:---|:---|
   | 💬 Comando por texto | Escríbelo y presiona `Enter` |
   | 🎙️ Comando por voz | Deja el campo vacío y presiona `Enter` |
   | 🚪 Salir | Escribe `salir` |

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0F2027,100:203A43&height=3&section=header" width="100%"/>

## 🧩 Explicación del código, bloque por bloque

### 1️⃣ `chatbot.py` — el programa principal

<details>
<summary><b>🔌 Conexión serie con la ESP32</b></summary>

```python
esp32 = serial.Serial(PUERTO_ESP32, BAUDIOS, timeout=2)
```

Abre el puerto USB donde está conectada la ESP32. Si falla (ESP32
desconectada, puerto incorrecto), el chatbot **sigue funcionando** pero
avisa que no podrá mover los LEDs — no se cae todo el programa por eso.

El `timeout=2` limita a 2 segundos cualquier lectura sobre el puerto
serie. Sin esto, si la ESP32 nunca respondiera, el programa se quedaría
esperando para siempre.

</details>

<details>
<summary><b>🎙️ Reconocimiento de voz</b></summary>

```python
def escuchar_voz():
    reconocedor = sr.Recognizer()
    with sr.Microphone() as fuente:
        audio = reconocedor.listen(fuente)
    texto = reconocedor.recognize_google(audio, language='es-ES')
```

Graba audio del micrófono y lo envía al servicio gratuito de
reconocimiento de voz de Google, que devuelve el texto transcrito en
español. Si no logra reconocer nada, devuelve `None` y el chatbot pide
repetir.

- `language='es-ES'` evita que el reconocedor use inglés por defecto
  (lo que arruinaría casi cualquier frase en español). Se eligió
  `es-ES` sobre `es-CO` por su mejor soporte en el servicio de Google,
  aunque para comandos cortos la diferencia práctica es mínima.
- `adjust_for_ambient_noise(fuente)` calibra la sensibilidad al ruido
  de fondo antes de grabar, para distinguir mejor dónde empieza y
  termina la voz.

</details>

<details>
<summary><b>🧠 Prompt de sistema y salida en JSON estricto</b></summary>

```python
system_prompt = (
    'Eres un chatbot domestico que solo puede encender o apagar dos LEDs...'
    '{"acciones": [{"accion": "encender" | "apagar", "led": "azul" | "naranja"}, ...], '
    '"respuesta": "..."}'
)
```

En vez de una respuesta libre, se exige que el modelo responda **solo
con un JSON**: una lista de acciones (una por cada LED mencionado) más
una frase de confirmación. Así se manejan peticiones combinadas como
*"apaga el naranja y enciende el azul"* en un solo mensaje: el modelo
devuelve **dos acciones**, y el programa las ejecuta una por una.

</details>

<details>
<summary><b>📡 Envío del mensaje a Groq</b></summary>

```python
def enviar_mensaje(mensaje, modelo='openai/gpt-oss-120b'):
    response = requests.post(API_URL, headers=headers, json=data)
    return response.json()['choices'][0]['message']['content']
```

Hace la petición HTTP a Groq con el prompt de sistema y el mensaje del
usuario, y devuelve el texto de respuesta (el JSON esperado).

Se usa `openai/gpt-oss-120b` porque, dentro del catálogo de Groq,
equilibra bien velocidad de inferencia y capacidad de seguir
instrucciones estrictas de formato — algo en lo que modelos más
pequeños suelen fallar, agregando texto extra antes o después del JSON.

</details>

<details>
<summary><b>💡 Traducir una acción a un comando serie</b></summary>

```python
def controlar_led(accion, led):
    destino = led.upper()          # AZUL o NARANJA
    orden = "ON" if accion == "encender" else "OFF"
    comando = f"{destino} {orden}\n"
    esp32.write(comando.encode('utf-8'))
```

Convierte una decisión individual (`accion="encender"`, `led="azul"`)
en el texto exacto que entiende la ESP32 (`"AZUL ON\n"`). El `\n` final
marca dónde termina un comando, ya que la comunicación serie es un
flujo continuo de bytes sin "mensajes" delimitados automáticamente.

</details>

<details>
<summary><b>⚙️ Procesar la respuesta completa</b></summary>

```python
def procesar_respuesta(respuesta_json_texto):
    datos = json.loads(respuesta_json_texto)
    acciones = datos.get('acciones', [])
    for item in acciones:
        controlar_led(item.get('accion'), item.get('led'))
    return respuesta
```

Convierte el JSON en un diccionario, recorre **todas** las acciones
(una, dos, o ninguna) y las ejecuta en orden. Si el modelo no devolvió
un JSON válido, el `try/except` evita que el programa se caiga:
simplemente muestra el texto tal cual llegó.

</details>

<details>
<summary><b>🔁 El loop principal</b></summary>

```python
while True:
    entrada = input("...")
    if entrada.strip() == '':
        mensaje_usuario = escuchar_voz()
    else:
        mensaje_usuario = entrada
    respuesta_cruda = enviar_mensaje(mensaje_usuario)
    respuesta_final = procesar_respuesta(respuesta_cruda)
```

Si el usuario presiona `Enter` sin escribir nada, se activa el modo
voz; si escribe algo, se usa eso directamente. En ambos casos el texto
pasa por Groq y luego por `procesar_respuesta()`.

</details>

### 2️⃣ `esp32_leds.ino` — firmware del ESP32

> 🧠 **Filosofía del sketch:** este programa **no piensa**, solo ejecuta.
> Toda la interpretación de lenguaje ya se hizo en la PC.

<details>
<summary><b>📥 Lectura no bloqueante del puerto serie, carácter por carácter</b></summary>

```cpp
void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (buffer.length() > 0) {
        ejecutarComando(buffer);
        buffer = "";
      }
    } else {
      buffer += c;
    }
  }
}
```

En vez de esperar una línea completa de una sola vez (lo que
bloquearía el programa), la ESP32 lee un carácter a la vez y lo
acumula en `buffer`. Al encontrar `\n`, sabe que el comando está
completo y lo ejecuta. Patrón común en proyectos que reciben texto por
serie/MQTT, donde nunca se sabe si el mensaje llega completo o
partido.

</details>

<details>
<summary><b>✅ Ejecutar el comando</b></summary>

```cpp
void ejecutarComando(String cmd) {
  cmd.trim();
  cmd.toUpperCase();
  if (cmd == "AZUL ON") { ... }
  else if (cmd == "NARANJA OFF") { ... }
  else if (cmd == "TODO ON") { ... }
  ...
}
```

`trim()` quita espacios o saltos de línea sobrantes, y
`toUpperCase()` normaliza mayúsculas/minúsculas, para que
`"azul on"`, `"AZUL ON"` o `"Azul On"` funcionen igual. Luego compara
contra cada comando conocido y mueve el pin con `digitalWrite()`.
`TODO ON` / `TODO OFF` controlan ambos LEDs a la vez, y `ESTADO`
responde con el estado actual de cada uno.

</details>

<details>
<summary><b>📊 Variables de estado</b></summary>

```cpp
bool estadoAzul = false;
bool estadoNaranja = false;
```

Guardan si cada LED está encendido o apagado, para responder al
comando `ESTADO` sin depender de leer el pin físico.

</details>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0F2027,100:203A43&height=3&section=header" width="100%"/>

## 🧠 Conceptos clave

<details>
<summary><b>🔌 Comunicación serie (UART/USB)</b></summary>

Forma más simple de que una PC y un microcontrolador se hablen: un
cable USB por el que se envían bytes en un solo sentido a la vez,
línea por línea. No necesita WiFi ni redes — por eso este proyecto es
más simple que uno con MQTT, pero requiere que PC y ESP32 estén
conectados físicamente por cable.

</details>

<details>
<summary><b>⚡ Baudios</b></summary>

Velocidad a la que viajan los datos por el puerto serie (aquí, 115200
baudios). Tanto la PC como la ESP32 deben usar el mismo valor, o se
leerán datos corruptos.

</details>

<details>
<summary><b>🧠 API de un LLM — Groq</b></summary>

Servicio en internet al que se le manda texto y devuelve una respuesta
generada por IA. Aquí se usa para "traducir" frases humanas
(*"prende el azul"*) a un formato que el programa procesa
automáticamente.

</details>

<details>
<summary><b>📦 Forzar salida en JSON</b></summary>

Pedirle a la IA que responda *solo* con un JSON permite leerlo de
forma confiable con `json.loads()`, sin adivinar qué quiso decir el
modelo. Técnica común al conectar un LLM a un sistema que debe tomar
acciones concretas.

</details>

<details>
<summary><b>🎙️ Reconocimiento de voz</b></summary>

Convertir audio grabado en texto. Se usa el servicio gratuito de
Google a través de `SpeechRecognition`, que necesita conexión a
internet (no es reconocimiento local).

</details>

<details>
<summary><b>📌 GPIO (General Purpose Input/Output)</b></summary>

Pines del microcontrolador programables para entregar o leer una señal
eléctrica. Aquí, GPIO 26 y 27 se configuran como `OUTPUT` para
prender/apagar cada LED con `digitalWrite(pin, HIGH)` o `LOW`.

</details>

<details>
<summary><b>🔒 Variable de entorno / seguridad de API keys</b></summary>

Forma de guardar datos sensibles (como una API key) fuera del código
fuente, para no subirlos por accidente a GitHub.

</details>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0F2027,100:203A43&height=3&section=header" width="100%"/>

## 🔒 Nota de privacidad

> Este proyecto usa reconocimiento de voz **en la nube** (Google), por
> lo que el audio grabado se envía a un servidor externo para
> transcribirse.

<div align="center">

## 👤 Autor

**Julián** · Ingeniería Mecatrónica · Universidad Militar Nueva Granada

![Footer](https://capsule-render.vercel.app/api?type=waving&color=0:0F2027,50:203A43,100:2C5364&height=120&section=footer)

</div>
