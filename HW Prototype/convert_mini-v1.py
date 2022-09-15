#import pandas as pd
#import firebase_admin
import serial
import time
from datetime import datetime

from smbus2 import SMBus        #For MLX90614
from mlx90614 import MLX90614

##firebase credentials
#from firebase_admin import credentials, firestore
#cred = credentials.Certificate('./saathi-c9678-firebase-adminsdk-qj7we-6c75ef6a2e.json');
#firebase_admin.initialize_app(cred, 
#{
#'databaseURL': 'https://saathi-c9678.firebaseio.com/'
#})
#db = firestore.client()
## doc_ref = db.collection(u’applications’)
#doc_ref=db.collection('users').document('uid7').collection('sensorReadings')

#Serial port setup , change baud and serial port
ser = serial.Serial('/dev/ttyUSB0', 115200)
ser.baudrate = 115200
#ser.port = 'COM5' #Already selected
#ser.open()        #Already open

#to buffer the incoming data
class ReadLine:
    def __init__(self, s):
        self.buf = bytearray()
        self.s = s
    
    def readline(self):
        i = self.buf.find(b"\n")
        if i >= 0:
            r = self.buf[:i+1]
            self.buf = self.buf[i+1:]
            return r
        while True:
            i = max(1, min(2048, self.s.in_waiting))
            data = self.s.read(i)
            i = data.find(b"\n")
            if i >= 0:
                r = self.buf + data[:i+1]
                self.buf[0:] = data[i+1:]
                return r
            else:
                self.buf.extend(data)

rl = ReadLine(ser)

samples=50 #number of data to be sent to cloud in one cycle
counter100 = 0

#garbage file data number defination
garbage_data=10
garbageline=0
garbage_data2=15
garbageline2=0
#definging and processing headers
headers="GFORCEX,GFORCEY,GFORCEZ,ROT_X,ROT_Y,ROT_Z,GSR,HEARTRATE,SpO2 %,AMB TEMP MLX, OBJ TEMP MLX"  #Added TEMP MLX for the MLX90614
headers=headers.rstrip()

#garbaging the initial sensor values
file = open("garbage.csv", "w" )
print("Created file")

while(garbageline < garbage_data):
    getData=str(rl.readline())
    data_garbage=getData
    #print(data_garbage)        
    garbageline=garbageline+1

print("first garbage disposal complete")
file.close()

#infinite loop to send data from serial to cloud
while(1):
    file = open("garbage2.csv", "w" )
    print("Created file")

    

    while(garbageline2 < garbage_data2):
        getData=str(rl.readline())
        data_garbage2=getData
     #print(data_garbage2)        
        garbageline2=garbageline2+1

    print("SECOND Garbage disposal complete")
    file.close()

    file = open("servermini.csv", "w" )
    print("Created file")

    line=0

    print("writing data to file " + "all.csv")
    while( line <= samples ):
        bus = SMBus(1)
        tempSensor = MLX90614(bus, address=0x5A)
        if line==0:
            print("Printing Column Headers")
            print(headers)
            file.write(headers + "\n")
        else:
            print("Line " + str(line) + ": writing...")
        
        mlx_amb_temp = tempSensor.get_amb_temp()
        mlx_obj_temp = tempSensor.get_obj_temp()
        getData=(str(rl.readline().decode('utf-8').rstrip()) + "," + str(round(mlx_amb_temp,2)) + "," + str(round(mlx_obj_temp,2)))
        data=getData
        print (datetime.now())
        print(data)

        file=open("servermini.csv", "a")
        file.write(data + "\n")
        bus.close()
        
        line=line+1

    print("writing complete")
    file.close()
    counter100 = counter100 + 1
    print("Counter100: " + str(counter100))
    print("Uploading data to the cloud...")

    

    #df = pd.read_csv('all.csv')
    #tmp = df.to_dict(orient='records')
    #list(map(lambda x: doc_ref.add(x), tmp))
    ser.reset_input_buffer()
    time.sleep(0.2)
