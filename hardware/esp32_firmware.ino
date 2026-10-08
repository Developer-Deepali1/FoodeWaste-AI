/**
 * FoodWaste AI - Phase 2 ESP32 Edge Firmware
 * Interconnects physical smart bin with FoodWaste AI FastAPI Backend.
 * Actuates SG90 servo trapdoors based on AI Decision Engine response.
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <ESP32Servo.h>

// Wi-Fi Configuration
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* serverUrl = "http://192.168.1.100:8000/decision";

// Actuator Pin Definitions
const int SERVO_ORGANIC_PIN = 18;
const int SERVO_RECYCLABLE_PIN = 19;
const int BUZZER_PIN = 25;

Servo servoOrganic;
Servo servoRecyclable;

void setup() {
  Serial.begin(115200);
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  // Initialize Servos to locked position (0 degrees)
  servoOrganic.attach(SERVO_ORGANIC_PIN);
  servoRecyclable.attach(SERVO_RECYCLABLE_PIN);
  servoOrganic.write(0);
  servoRecyclable.write(0);

  // Connect to Wi-Fi
  Serial.print("Connecting to Wi-Fi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n[IoT Bin Online] Connected to FoodWaste AI Gateway");
}

void loop() {
  // In real operation, loop triggers on proximity sensor detection.
  // Sample test invocation:
  delay(10000);
  sendDecisionTestQuery();
}

void sendDecisionTestQuery() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    // Sample payload simulating edge vision output
    String requestPayload = "{\"objects\":[{\"object\":\"banana_peel\",\"category\":\"Organic\",\"confidence\":0.96}]}";

    int httpCode = http.POST(requestPayload);
    if (httpCode == HTTP_CODE_OK) {
      String response = http.getString();
      Serial.println("[AI Response]: " + response);

      StaticJsonDocument<1024> doc;
      deserializeJson(doc, response);

      const char* status = doc["status"];
      const char* actionType = doc["action_type"];

      if (strcmp(status, "Mixed Waste") == 0) {
        // Mixed waste alert: Keep flaps locked and trigger buzzer siren
        Serial.println("⚠ MIXED WASTE! Flaps locked.");
        digitalWrite(BUZZER_PIN, HIGH);
        delay(300);
        digitalWrite(BUZZER_PIN, LOW);
      } 
      else if (strcmp(actionType, "DIRECT_DISPOSAL") == 0) {
        // Safe disposal: Open designated trapdoor
        Serial.println("✓ Opening Organic Bin flap...");
        servoOrganic.write(90);
        delay(5000);
        servoOrganic.write(0);
      }
    }
    http.end();
  }
}
