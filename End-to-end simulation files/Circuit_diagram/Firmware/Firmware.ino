// Including Libraries
#include "Arduino.h"
#include "BTHC05.h"
#include "LM35.h"
#include "MPU6050.h"
#include "Wire.h"
#include "I2Cdev.h"
#include "MAX30100.h"

// Pin Definitions
#define BTHC05_PIN_TXD  1
#define BTHC05_PIN_RXD  0
#define LOplus  4            // Setup for leads off detection LO +
#define LOminus  5           // Setup for leads off detection LO -
#define HEARTRATE_PIN_SIG A3
#define LM35_PIN_VOUT  A2
#define GSR_PIN_SIG  A6

// Global variables and defines
int16_t mpu6050Ax, mpu6050Ay, mpu6050Az;
int16_t mpu6050Gx, mpu6050Gy, mpu6050Gz;
int gsr_val = 0;
int gsr_avg = 0;

// object initialization
BTHC05 bthc05(BTHC05_PIN_RXD,BTHC05_PIN_TXD);
LM35 lm35(LM35_PIN_VOUT);
MPU6050 mpu6050;

// defining vars for testing menu
const int timeout = 10000;       //defining timeout of 10 sec
char menuOption = 0;
long time0;

void setup()
{
  // Setup Serial which is useful for debugging
  // Use the Serial Monitor to view printed messages
  Serial.begin(9600);
  while (!Serial) ; // wait for serial port to connect. Needed for native USB
  Serial.println("start");
  
  bthc05.begin(9600);
  //This example uses HC-05 Bluetooth to communicate with an Android device.
  //Download bluetooth terminal from google play store, https://play.google.com/store/apps/details?id=Qwerty.BluetoothTerminal&hl=en
  //Pair and connect to 'HC-05', the default password for connection is '1234'.
  //You should see this message from your arduino on your android device
  bthc05.println("Bluetooth On....");
  Wire.begin();
  mpu6050.initialize();
  menuOption = menu();
}

void loop() 
{
  if(menuOption == '1') 
  {
    // LM35DZ - Temperature Sensor - Test Code
    //Get Measurment from LM35 temperature sensor.
    float lm35TempC = lm35.getTempC();
    Serial.print(F("Temp: ")); Serial.print(lm35TempC); Serial.println(F("[°C]"));
  }
  else if(menuOption == '2') 
  {
    // HC-05 Bluetooth Module Test Code
    String bthc05Str = "";
    //Receive String from bluetooth device
    if (bthc05.available()) 
    {
      //Read a line from bluetooth terminal
      bthc05Str = bthc05.readStringUntil('\n');
      // Printing data to serial monitor
      Serial.print("BT Raw Data: ");
      Serial.println(bthc05Str);
    }
    //Send sensor data to Bluetooth device
    bthc05.println("Sensor data can be put here");
  }
  else if(menuOption == '3')
  {
    // AD8232 ECG Sensor Test code
    if((digitalRead(LOplus) == 1)||(digitalRead(LOminus) == 1))
    {
      Serial.println('!');
    }
    else
    {
      // send the value of analog input 0:
      Serial.println(analogRead(A3));
    }
    delay(1);          //Wait for a bit to prevent serial data from saturating
  }
  else if(menuOption == '4')
  {
    // MAX30100 - Heart Rate and SpO2 Test code To be added
  }
  else if(menuOption == '5') 
  {
    // MPU-6050 - Accelerometer and Gyro - Test Code
    mpu6050.getMotion6(&mpu6050Ax, &mpu6050Ay, &mpu6050Az, &mpu6050Gx, &mpu6050Gy, &mpu6050Gz);   //read accelerometer and gyroscope raw data in three axes
    double mpu6050Temp = ((double)mpu6050.getTemperature() + 12412.0) / 340.0;
    Serial.print("a/g-\t");
    Serial.print(mpu6050Ax); Serial.print("\t");
    Serial.print(mpu6050Ay); Serial.print("\t");
    Serial.print(mpu6050Az); Serial.print("\t");
    Serial.print(mpu6050Gx); Serial.print("\t");
    Serial.print(mpu6050Gy); Serial.print("\t");
    Serial.print(mpu6050Gz); Serial.print("\t");
    Serial.print(F("Temp- "));   
    Serial.println(mpu6050Temp);
    delay(100);
  }
  else if(menuOption == '6') 
  {
    // GSR Sensor Module - Test Code
    long gsr_sum=0;
    for(int i=0;i<10;i++)              //Average the 10 measurements to remove the glitch
    {
      gsr_val=analogRead(GSR_PIN_SIG);
      gsr_sum += gsr_val;
      delay(5);
    }
    gsr_avg = gsr_sum/10;
    Serial.println(gsr_avg);
  }
  
  if (millis() - time0 > timeout)
  {
      menuOption = menu();
  }
}

// Menu function for selecting the components to be tested
char menu()
{
  Serial.println(F("\nWhich component would you like to test?"));
  Serial.println(F("(1) LM35DZ - Temperature Sensor"));
  Serial.println(F("(2) HC-05 Bluetooth Serial Module"));
  Serial.println(F("(3) AD8232 Analog Heart Rate Monitor Sensor (ECG"));
  Serial.println(F("(4) MAX30100 - Particle Sensor (HR & SpO2)"));
  Serial.println(F("(5) MPU-6050 - Accelerometer and Gyro"));
  Serial.println(F("(6) GSR Sensor Module"));
  Serial.println(F("(menu) send anything else or press on board reset button\n"));
  while (!Serial.available());
  
  // Read data from serial monitor if received
  while (Serial.available()) 
  {
    char c = Serial.read();
    if (isAlphaNumeric(c)) 
    {
      if(c == '1') 
        Serial.println(F("Now Testing LM35DZ - Temperature Sensor"));
      else if(c == '2')
        Serial.println(F("Now Testing HC-05 Bluetooth Serial Module"));
      else if(c == '3') 
        Serial.println(F("Now Testing AD8232 Analog Heart Rate Monitor Sensor (ECG)"));
      else if(c == '4') 
        Serial.println(F("MAX30100 - Now Testing Particle Sensor - No test code"));
      else if(c == '5') 
        Serial.println(F("Now Testing MPU-6050 - Accelerometer and Gyro"));
      else if(c == '6')
        Serial.println(F("Now Testing GSR Sensor Module"));
      else
      {
        Serial.println(F("Unexpected input!"));
        return 0;
      }
      time0 = millis();
      return c;
    }
  }
}
