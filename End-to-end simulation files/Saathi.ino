#include <Wire.h>
#include <SPI.h>




//----- Heart Beat Sensor -----//
#define USE_ARDUINO_INTERRUPTS true    // Set-up low-level interrupts for most acurate BPM math.
#include <PulseSensorPlayground.h>

const int Pulsewire = 0; // A0 Analog pin
int Threshold = 550;     // Determine which Signal to "count as a beat" and which to ignore.
PulseSensorPlayground pulseSensor; // Pulse sensor instance created
//-----------------------------//


unsigned long delayTime;
int tempPin = 4; // A4 pin


void setup() {
  Serial.begin(9600);



// Heart beat sensor
  pulseSensor.analogInput(Pulsewire);
  pulseSensor.setThreshold(Threshold);
  pulseSensor.blinkOnPulse(13); // To blink Arduino's built-in LED on pulse
  if (pulseSensor.begin()) {
//    Serial.println("We created a pulseSensor Object !");  
  }

  delayTime = 1000;

  Serial.println();
}


int bpm;
float x,y,z;


void loop() {

    // Temperature
    Serial.print("Temp: ");
    Serial.println(read_temp());
    delay(1000);

    
    // BPM - Pulse rate
    bpm = pulseSensor.getBeatsPerMinute();
    Serial.print("BPM: ");
    Serial.println(bpm);
    delay(1000); 

    // Acceleration
    x = ((analogRead(A3)*2.0)/1024.0)-1;  
    y = ((analogRead(A2)*2.0)/1024.0)-1;
    z = ((analogRead(A1)*2.0)/1024.0)-1;
    Serial.print("Acc.X: ");
    Serial.println(x);
    delay(1000);
    Serial.print("Acc.Y: ");
    Serial.println(y);
    delay(1000);
    Serial.print("Acc.Z: ");
    Serial.println(z);
    delay(1000);

    delay(delayTime);
}


float read_temp(){
  int val = analogRead(tempPin);
  float mv = (val/1024.0)*5000.0; // converting to milli volts
  float cel = mv/10.0; // 10mV = 1 deg cel
  return cel;
}
