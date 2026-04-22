import os

from datetime import datetime
from dotenv import load_dotenv

from imu import IMU
from servo import Servo
from gps import GPS
from file_manager import FileManager

load_dotenv()

now = datetime.now()

fileName = f"{now.strftime('%m.%d.%Y-%H:%M:%S')}.csv"
dirName = "./data/"
headers = ["Time", "Ax", "Ay", "Az", "Wx", "Wy", "Wz", "q0", "q1", "q2", "q3"]

f = FileManager(fileName, dirName, headers)

# imu = IMU(os.getenv("IMU_PORT"), os.getenv("IMU_BAUD"))
# imu.openDevice()

# s = Servo(os.getenv("SERVO_PORT"), os.getenv("SERVO_BAUD"), os.getenv("SERVO_1_ID"))
# s.turnMotorOn()

gps = GPS(os.getenv("GPS_PORT"), os.getenv("GPS_BAUD"))

try:
    while True:
        print(gps.readGPS())

except KeyboardInterrupt:
    print("Interupt")
