import numpy as np
from numpy import linalg as la
import math

from LaserVectorCalculator import calculateLaserVectorTest

d2r = math.pi/180
r2d = 180/math.pi

encoder_z = 0*d2r
encoder_a = 0*d2r

encoderData = np.array([encoder_z, encoder_a])

imu_x = 90*d2r;  
imu_y = 0*d2r;   
imu_z = 0*d2r;   

imuData = np.array([imu_x, imu_y, imu_z])

e = calculateLaserVectorTest(encoderData, imuData)

print(e)