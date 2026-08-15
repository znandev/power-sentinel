#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

#define FW_VERSION  "0.2.0"
#define DEVICE_NAME "Frigate-01"
#define DEVICE_MODEL "ESP8266-D1Mini"

#define PLN_PIN D5

const char* WIFI_SSID = "xxxxxxxxx";
const char* WIFI_PASS = "xxxxxxx";

const char* SERVER_IP = "xx.xxx.xx.xx";
const int SERVER_PORT = 8080;

WiFiClient client;
HTTPClient http;

unsigned long lastBlink = 0;
unsigned long lastHeartbeat = 0;

bool ledState = false;
bool lastState = HIGH;

//
// CONNECT WIFI
//

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

//
// SEND PLN STATE
//

void sendState(bool state) {

    if (WiFi.status() != WL_CONNECTED)
        return;

    String url =
        "http://" +
        String(SERVER_IP) +
        ":" +
        String(SERVER_PORT) +
        "/pln"
        "?state=" +
        String(state == LOW ? "ON" : "OFF") +
        "&device=" +
        String(DEVICE_NAME) +
        "&model=" +
        String(DEVICE_MODEL) +
        "&fw=" +
        String(FW_VERSION);

    Serial.println();
    Serial.print("Sending State : ");
    Serial.println(url);

    http.setTimeout(3000);

    http.begin(client, url);

    int code = http.GET();

    if (code > 0) {

        Serial.print("HTTP Code : ");
        Serial.println(code);

    } else {

        Serial.print("HTTP Error : ");
        Serial.println(http.errorToString(code));

    }

    http.end();

}

//
// HEARTBEAT
//

void sendHeartbeat(bool state) {

    if (WiFi.status() != WL_CONNECTED)
        return;

    String url =
        "http://" +
        String(SERVER_IP) +
        ":" +
        String(SERVER_PORT) +
        "/heartbeat"
        "?power=" +
        String(state == LOW ? "ON" : "OFF") +
        "&device=" +
        String(DEVICE_NAME) +
        "&model=" +
        String(DEVICE_MODEL) +
        "&fw=" +
        String(FW_VERSION) +

        "&rssi=" +
        String(WiFi.RSSI()) +

        "&ssid=" +
        String(WIFI_SSID) +

        "&heap=" +
        String(ESP.getFreeHeap()) +

        "&uptime=" +
        String(millis() / 1000);

    http.setTimeout(3000);

    http.begin(client, url);

    int code = http.GET();

    if (code > 0) {

        Serial.print("Heartbeat HTTP : ");
        Serial.println(code);

    } else {

        Serial.print("Heartbeat Error : ");
        Serial.println(http.errorToString(code));

    }

    http.end();

}

//
// SETUP
//

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

    // Sync pertama
    sendState(lastState);
    sendHeartbeat(lastState);

}

//
// LOOP
//

void loop() {

    //
    // Auto reconnect
    //

    if (WiFi.status() != WL_CONNECTED) {

        connectWifi();

    }

    //
    // Heartbeat server
    //

    if (millis() - lastHeartbeat >= 5000) {

        lastHeartbeat = millis();

        sendHeartbeat(lastState);

    }

    //
    // LED heartbeat
    //

    if (millis() - lastBlink >= 1000) {

        lastBlink = millis();

        ledState = !ledState;

        digitalWrite(
            LED_BUILTIN,
            ledState ? LOW : HIGH
        );

    }

    //
    // Detect PLN
    //

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

        // Sinkronkan heartbeat juga
        sendHeartbeat(state);

        Serial.println("==============================");

    }

    delay(50);

}