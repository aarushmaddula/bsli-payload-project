import math
import time

from datetime import datetime
import dotenv
import numpy as np
import struct
import random

from IMU import IMU
from Servo import Servo
from LaserVectorCalculator import calculateLaserVector
from FileManager import FileManager

now = datetime.now()

fileName = f"{now.strftime("%m.%d.%Y-%H:%M:%S")}.csv"
dirName = "./data/"
headers = ["Time", "Ax", "Ay", "Az", "Wx", "Wy", "Wz", "q0", "q1", "q2", "q3"]

f = FileManager(fileName, dirName, headers)

imu = IMU("/dev/ttyUSB0", 230400)
imu.openDevice()

s = Servo("/dev/ttyUSB1", 115200, 1)
s.turnMotorOn()

# a = 0

while True:
    data = imu.getOutputData()

    a = int((data.get("yaw", 0) + 180) * 100)

    
    bites = s.readMultiLoopAngle()    
    b = struct.unpack('<i', bites[5:9])[0]

    rots = b // 36000

    diff = (b - a + 18000) % 36000 - 18000
    angle = b - diff

    print(a, "\t", b, "\t", rots,"\t", diff, "\t", angle)

    # s.setSingleLoopAngle(a, 0x01 if diff > 0 else 0x00)
    s.setMultiLoopAngle(angle)

    # a += int(np.random.normal(loc=0, scale=1000))
    # a %= 36000

    # time.sleep(0.1)

    # f.recordOutput(data)
    
    # d2r = math.pi/180
    # r2d = 180/math.pi

    # encoder_z = 0*d2r
    # encoder_a = 0*d2r

    # encoderData = np.array([encoder_z, encoder_a])

    # q0 = data.get("q0", "None")
    # q1 = data.get("q1", "None")
    # q2 = data.get("q2", "None")
    # q3 = data.get("q3", "None")

    # quatIMU = np.array([q0, q1, q2, q3])
    
    # e = calculateLaserVector(encoderData, quatIMU)
    


