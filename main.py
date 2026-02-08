from IMU import IMU
from datetime import datetime

import numpy as np
import math
import csv
import os
import time

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

def quaternionToEulerAngle(q1, q2, q3, q4):
    
    a11 = q1 ** 2 - q2 ** 2 - q3 ** 2 + q4 ** 2
    a12 = 2 * ( q1 * q2 + q3 * q4 )
    a13 = 2 * ( q1 * q3 - q2 * q4 )
    a21 = 2 * ( q1 * q2 - q3 * q4 )
    a22 = q2 ** 2 - q1 ** 2 - q3 ** 2 + q4 ** 2
    a23 = 2 * ( q2 * q3 + q1 * q4 )
    a31 = 2 * ( q1 * q3 + q2 * q4 )
    a32 = 2 * ( q2 * q3 - q1 * q4 )
    a33 = q3 ** 2 - q1 ** 2 - q2 ** 2 + q4 ** 2

    DCM = [	[a11, a12, a13], [a21, a22, a23], [a31, a32, a33] ]

    psi 	= math.atan2( a12, a11 )
    theta 	= math.atan2( -a13, math.sqrt( a11 * a11 + a12 * a12 ))
    phi 	= math.atan2( a23, a33 )

    return [phi, theta, psi]

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
 
    