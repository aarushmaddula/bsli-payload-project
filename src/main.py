import math
import time
import os

from datetime import datetime
from dotenv import load_dotenv
import numpy as np
import struct
import random

from IMU import IMU
from Servo import Servo
from LaserVectorCalculator import calculateLaserVector
from FileManager import FileManager

load_dotenv()

now = datetime.now()

fileName = f"{now.strftime('%m.%d.%Y-%H:%M:%S')}.csv"
dirName = "./data/"
headers = ["Time", "Ax", "Ay", "Az", "Wx", "Wy", "Wz", "q0", "q1", "q2", "q3"]

f = FileManager(fileName, dirName, headers)

imu = IMU(os.getenv("IMU_PORT"), os.getenv("IMU_BAUD"))
imu.openDevice()

s = Servo(os.getenv("SERVO_PORT"), os.getenv("SERVO_BAUD"), os.getenv("SERVO_1_ID"))
s.turnMotorOn()

def testQuat1():
    data = imu.getOutputData()

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

a = 0
def testMotor1(a):
    data = imu.getOutputData()

    # a = int((data.get("yaw", 0) + 180) * 100)

    bites = s.readMultiLoopAngle()
    b = struct.unpack("<i", bites[5:9])[0]

    diff = (b - a + 18000) % 36000 - 18000
    angle = b - diff
    print(a, "\t", b, "\t", diff, "\t", angle, "\t", bites.hex(" "))

    s.setMultiLoopAngle(a)

    a += int(np.random.normal(loc=0, scale=1000))
    a %= 36000

    time.sleep(0.1)

lastAngle = 0

try:
    while True:
        data = imu.getOutputData()

        # a = int((data.get("yaw", 0) + 180) * 100)

        bites = s.readMultiLoopAngle()
        b = struct.unpack("<i", bites[5:9])[0]

        diff = (b - a + 18000) % 36000 - 18000
        angle = b - diff

        if abs(lastAngle - b) > 36000:
            print(a, "\t", b, "\t", diff, "\t", angle, "\t", bites.hex(" "))

        lastAngle = b

        s.setMultiLoopAngle(angle)

        a += int(np.random.normal(loc=0, scale=1000))
        a %= 36000

        time.sleep(0.1)

except KeyboardInterrupt:
    s.turnMotorOff()
