from IMU import IMU
from datetime import datetime

import numpy as np
import math
import csv
import os
import time

from LaserVectorCalculator import calculateLaserVector

# PORT = "/dev/pts/5"
PORT = "/dev/ttyUSB0"
BAUD = 230400

now = datetime.now()

fileName = f"{now.strftime("%m.%d.%Y-%H:%M:%S")}.csv"
dirName = "./data/"

base_path = os.path.normpath(dirName)
path = os.path.join(base_path, fileName)
os.makedirs(base_path, exist_ok=True)

file = open(path, "x")
w = csv.writer(file)
 
arr = ["Time", "Ax", "Ay", "Az", "Wx", "Wy", "Wz", "q0", "q1", "q2", "q3"]

w.writerow(arr)

imu = IMU(PORT, BAUD)
imu.openDevice()

def readConfig():
    tVals: dict = imu.readRegister(0x02) 
    
    if (len(tVals)>0):
        for i in tVals:
            print(i, hex(tVals.get(i)))
    else:
        print("None")
    
    tVals = imu.readRegister(0x23)

    if (len(tVals)>0):
        print(str(tVals))
    else:
        print("None")

readConfig()

while True:
    data = imu.getOutputData()

    w.writerow([
        data.get("hour", 0) * (3600 * 1000) + data.get("minute", 0) * (60 * 1000) + data.get("second", 0) * (1000) + data.get("millisecond", 0),
        data.get("ax", "None"),
        data.get("ay", "None"),
        data.get("az", "None"),
        data.get("wx", "None"),
        data.get("wy", "None"),
        data.get("wz", "None"),
        data.get("q0", "None"),
        data.get("q1", "None"),
        data.get("q2", "None"),
        data.get("q3", "None")
    ])
    
    d2r = math.pi/180
    r2d = 180/math.pi

    encoder_z = 0*d2r
    encoder_a = 0*d2r

    encoderData = np.array([encoder_z, encoder_a])

    q0 = data.get("q0", "None")
    q1 = data.get("q1", "None")
    q2 = data.get("q2", "None")
    q3 = data.get("q3", "None")

    quatIMU = np.array([q0, q1, q2, q3])
    
    e = calculateLaserVector(encoderData, quatIMU)
    
    r = [10, 5, 10]; 
    r_x = r[0]
    r_y = r[1]
    r_z = r[2]



