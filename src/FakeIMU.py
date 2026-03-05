import time
import math

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import numpy as np
import serial
import struct

acc_noise = 0.05
gyro_noise = 0.002

class FakeIMU:
    DT = 0.005

    def __init__(self, port, BAUD) -> None:
        self.ser = serial.Serial(port, BAUD)

    def getBaud(self) -> int:
        return self.ser.baudrate

    def checksum(self, frame: list) -> int:
        return sum(frame) & 0xFF

    def generateTime(self, t) -> list:
        start = datetime(2000, 1, 1)
        end = start + timedelta(seconds=t)

        diff = relativedelta(end, start)

        return [
            diff.years,
            diff.months,
            diff.days,
            diff.hours,
            diff.minutes,
            diff.seconds, 
            diff.microseconds & 0x0F,
            diff.microseconds & 0xF0
        ]

    def generateAngle(self, t: int) -> list:
        roll = 20 * math.sin(t)
        pitch = 10 * math.cos(t)
        yaw = ((t * 30) % 360) - 180

        return [
            int(roll / 180 * 32768),
            int(pitch / 180 * 32768),
            int(yaw / 180 * 32768),
            0,
        ]

    def generateGyro(self, t: int) -> list:
        gx = int(100 * math.sin(t))
        gy = int(50 * math.cos(t))
        gz = int(30)

        return [
            int(gx / 2000 * 32768),
            int(gy / 2000 * 32768),
            int(gz / 2000 * 32768),
            0,
        ]

    def generateAccel(self, t: int) -> list:
        ax = int(16384 * math.sin(t))
        ay = 0
        az = 16384

        return [ax, ay, az, 0]
    
    def generateMag(self, t: int) -> list:
        v = np.random.randn(4)
        v /= np.linalg.norm(v)
        return [0, 0, 0, 0]
    
    def generateQuat(self, t: int) -> list:
        cy = math.cos(t * 0.5)
        sy = math.sin(t * 0.5)
        cp = math.cos(t * 0.5)
        sp = math.sin(t * 0.5)
        cr = math.cos(t * 0.5)
        sr = math.sin(t * 0.5)

        w = cr * cp * cy + sr * sp * sy
        x = sr * cp * cy - cr * sp * sy
        y = cr * sp * cy + sr * cp * sy
        z = cr * cp * sy - sr * sp * cy

        return [
            int(w * 32767), 
            int(x * 32767), 
            int(y * 32767), 
            int(z * 32767)
        ]

    def sendFrame(self, frame_id, data, format):
        try:
            frame = bytearray()
            frame.append(0x55)
            frame.append(frame_id)
            frame += struct.pack(format, *data)
            frame.append(self.checksum(frame))
            self.ser.write(frame)
        except Exception as ex:
            print(str(data) + " | " + str(frame_id) + ": " + str(ex))

    def processData(self):
        t = 0.0

        while True:
            print(self.generateTime(t), self.DT, t)

            self.sendFrame(0x50, self.generateTime(t), "<HBBBBBBB")
            self.sendFrame(0x51, self.generateAccel(t), "<hhhh")
            self.sendFrame(0x52, self.generateGyro(t), "<hhhh")
            self.sendFrame(0x53, self.generateAngle(t), "<hhhh")
            self.sendFrame(0x54, self.generateMag(t), "<hhhh")
            self.sendFrame(0x59, self.generateQuat(t), "<hhhh")
            

            t += self.DT
            time.sleep(self.DT)

if __name__ == "__main__":
    imu = FakeIMU("/dev/pts/2", 230400)
    imu.processData()