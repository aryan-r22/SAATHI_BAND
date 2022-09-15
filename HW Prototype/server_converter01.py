from flask import Flask
import pandas as pd
import serial
import time

from datetime import datetime
from smbus2 import SMBus        #For MLX90614
from mlx90614 import MLX90614

ser = serial.Serial('/dev/ttyUSB0', 115200)
ser.baudrate = 115200

size_int=30
size_float=30.0


fah_temp=[]
for i in range(size_int):
    fah_temp.append(0)
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

samples=1 #number of data to be sent to cloud in one cycle
counter50 = 0
garbage_data=10
garbageline=0

headers="GFORCEX,GFORCEY,GFORCEZ,ROT_X,ROT_Y,ROT_Z,GSR,HEARTRATE,SpO2 %,AMB TEMP MLX, OBJ TEMP MLX"  #Added TEMP MLX for the MLX90614
headers=headers.rstrip()

file = open("garbage.csv", "w" )
print("Created garbage file")

while(garbageline < garbage_data):
    getData=str(rl.readline())
    data_garbage=getData
    #print(data_garbage)        
    garbageline=garbageline+1

print("first garbage disposal complete")
file.close()

app=Flask(__name__)

@app.route("/")
def data():

    ser.reset_input_buffer()
    time.sleep(0.2)
    
    file= open("serverconverter.csv" , "w")
    line=0
    print("writind data to csv file")
    while( line <=samples):
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
        
        fah_temp[size_int-1]=mlx_obj_temp*1.8 + 32
        fah_mean=fah_temp[0]
        for i in range(size_int-1):
            fah_mean=fah_mean+ fah_temp[i+1]
            fah_temp[i]=fah_temp[i+1]
        mlx_obj_temp= fah_mean/size_float
        
        getData=(str(rl.readline().decode('utf-8').rstrip()) + "," + str(round(mlx_amb_temp,2)) + "," + str(round(mlx_obj_temp,2)))
        data=getData
        print (datetime.now())
        print(data)

        #file=open("servermini.csv", "a")
        file.write(data + "\n")
        bus.close()
        
        line=line+1

    print("writing complete")
    file.close()

    

    print("file closed")
    csv_file=pd.read_csv("serverconverter.csv")
    csv_file=csv_file.to_dict()
    return csv_file


if __name__ =="__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
        
