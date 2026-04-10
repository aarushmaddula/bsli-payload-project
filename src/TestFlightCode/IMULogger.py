import os
import time
import numpy as np

from datetime import datetime
from dotenv import load_dotenv

from IMU import IMU
from FileManager import FileManager

load_dotenv()

# Creates the csv file for logging
now = datetime.now()

fileName = f"{now.strftime('%m.%d.%Y-%H.%M.%S')}.csv"
dirName = "./src/TestFlightCode/data/"
headers = ["Time", "Ax", "Ay", "Az", "Wx", "Wy", "Wz", "q0", "q1", "q2", "q3"]

f = FileManager(fileName, dirName, headers)

# Turns on the IMU
imu = IMU(os.getenv("IMU_PORT"), os.getenv("IMU_BAUD"))
imu.openDevice()

# Settings for calibration trigger
STATIONARY_WINDOW = 50        # Last number of accel data points to keep track of 
STATIONARY_THRESHOLD=0.15     # The threshold of the std of accel until the imu is considered moving 
STATIONARY_TIME = 30.0        # Stationary Time required to trigger a calibration
LAUNCH_THRESHOLD = 10.0        # G-force required to detect launch

accelBuffer = []
lastMovementTime = time.time()
movedSinceCalibration = True

rocketLaunched = False

while True:
  try:
    data = imu.getOutputData()

    if (len(data) == 0):
       continue
    
    f.recordOutput(data)

    if rocketLaunched: 
      continue

    # The first data output lacks acceleration data for some reason.
    if "ax" not in data:
      continue
    
    ax, ay, az = data["ax"], data["ay"], data["az"]

    # Checks if rocket has been launched
    totalAccel = np.sqrt(ax**2 + ay**2 + az**2)

    if totalAccel > LAUNCH_THRESHOLD:
      rocketLaunched = True
      accelBuffer.clear()
      print("Launch detected! Disabling calibration...")
      continue

    accelBuffer.append((ax, ay, az))
    
    if len(accelBuffer) > STATIONARY_WINDOW:
      accelBuffer.pop(0)

    if len(accelBuffer) == STATIONARY_WINDOW:
        arr = np.array(accelBuffer)
        std = np.std(arr, axis=0)

        isStationary = all(s < STATIONARY_THRESHOLD for s in std)

        if not isStationary:
            lastMovementTime = time.time()
            movedSinceCalibration = True
            print("IMU moving", std)

        timeStationary = time.time() - lastMovementTime

        if isStationary and timeStationary >= STATIONARY_TIME and movedSinceCalibration:
            print("IMU stationary! Recalibrating...")
            imu.calibrate(0x01)
            time.sleep(5)
            imu.calibrate(0x08)
            lastMovementTime = time.time()
            movedSinceCalibration = False
            accelBuffer.clear()
            print("Recalibration complete.")

  except KeyboardInterrupt:
    print("Length of queue:", imu.framePackageBuffer.qsize())
    imu.closeDevice()
    f.close()
    break

  except Exception as e:
    print("An error has occured: ", e)


