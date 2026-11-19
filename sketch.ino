#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ArduinoJson.h>
#include "secrets.h"

#define DHTPIN 15
#define DHTTYPE DHT22
#define POT_CORRIENTE_PIN 34
#define RELAY_PIN 26
#define LED_ESTADO_PIN 2

DHT dht(DHTPIN, DHTTYPE);
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

unsigned long ultimoCiclo = 0;
const unsigned long INTERVALO_MS = 5000; // Intervalo fijo de 5 segundos
bool cargadorActivo = true;

void conectarWiFi() {
  Serial.print("Conectando a WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(400);
    Serial.print(".");
  }
  Serial.println("\nWiFi conectado -> IP: " + WiFi.localIP().toString());
}

// Recepción de comandos RPC desde el interruptor de ThingsBoard
void callbackMQTT(char* topic, byte* payload, unsigned int length) {
  String topicStr = String(topic);
  String mensaje = "";
  for (unsigned int i = 0; i < length; i++) {
    mensaje += (char)payload[i];
  }
  Serial.println("RPC ThingsBoard [" + topicStr + "]: " + mensaje);

  StaticJsonDocument<200> rpcDoc;
  DeserializationError error = deserializeJson(rpcDoc, mensaje);

  if (!error && rpcDoc.containsKey("params")) {
    cargadorActivo = rpcDoc["params"].as<bool>();
  } else if (mensaje.indexOf("true") >= 0 || mensaje.indexOf("1") >= 0) {
    cargadorActivo = true;
  } else if (mensaje.indexOf("false") >= 0 || mensaje.indexOf("0") >= 0) {
    cargadorActivo = false;
  }

  digitalWrite(RELAY_PIN, cargadorActivo ? HIGH : LOW);
  digitalWrite(LED_ESTADO_PIN, cargadorActivo ? HIGH : LOW);
  Serial.println(cargadorActivo ? ">> CONTACTOR: HABILITADO (ON)" : ">> CONTACTOR: CORTE ACTIVADO (OFF)");

  // Confirmar respuesta RPC a ThingsBoard para evitar timeout en el interruptor
  String requestId = topicStr.substring(topicStr.lastIndexOf('/') + 1);
  String responseTopic = "v1/devices/me/rpc/response/" + requestId;
  mqttClient.publish(responseTopic.c_str(), cargadorActivo ? "true" : "false");
}

void reconectarMQTT() {
  while (!mqttClient.connected()) {
    Serial.print("Conectando a ThingsBoard MQTT...");
    if (mqttClient.connect("ESP32_VoltGuard", TB_TOKEN, NULL)) {
      Serial.println(" Conectado!");
      mqttClient.subscribe(TOPIC_CONTROL);
    } else {
      Serial.print(" Error rc=");
      Serial.print(mqttClient.state());
      Serial.println(" reintentando en 2s...");
      delay(2000);
    }
  }
}

void registrarEnInfluxDB(float tempCeldas, float corrienteAmp, int estadoRele) {
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClientSecure clientSecure;
    clientSecure.setInsecure();

    HTTPClient http;
    if (http.begin(clientSecure, INFLUX_URL)) {
      http.addHeader("Authorization", "Token " + String(INFLUX_TOKEN));
      http.addHeader("Content-Type", "text/plain; charset=utf-8");

      String lineProtocol = "bahia_carga,estacion=bahia_01 temperatura_celdas=" + String(tempCeldas, 2) +
                            ",corriente_carga=" + String(corrienteAmp, 2) +
                            ",estado_cargador=" + String(estadoRele);

      int httpCode = http.POST(lineProtocol);
      Serial.println("InfluxDB HTTP Status: " + String(httpCode));
      http.end();
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(LED_ESTADO_PIN, OUTPUT);

  digitalWrite(RELAY_PIN, HIGH);
  digitalWrite(LED_ESTADO_PIN, HIGH);

  dht.begin();
  conectarWiFi();

  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  mqttClient.setCallback(callbackMQTT);
}

void loop() {
  if (!mqttClient.connected()) {
    reconectarMQTT();
  }
  mqttClient.loop();

  unsigned long ahora = millis();
  if (ahora - ultimoCiclo >= INTERVALO_MS) {
    ultimoCiclo = ahora;

    float temperatura = dht.readTemperature();
    if (isnan(temperatura)) temperatura = 24.0;

    int lecturaADC = analogRead(POT_CORRIENTE_PIN);
    float corriente = (lecturaADC / 4095.0) * 8.0;
    if (!cargadorActivo) {
      corriente = 0.0;
    }

    StaticJsonDocument<200> doc;
    doc["temperatura_celdas"] = round(temperatura * 100.0) / 100.0;
    doc["corriente_carga"] = round(corriente * 100.0) / 100.0;
    doc["estado_cargador"] = cargadorActivo ? 1 : 0;

    char jsonBuffer[200];
    serializeJson(doc, jsonBuffer);
    mqttClient.publish(TOPIC_DATOS, jsonBuffer);
    Serial.println("ThingsBoard Telemetry -> " + String(jsonBuffer));

    registrarEnInfluxDB(temperatura, corriente, cargadorActivo ? 1 : 0);
  }
}
