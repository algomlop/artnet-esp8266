#include <ESPAsyncUDP.h>

#include <WiFiManager.h> // https://github.com/tzapu/WiFiManager
#include <FastLED.h>
#include <ArtnetWifi.h>

const int numLeds = 30; // Change if your setup has more or less LED's
const int numberOfChannels = numLeds * 3; // Total number of DMX channels you want to receive (1 led = 3 channels)
#define DATA_PIN 12 //The data pin that the WS2812 strips are connected to.
CRGB leds[numLeds];

// Artnet settings
ArtnetWifi artnet;
const int startUniverse = 0;

bool sendFrame = 1;
int previousDataLength = 0;



void onDmxFrame(uint16_t universe, uint16_t length, uint8_t sequence, uint8_t* data)
{
  sendFrame = 1;


  
  // set brightness of the whole strip 
  if (universe == 15)
  {
    FastLED.setBrightness(data[0]);
    Serial.print("Brightness: ");      // Space separator for readability
        Serial.print(data[0]);  // Print each byte in decimal
    Serial.print(" ");      // Space separator for readability
  }
  // read universe and put into the right part of the display buffer
  for (int i = 0; i < length / 3; i++)
  {
    int led = i + (universe - startUniverse) * (previousDataLength / 3);
    if (led < numLeds)
    {
      leds[led] = CRGB(data[i * 3], data[i * 3 + 1], data[i * 3 + 2]);
      Serial.print("LED: ");
      Serial.print(led);
      Serial.print(" ");  // Separador para legibilidad
      
      Serial.print(data[i * 3]);       // Rojo
      Serial.print(", ");
      Serial.print(data[i * 3 + 1]);   // Verde
      Serial.print(", ");
      Serial.print(data[i * 3 + 2]);   // Azul
      Serial.println();  // Nueva línea para separar cada LED
    }
  }
  previousDataLength = length;     
  FastLED.show();
}

void setup()
{
  Serial.begin(115200);
  WiFiManager wm;


  bool res;
  res = wm.autoConnect("AutoConnectAP",""); // password protected ap

  if(!res) {
      Serial.println("Failed to connect");
      // ESP.restart();
  } 
  else {
      //if you get here you have connected to the WiFi    
      Serial.println("connected...yeey :)");

      artnet.begin();
      FastLED.addLeds<WS2812, DATA_PIN, GRB>(leds, numLeds);
    
      // onDmxFrame will execute every time a packet is received by the ESP32
      artnet.setArtDmxCallback(onDmxFrame);
  }
  

}

void loop()
{
  // we call the read function inside the loop
  artnet.read();
}

