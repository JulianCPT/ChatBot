# 🤖 ChatBot Doméstico — Control de LEDs por Voz o Texto

Proyecto de Ingeniería Mecatrónica — Universidad Militar Nueva Granada.

Chatbot en Python que permite **encender o apagar dos LEDs** (uno azul y
uno naranja) hablándole o escribiéndole en lenguaje natural, usando
reconocimiento de voz, un modelo de lenguaje (**Groq**) para interpretar
la intención del usuario, y comunicación **serie (USB)** con un **ESP32**
que ejecuta la orden física.

El chatbot entiende peticiones combinadas en un solo mensaje, por
ejemplo:
- "enciende el azul y el naranja"
- "apaga el naranja y prende el azul"
- "enciende todo"

---

## 📐 Arquitectura general

```
[Usuario habla o escribe]
        │
        ▼
┌───────────────────────┐
│   chatbot.py (PC)      │
│                        │
│  1. Si el usuario no   │
│     escribe nada y     │
│     presiona Enter,    │
│     graba y transcribe │
│     su voz             │
│                        │
│  2. Envía el texto a   │
│     la API de Groq     │
└──────────┬─────────────┘
           │  JSON: { "acciones": [...], "respuesta": "..." }
           ▼
┌───────────────────────┐
│  procesar_respuesta()  │  <- interpreta el JSON
│  controlar_led()       │  <- arma el comando de texto
└──────────┬─────────────┘
           │  Puerto serie (USB), ej. "AZUL ON\n"
           ▼
┌───────────────────────┐
│   ESP32                │
│   (sketch .ino)        │
│   enciende/apaga GPIO  │
└───────────────────────┘
```

**Idea clave:** el ESP32 **no interpreta lenguaje natural**. Toda la
inteligencia (entender qué pidió el usuario) vive en la PC, en Python,
apoyándose en la API de Groq. El ESP32 solo recibe comandos ya
decididos y simples como `"AZUL ON"` o `"TODO OFF"` por el cable USB, y
únicamente se encarga de mover los pines físicos. Esto es distinto a un
proyecto con MQTT/WiFi: aquí la comunicación es directa por cable
(serie), no por red.

---

## 📁 Estructura sugerida del repositorio

```
ChatBot/
├── chatbot.py           # Programa principal en Python (PC)
├── esp32_leds.ino        # Firmware del ESP32 (ejecuta comandos)
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ⚙️ Requisitos

- Python 3.10+
- Una cuenta en [Groq](https://console.groq.com/) para obtener una API
  key gratuita (se usa para interpretar el mensaje del usuario)
- Un ESP32 con:
  - LED azul → resistencia → **GPIO 26**
  - LED naranja → resistencia → **GPIO 27**
  - Cátodo de ambos LEDs → GND
- Arduino IDE (o PlatformIO) para subir `esp32_leds.ino`
- Un micrófono en la PC (para el modo de voz)

Instalar dependencias de Python:

```bash
pip install requests pyserial SpeechRecognition pyaudio
```

> `pyaudio` es necesario para que `SpeechRecognition` pueda usar el
> micrófono. En Windows a veces falla con `pip` normal; si eso pasa, se
> puede instalar con `pip install pipwin` y luego `pipwin install pyaudio`.

---

## 🔑 Configurar la API key de Groq

En el código, reemplaza el valor de `API_KEY` por tu propia key de Groq:

```python
API_KEY = 'Aca debe ir tu Api'
```

Si prefieres no dejarla escrita directamente en el archivo, también
puedes leerla desde una variable de entorno:

```python
import os
API_KEY = os.environ.get("GROQ_API_KEY")
```

Y definirla antes de correr el programa:

```powershell
$env:GROQ_API_KEY = "tu_api_key_aqui"
```

---

## ▶️ Cómo correrlo

1. Sube `esp32_leds.ino` a la ESP32 desde Arduino IDE.
2. Anota en qué puerto quedó conectada (`COM3` en Windows,
   `/dev/ttyUSB0` en Linux/Mac) y ajústalo en `chatbot.py`:
   ```python
   PUERTO_ESP32 = 'COM3'
   ```
3. Corre el chatbot:
   ```bash
   python chatbot.py
   ```
4. En la consola:
   - Escribe un comando directo (ej. `enciende el azul`) y presiona Enter.
   - O deja el campo vacío y presiona Enter para hablar por micrófono.
   - Escribe `salir` para terminar.

---

## 🧩 Explicación del código, bloque por bloque

### 1. `chatbot.py` — el programa principal

**Conexión serie con la ESP32**
```python
esp32 = serial.Serial(PUERTO_ESP32, BAUDIOS, timeout=2)
```
Abre el puerto USB donde está conectada la ESP32. Si falla (por
ejemplo, el ESP32 no está conectado o el puerto es otro), el chatbot
sigue funcionando pero avisa que no podrá mover los LEDs — no se cae
todo el programa por eso.

El parámetro `timeout=2` le pone un límite de 2 segundos a cualquier
operación de lectura sobre el puerto serie. Sin esto, si el programa
intentara leer una respuesta de la ESP32 y esta nunca llegara (cable
desconectado, ESP32 colgada, etc.), el programa se quedaría esperando
para siempre. Con el timeout, simplemente continúa después de esos 2
segundos.

**Reconocimiento de voz**
```python
def escuchar_voz():
    reconocedor = sr.Recognizer()
    with sr.Microphone() as fuente:
        audio = reconocedor.listen(fuente)
    texto = reconocedor.recognize_google(audio, language='es-ES')
