import os

from datetime import datetime
from dotenv import load_dotenv

from IMU import IMU
from FileManager import FileManager

load_dotenv()

now = datetime.now()

fileName = f"{now.strftime('%m.%d.%Y-%H:%M:%S')}.csv"
dirName = "./data/"
headers = ["Time", "Ax", "Ay", "Az", "Wx", "Wy", "Wz", "q0", "q1", "q2", "q3"]

f = FileManager(fileName, dirName, headers)

imu = IMU(os.getenv("IMU_PORT"), os.getenv("IMU_BAUD"))
imu.openDevice()

try:
  while True:
    data = imu.getOutputData()
    if (len(data) > 0):
      f.recordOutput(data)
      
except KeyboardInterrupt:
  imu.closeDevice()

