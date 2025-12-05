from IMU import IMU
from datetime import datetime
import uuid
import time
from FileManager import FileManager

PORT = "/dev/ttyUSB0"
BAUD = 115200

arr = ["Time", "Ax", "Ay", "Az", "Roll", "Pitch", "Yaw"]

log = FileManager(str(uuid.uuid1()) + ".csv", "./data", arr)
imu = IMU(PORT, BAUD)

while 1:
    allFrames = imu.getOutputData()

    output = [None] * 8

    for frame in allFrames:
        match frame[1]:
            case 0x50:
                hour = frame[5]
                minute = frame[6]
                second = frame[7]

                ms = imu.to_int16(frame[8], frame[9])

                timeStr = hour * (3600 * 1000) + minute * (60 * 1000) + second * (1000) + ms
                output[0] = timeStr

            case 0x51:
                acc = frame

                ax = imu.to_int16(acc[2], acc[3]) / 32768 * 16
                ay = imu.to_int16(acc[4], acc[5]) / 32768 * 16
                az = imu.to_int16(acc[6], acc[7]) / 32768 * 16

                output[1:4] = [ax, ay, az]

            case 0x53:
                gyro = frame

                roll = imu.to_int16(gyro[2], gyro[3]) / 32768 * 180
                pitch = imu.to_int16(gyro[4], gyro[5]) / 32768 * 180
                yaw = imu.to_int16(gyro[6], gyro[7]) / 32768 * 180

                output[4:8] = [ax, ay, az]

    log.recordOutput(output)


    