```
Graba audio del micrófono y lo envía al servicio de reconocimiento de
voz de Google (gratuito, a través de la librería `SpeechRecognition`),
que devuelve el texto transcrito en español. Si no logra reconocer
nada, devuelve `None` y el chatbot le pide al usuario que repita.

El parámetro `language='es-ES'` le dice al servicio de Google qué
idioma y acento esperar. Sin esto, el reconocedor usa inglés por
defecto y transcribiría mal casi cualquier frase en español (podría
interpretar "enciende el azul" como una mezcla de palabras en inglés
sin sentido). Se eligió `es-ES` (español genérico/España) en vez de un
código regional como `es-CO` porque tiene mejor soporte y cobertura en
el servicio de Google que la mayoría de variantes latinoamericanas,
aunque para este caso de uso (comandos cortos y simples) la diferencia
práctica entre variantes del español es mínima.

`adjust_for_ambient_noise(fuente)` se llama antes de grabar para que el
reconocedor "escuche" un instante el ruido de fondo del ambiente y
calibre su sensibilidad — así distingue mejor dónde empieza y termina
la voz del usuario en vez de grabar solo silencio o ruido.

**Prompt de sistema y salida en JSON estricto**
```python
system_prompt = (
    'Eres un chatbot domestico que solo puede encender o apagar dos LEDs...'
    '{"acciones": [{"accion": "encender" | "apagar", "led": "azul" | "naranja"}, ...], '
    '"respuesta": "..."}'
)
```
Aquí está la parte más importante: en vez de pedirle a la IA una
respuesta libre, se le exige que **responda solo con un JSON** con una
lista de acciones (una por cada LED mencionado) y una frase de
confirmación. Esto es lo que permite manejar peticiones combinadas
como "apaga el naranja y enciende el azul" en un solo mensaje: el
modelo devuelve **dos acciones** en la lista `"acciones"`, una por cada
LED, y el programa las ejecuta una por una.

**Envío del mensaje a Groq**
```python
def enviar_mensaje(mensaje, modelo='openai/gpt-oss-120b'):
    response = requests.post(API_URL, headers=headers, json=data)
    return response.json()['choices'][0]['message']['content']
```
Hace la petición HTTP a la API de Groq con el prompt de sistema y el
mensaje del usuario, y devuelve el texto de la respuesta (que debería
ser el JSON descrito arriba).

Se usa `openai/gpt-oss-120b` como modelo por defecto porque, dentro del
catálogo de Groq, ofrece un buen equilibrio entre velocidad de
respuesta (Groq es conocido por su infraestructura de inferencia muy
rápida) y capacidad para seguir instrucciones estrictas de formato como
"responde solo con este JSON, sin texto adicional" — algo en lo que
modelos más pequeños suelen fallar con más frecuencia, agregando texto
extra antes o después del JSON.

**Traducir una acción a un comando serie**
```python
def controlar_led(accion, led):
    destino = led.upper()          # AZUL o NARANJA
    orden = "ON" if accion == "encender" else "OFF"
    comando = f"{destino} {orden}\n"
    esp32.write(comando.encode('utf-8'))
```
Convierte una decisión individual (por ejemplo `accion="encender"`,
`led="azul"`) en el texto exacto que la ESP32 sabe interpretar
(`"AZUL ON\n"`), y lo envía por el puerto serie. El `\n` al final es
importante: la comunicación serie es simplemente un flujo continuo de
bytes, sin "mensajes" delimitados de forma automática — por eso hace
falta un carácter que marque "aquí termina un comando", y `\n` es la
convención más común para eso (ver más abajo cómo lo lee la ESP32).

**Procesar la respuesta completa**
```python
def procesar_respuesta(respuesta_json_texto):
    datos = json.loads(respuesta_json_texto)
    acciones = datos.get('acciones', [])
    for item in acciones:
        controlar_led(item.get('accion'), item.get('led'))
    return respuesta
