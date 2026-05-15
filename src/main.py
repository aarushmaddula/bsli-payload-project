import os

from datetime import datetime
from dotenv import load_dotenv

from imu import IMU
from servo import Servo
from gps import GPS
from file_manager import FileManager

load_dotenv()

# imu = IMU(os.getenv("IMU_PORT"), int(os.getenv("IMU_BAUD")), int(os.getenv("IMU_ID")))
# imu.open_device()

# s = Servo(os.getenv("SERVO_PORT"), os.getenv("SERVO_BAUD"), os.getenv("SERVO_1_ID"))
# s.turnMotorOn()

gps = GPS(os.getenv("GPS_PORT"), os.getenv("GPS_BAUD"))

try:
    while True:
        print(gps.readGPS())

except KeyboardInterrupt:
    print("Interupt")
