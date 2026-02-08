from datetime import datetime
import numpy
import serial
import struct
import time
import math

PORT = "/dev/pts/4"
BAUD = 230400
DT = 0.005

ser = serial.Serial(PORT, BAUD)

def checksum(frame):
    return sum(frame) & 0xFF

def send_frame(frame_id, data, format):
  try:
    frame = bytearray()
    frame.append(0x55)
    frame.append(frame_id)
    frame += struct.pack(format, *data)
    frame.append(checksum(frame))
    ser.write(frame)
  except Exception as ex:
    print(str(data) + " | " + str(frame_id) + ": " + str(ex))

acc_noise = 0.05      # m/s^2
gyro_noise = 0.002    # rad/s

t = 0.0

while True:

    now = datetime.now()

    year = now.year
    month = now.month
    day = now.day
    hour = now.hour
    minute = now.minute
    second = now.second
    millisecond = int(now.microsecond / 1000)

    # ---- fake motion ----
    roll  = 20 * math.sin(t)
    pitch = 10 * math.cos(t)
    yaw   = ((t * 30) % 360) - 180

    gx = int(100 * math.sin(t))
    gy = int(50 * math.cos(t))
    gz = int(30)

    ax = int(16384 * math.sin(t))
    ay = 0
    az = 16384

    # ---- convert to raw ----

    tm = [
        year,
        month,
        day,
        hour,
        minute,
        second,
        millisecond & 0x0F,
        millisecond & 0xF0
    ]

    accel = [
        ax,
        ay,
        az,
        0
    ]

    gyro = [
        int(gx / 2000 * 32768),
        int(gy / 2000 * 32768),
        int(gz / 2000 * 32768),
        0
    ]

    angle = [
        int(roll  / 180 * 32768),
        int(pitch / 180 * 32768),
        int(yaw   / 180 * 32768),
        0
    ]

    send_frame(0x50, tm, "<HBBBBBBB")
    send_frame(0x51, accel, "<hhhh")
    send_frame(0x52, gyro, "<hhhh")
    send_frame(0x53, angle, "<hhhh")

    t += DT
    time.sleep(DT)
