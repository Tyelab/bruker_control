import serial
import time
import csv
import numpy
import matplotlib


ser = serial.Serial('COM13', 115200)
ser.flushInput()
num_trials = 0

while num_trials < 21:
    try:
        ser_bytes = ser.readline()
        decoded_bytes = ser_bytes[0:len(ser_bytes)-2].decode("utf-8")
        print(decoded_bytes)
        num_trials += 1
        with open("test_data.csv","a") as f:
            writer = csv.writer(f,delimiter=",")
            writer.writerow([time.time(),decoded_bytes])
    except:
        print("Keyboard Interrupt")
        break
