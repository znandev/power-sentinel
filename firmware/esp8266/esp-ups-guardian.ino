#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

#define FW_VERSION "0.2.0"
#define PLN_PIN D5
#define DEVICE_NAME "Frigate-01"

const char* WIFI_SSID = "MikroTik-RB9412nd";
const char* WIFI_PASS = "04122025";

const char* SERVER_IP = "10.77.227.100";
const int SERVER_PORT = 8080;

WiFiClient client;
HTTPClient http;

unsigned long lastBlink = 0;
unsigned long lastHeartbeat = 0;

bool ledState = false;
bool lastState = HIGH;

// ======================================================
// CONNECT WIFI
// ======================================================

void connectWifi() {

  if (WiFi.status() == WL_CONNECTED)
    return;

  Serial.println();
  Serial.println("================================");
  Serial.println("Connecting WiFi...");
  Serial.println("================================");

  WiFi.mode(WIFI_STA);
  WiFi.hostname("ESP-UPS-Guardian");
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  unsigned long start = millis();

  while (WiFi.status() != WL_CONNECTED) {

    Serial.print(".");

    digitalWrite(LED_BUILTIN, LOW);
    delay(100);
    digitalWrite(LED_BUILTIN, HIGH);
    delay(400);

    if (millis() - start > 30000) {

      Serial.println();
      Serial.println("WiFi Timeout!");

      return;

    }
  }

  Serial.println();
  Serial.println("================================");
  Serial.println("WiFi Connected!");
  Serial.print("IP Address : ");
  Serial.println(WiFi.localIP());
  Serial.println("================================");
}

// ======================================================
// SEND STATE TO SERVER
// ======================================================

void sendState(bool state) {

  if (WiFi.status() != WL_CONNECTED) {

    Serial.println("WiFi disconnected!");
    return;

  }

  String url =
      "http://" +
      String(SERVER_IP) +
      ":" +
      String(SERVER_PORT) +
      "/pln?state=" +
      (state == LOW ? "ON" : "OFF");

  Serial.println();
  Serial.print("Sending : ");
  Serial.println(url);

  http.setTimeout(3000);

  http.begin(client, url);

  int code = http.GET();

  if (code > 0) {

    Serial.print("HTTP Code : ");
    Serial.println(code);

    String payload = http.getString();

    Serial.print("Response  : ");
    Serial.println(payload);

  } else {

    Serial.print("HTTP Error : ");
    Serial.println(http.errorToString(code));

  }

  http.end();

}

// ======================================================
// SETUP
// ======================================================

void setup() {

  Serial.begin(115200);

  pinMode(PLN_PIN, INPUT_PULLUP);
  pinMode(LED_BUILTIN, OUTPUT);

  digitalWrite(LED_BUILTIN, HIGH);

  Serial.println();
  Serial.println("================================");
  Serial.println(" ESP UPS Guardian");
  Serial.print(" Firmware : ");
  Serial.println(FW_VERSION);
  Serial.println("================================");

  connectWifi();

  lastState = digitalRead(PLN_PIN);

  Serial.print("Initial State : ");

  if (lastState == LOW)
    Serial.println("PLN ON");
  else
    Serial.println("PLN OFF");

  sendState(lastState);

}

void sendHeartbeat() {

    if (WiFi.status() != WL_CONNECTED)
        return;

    String url =
        "http://" +
        String(SERVER_IP) +
        ":" +
        String(SERVER_PORT) +
        "/heartbeat";

  http.setTimeout(3000);

  http.begin(client, url);

  int code = http.GET();

  if(code <= 0){

    Serial.print("Heartbeat Error : ");
    Serial.println(http.errorToString(code));

  }

  http.end();

}

// ======================================================
// LOOP
// ======================================================

void loop() {

  // Auto reconnect WiFi
  if (WiFi.status() != WL_CONNECTED) {

    connectWifi();

  }

  // Heartbeat LED
  // LED Heartbeat
  if (millis() - lastBlink >= 1000) {

     lastBlink = millis();

     ledState = !ledState;

     digitalWrite(LED_BUILTIN, ledState ? LOW : HIGH);

  }

  bool state = digitalRead(PLN_PIN);

  if (state != lastState) {

    lastState = state;

    Serial.println();
    Serial.println("==============================");

    if (state == LOW)
      Serial.println("PLN ON");
    else
      Serial.println("PLN OFF");

    sendState(state);

    Serial.println("==============================");

  }

  delay(50);

}
