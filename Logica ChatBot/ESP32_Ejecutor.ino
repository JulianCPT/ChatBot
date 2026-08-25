/*
  ============================================================
  ESP32 - Ejecutor de comandos para el chatbot domestico
  ============================================================

  Este sketch NO interpreta lenguaje natural: recibe comandos
  simples ya decididos por el chatbot en Python (que usa la
  API de DeepSeek para interpretar la voz del usuario) a
  través del puerto Serie (USB), y enciende/apaga los LEDs.

  Conexiones (según el circuito):
    - LED azul -> resistencia -> GPIO 26
    - LED naranja  -> resistencia -> GPIO 27
    - Cátodos de ambos LEDs -> GND

  Comandos que entiende (una línea de texto terminada en '\n'):
    AZUL ON
    AZUL OFF
    NARANJA ON
    NARANJA OFF
    TODO ON
    TODO OFF
    ESTADO
  ============================================================
*/

const int PIN_LED_AZUL = 26;
const int PIN_LED_NARANJA  = 27;

bool estadoAzul = false;
bool estadoNaranja  = false;

String buffer = "";

void setup() {
  Serial.begin(115200);
  pinMode(PIN_LED_AZUL, OUTPUT);
  pinMode(PIN_LED_NARANJA, OUTPUT);
  digitalWrite(PIN_LED_AZUL, LOW);
  digitalWrite(PIN_LED_NARANJA, LOW);
  Serial.println("ESP32 lista. Esperando comandos del chatbot...");
}

void ejecutarComando(String cmd) {
  cmd.trim();
  cmd.toUpperCase();

  if (cmd == "AZUL ON") {
    estadoAzul = true;
    digitalWrite(PIN_LED_AZUL, HIGH);
    Serial.println("OK: LED azul encendido");
  } else if (cmd == "AZUL OFF") {
    estadoAzul = false;
    digitalWrite(PIN_LED_AZUL, LOW);
    Serial.println("OK: LED azul apagado");
  } else if (cmd == "NARANJA ON") {
    estadoNaranja = true;
    digitalWrite(PIN_LED_NARANJA, HIGH);
    Serial.println("OK: LED naranja encendido");
  } else if (cmd == "NARANJA OFF") {
    estadoNaranja = false;
    digitalWrite(PIN_LED_NARANJA, LOW);
    Serial.println("OK: LED naranja apagado");
  } else if (cmd == "TODO ON") {
    estadoAzul = true;
    estadoNaranja = true;
    digitalWrite(PIN_LED_AZUL, HIGH);
    digitalWrite(PIN_LED_NARANJA, HIGH);
    Serial.println("OK: Ambos LEDs encendidos");
  } else if (cmd == "TODO OFF") {
    estadoAzul = false;
    estadoNaranja = false;
    digitalWrite(PIN_LED_AZUL, LOW);
    digitalWrite(PIN_LED_NARANJA, LOW);
    Serial.println("OK: Ambos LEDs apagados");
  } else if (cmd == "ESTADO") {
    String estado = "ESTADO Azul=";
    estado += estadoAzul ? "ON" : "OFF";
    estado += " Naranja=";
    estado += estadoNaranja ? "ON" : "OFF";
    Serial.println(estado);
  } else if (cmd.length() > 0) {
    Serial.println("ERROR: comando no reconocido -> " + cmd);
  }
}

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
