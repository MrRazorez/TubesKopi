#include <DHT.h>
#include <SPI.h>
#include <Adafruit_BMP280.h>

#define DHTPIN 2
#define DHTTYPE DHT11
#define BMP_SCK  (13)
#define BMP_MISO (12)
#define BMP_MOSI (11)
#define BMP_CS   (10)
#define RAINPIN A2

DHT dht(DHTPIN, DHTTYPE);
Adafruit_BMP280 bmp(BMP_CS, BMP_MOSI, BMP_MISO,  BMP_SCK);

void setup() {
    dht.begin();
    bmp.begin();
    pinMode(RAINPIN, INPUT);

    bmp.setSampling(Adafruit_BMP280::MODE_NORMAL, Adafruit_BMP280::SAMPLING_X2, Adafruit_BMP280::SAMPLING_X16, Adafruit_BMP280::FILTER_X16, Adafruit_BMP280::STANDBY_MS_500);

    Serial.begin(9600);
}

void loop() {
    if (Serial.available() > 0) {
        String line = Serial.readStringUntil('\n');

        if (line == "OK") {
            float h = dht.readHumidity();
            float t = bmp.readTemperature();
            float T = dht.readTemperature();
            float p = bmp.readPressure();
            float w = 1023 - analogRead(RAINPIN);

            Serial.print("hum:");
            Serial.print(h);
            Serial.print(",tmpBMP:");
            Serial.print(t);
            Serial.print(",tmpDHT:");
            Serial.print(T);
            Serial.print(",pre:");
            Serial.print(p);
            Serial.print(",wet:");
            Serial.print(w);
            Serial.print("\n");

            delay(500);
        }
    }
}