```
Convierte el texto JSON en un diccionario de Python, recorre **todas**
las acciones que vinieron en la lista (puede ser una, dos, o ninguna) y
las ejecuta en orden. Si el modelo no devolvió un JSON válido (por
ejemplo, si Groq tuvo un error), el `try/except` evita que el programa
se caiga: simplemente muestra el texto tal cual llegó.

**El loop principal**
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
Si el usuario presiona Enter sin escribir nada, se activa el modo voz;
si escribe algo, se usa eso directamente como comando. En ambos casos
el texto termina pasando por Groq y luego por `procesar_respuesta()`.

---

### 2. `esp32_leds.ino` — firmware del ESP32

**Filosofía del sketch**

Este programa **no piensa**, solo ejecuta. Toda la interpretación de
lenguaje ya se hizo en la PC; la ESP32 solo recibe líneas de texto ya
decididas (`"AZUL ON"`, `"TODO OFF"`, etc.) y mueve pines.

**Lectura no bloqueante del puerto serie, carácter por carácter**
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
En vez de esperar a que llegue una línea completa de una sola vez
(lo cual bloquearía el programa), la ESP32 va leyendo un carácter a la
vez y los va acumulando en `buffer`. Cuando encuentra un salto de línea
(`\n`, el que Python manda al final de cada comando), sabe que el
comando está completo y lo ejecuta. Este patrón es común en proyectos
de electrónica que reciben texto por serie/MQTT: nunca se sabe si el
mensaje llega de una vez o partido en pedazos, así que se arma poco a
poco hasta ver el delimitador.

**Ejecutar el comando**
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
Antes de comparar, se usa `trim()` para quitar espacios o saltos de
línea sobrantes que pudieran colarse al armar el `buffer`, y
`toUpperCase()` para que no importe si el comando llega en mayúsculas,
minúsculas o mezclado — así `"azul on"`, `"AZUL ON"` o `"Azul On"`
funcionan igual. Luego compara el texto recibido contra cada comando
conocido y mueve el pin correspondiente con `digitalWrite()`. `TODO ON` / `TODO OFF` controlan
ambos LEDs a la vez, y `ESTADO` responde con el estado actual de cada
uno — útil para verificar desde el monitor serial que todo está
sincronizado.

**Variables de estado**
```cpp
bool estadoAzul = false;
bool estadoNaranja = false;
```
Guardan en la ESP32 si cada LED está encendido o apagado, para poder
responder al comando `ESTADO` sin depender de leer el pin físico.

---

## 🧠 Conceptos clave (para quien no conozca IoT/electrónica)

**Comunicación serie (UART/USB)**
Es la forma más simple de que una PC y un microcontrolador (como el
ESP32) se hablen: un cable USB por el que se envían bytes en un solo
sentido a la vez, línea por línea. No necesita WiFi ni redes: por eso
este proyecto es más simple que uno con MQTT, pero requiere que la PC
y el ESP32 estén físicamente conectados por cable.

**Baudios**
Es la velocidad a la que viajan los datos por el puerto serie (aquí,
115200 baudios). Tanto la PC como la ESP32 deben usar el mismo valor,
o se leerán datos corruptos.

**API de un modelo de lenguaje (LLM) — Groq**
Un servicio en internet al que se le manda texto y devuelve una
respuesta generada por un modelo de inteligencia artificial. Aquí se
usa para "traducir" frases humanas ("prende el azul") en un formato que
el programa pueda procesar automáticamente.

**Forzar salida en JSON**
Pedirle a la IA que responda *solo* con un JSON (en vez de una
respuesta libre en lenguaje natural) permite que el código la lea de
forma confiable con `json.loads()`, sin tener que adivinar qué quiso
decir el modelo. Es una técnica común al conectar un LLM a un sistema
que necesita tomar acciones concretas, no solo mostrar texto.

**Reconocimiento de voz**
Convertir audio grabado en texto. Aquí se usa el servicio gratuito de
reconocimiento de voz de Google a través de la librería
`SpeechRecognition`, que necesita conexión a internet para funcionar
(no es reconocimiento local).

**GPIO (General Purpose Input/Output)**
Los pines del microcontrolador que se pueden programar para que
entreguen o lean una señal eléctrica. Aquí, GPIO 26 y GPIO 27 se
configuran como salida (`OUTPUT`) para prender o apagar cada LED con
`digitalWrite(pin, HIGH)` (encendido) o `LOW` (apagado).

**Variable de entorno / seguridad de API keys**
Una forma de guardar datos sensibles (como una API key) fuera del
código fuente, para no subirlos por accidente a GitHub. Se explica
cómo aplicarlo en la sección de configuración más arriba.

---

## 🔒 Nota

Este proyecto usa reconocimiento de voz **en la nube** (Google), por lo
que el audio grabado se envía a un servidor externo para transcribirse.

---

## 👤 Autor

Proyecto desarrollado por Julián — Ingeniería Mecatrónica, Universidad
Militar Nueva Granada.
