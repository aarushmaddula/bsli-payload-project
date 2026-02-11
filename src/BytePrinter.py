import serial
import time

ser = serial.Serial('/dev/ttyUSB0', 230400, timeout=1)

def readFrame():
    """Read a single 11-byte IMU frame starting with 0x55."""
    
    while True:
        if ser.read(1) == b'\x55':
            break

    frame = ser.read(10)
    if len(frame) != 10:
        return None

    return b'\x55' + frame

def write(register, dataL, dataH):
    ser.write(bytes([0xFF, 0xAA, register, dataL, dataH]))

while True:
    b = ser.read(1)

    if b:
        print(f"{b[0]:02X}", end=" ")
   
