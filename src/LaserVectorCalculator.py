import numpy as np
from numpy import linalg as la
import math

d2r = math.pi/180
r2d = 180/math.pi

def quat2DCM(q):
  q1 = q[1]
  q2 = q[2]
  q3 = q[3]
  q4 = q[4] 
    
  a11 = q1^2 - q2^2 - q3^2 + q4^2
  a12 = 2 * ( q1 * q2 + q3 * q4 )
  a13 = 2 * ( q1 * q3 - q2 * q4 )
  a21 = 2 * ( q1 * q2 - q3 * q4 )
  a22 = q2^2 - q1^2 - q3^2 + q4^2
  a23 = 2 * ( q2 * q3 + q1 * q4 )
  a31 = 2 * ( q1 * q3 + q2 * q4 )
  a32 = 2 * ( q2 * q3 - q1 * q4 )
  a33 = q3^2 - q1^2 - q2^2 + q4^2

  return [[a11, a12, a13], 
          [a21, a22, a23],
          [a31, a32, a33]]

def multiplyquat(q1, q2):
  w1 = q1[0]
  x1 = q1[1]
  y1 = q1[2]
  z1 = q1[3]
  
  w2 = q2[0] 
  x2 = q2[1] 
  y2 = q2[2] 
  z2 = q2[3]
  
  w = w1*w2 - x1*x2 - y1*y2 - z1*z2
  x = w1*x2 + x1*w2 + y1*z2 - z1*y2
  y = w1*y2 - x1*z2 + y1*w2 + z1*x2
  z = w1*z2 + x1*y2 - y1*x2 + z1*w2
  
  return np.array([w, x, y, z])

def calcEncoderQuat(encoder_z, encoder_a):
  qz = np.array([[math.cos(encoder_z/2)], [0], [0], [math.sin(encoder_z/2)]])
  qx = np.array([[math.cos(encoder_a/2)], [math.sin(encoder_a/2)], [0], [0]])

  return multiplyquat(qz, qx)

def calcPointVector(quatEncoder, quatIMU):
  invQuatEncoder = np.concatenate(([[quatEncoder[0]], -quatEncoder[1:4]]), axis=0)
  invQuatIMU = np.concatenate(([[quatIMU[0]], -quatIMU[1:4]]), axis=0)

  initQuat = np.array([[0], [0], [0], [-1]])

  bodyVector = multiplyquat(multiplyquat(quatEncoder, initQuat), invQuatEncoder)
  pointingQuat = multiplyquat(multiplyquat(invQuatIMU, bodyVector), quatIMU)
    
  return pointingQuat[1:]

def eul2quat(psi, theta, phi):
  c1 = math.cos(psi/2)
  c2 = math.cos(theta/2) 
  c3 = math.cos(phi/2);  

  s1 = math.sin(psi/2)
  s2 = math.sin(theta/2)
  s3 = math.sin(phi/2)     

  q0 = c1*c2*c3 + s1*s2*s3
  q1 = c1*c2*s3 - s1*s2*c3
  q2 = c1*s2*c3 + s1*c2*s3
  q3 = s1*c2*c3 - c1*s2*s3

  return np.array([[q0], [q1], [q2], [q3]])


def calculateLaserVector(encoderData, quatIMU):

  encoder_z = encoderData[0]
  encoder_a = encoderData[1]

  quatIMUUnit = quatIMU / la.norm(quatIMU)

  quatEncoder = calcEncoderQuat(encoder_z, encoder_a)
  quatEncoderUnit = quatEncoder / la.norm(quatEncoder)

  return calcPointVector(quatEncoderUnit, quatIMUUnit)


def calculateLaserVectorTest(encoderData, imuData):
  encoder_z = encoderData[0]
  encoder_a = encoderData[1]

  imu_x = imuData[0];  
  imu_y = imuData[1];   
  imu_z = imuData[2];   
  
  quatIMU = eul2quat(imu_z, imu_y, imu_x)
  quatIMUUnit = quatIMU / la.norm(quatIMU)

  quatEncoder = calcEncoderQuat(encoder_z, encoder_a)
  quatEncoderUnit = quatEncoder / la.norm(quatEncoder)

  return calcPointVector(quatEncoderUnit, quatIMUUnit)
