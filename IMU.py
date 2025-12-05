import struct
import serial
import time

class IMU:
  def __init__(self, port, baud):
      self.__ser = serial.Serial(port, baud, timeout=0.5)
      print("Initiated!")

  def write(self, register, dataL, dataH):
      self.__ser.write(bytes([0xFF, 0xAA, register, dataL, dataH]))

  def checksum_ok(self, frame):
    return (sum(frame[:10]) & 0xFF) == frame[10]

  def to_int16(self, lo, hi):
    return struct.unpack('<h', bytes([lo, hi]))[0]

  def unlock(self):
    self.write(0x69, 0x88, 0xB5)

  def save(self):
    self.write(0x00, 0x00, 0x00)

  def close(self):
     self.__ser.close()

  def calibrate(self, val):
      """
      Set calibration mode:
        0000(0x00): Normal working mode
        0001(0x01): Automatic accelerometer calibration
        0011(0x03): Height reset
        0100(0x04): Set the heading angle to zero
        0111(0x07): Magnetic Field Calibration (Spherical Fitting)
        1000 (0x08): Set the angle reference
        1001(0x09): Magnetic Field Calibration (Dual Plane Mode)
      
      Parameters:
        val (int):
            One of the calibration modes
      """
      self.unlock()
      self.write(0x01, val, 0x00)
      self.save()

  def configureOutputContent(self, hexL, hexH):
    """
    Configure which data types the IMU outputs in continuous stream.
    
    Bit Assignments (LSB → MSB):
      0: TIME      
      1: ACC       
      2: GYRO      
      3: ANGLE     
      4: MAG       
      5: PORT      
      6: PRESS     
      7: GPS       
      8: VELOCITY  
      9: QUATERNION
      10: GSA       
    
    Parameters:
      hexL (int):
          Low byte of the RSW bitmask (0-255)
      
      hexH (int):
          High byte of the RSW bitmask (0-255)
    """

    self.unlock()
    self.write(0x02, hexL, hexH)
    self.save()

  def setOutputRate(self, rate):
    """
    Set the IMU output rate (RRATE register).

    RRATE Assignments:
      0001(0x01): 0.2Hz
      0010(0x02): 0.5Hz
      0011(0x03): 1Hz
      0100(0x04): 2Hz
      0101(0x05): 5Hz
      0110(0x06): 10Hz
      0111(0x07): 20Hz
      1000(0x08): 50Hz
      1001(0x09): 100Hz
      1011(0x0B): 200Hz
      1011(0x0C): single return
      1100(0x0D): no return

    Parameters:
      rate (int): One of the RRATE values.      
    """
    self.unlock()
    self.write(0x03, rate, 0x00)
    self.save()

    time.sleep(5)
    print("Output Rate Changed!")

  def setBandwidth(self, bandwidth):
    """
    Set the IMU bandwidth.

    Bandwidth Assignments:
      0000(0x00): 256Hz
      0001(0x01): 188Hz
      0010(0x02): 98Hz
      0011(0x03): 42Hz
      0100(0x04): 20Hz
      0101(0x05): 10Hz
      0110(0x06): 5Hz

    Parameters:
      rate (int): One of the Bandwidth values.      
    """
    self.unlock()
    self.write(0x31, bandwidth, 0x00)
    self.save()

    time.sleep(5)
    print("Output Rate Changed!")

  def setBaud(self, baud):
    """
    Sets the Baud of the IMU.

    BAUD Assignments
      0001(0x01): 4800bps
      0010(0x02): 9600bps
      0011(0x03): 19200bps
      0100(0x04): 38400bps
      0101(0x05): 57600bps
      0110(0x06): 115200bps
      0111(0x07): 230400bps

    Parameter:
      baud (int): One of the BAUD values
    """
    self.unlock()
    self.write(0x04, baud, 0x00)
    self.save()

    print("Changed Baud")

  def readFrame(self):
    """Read a single 11-byte IMU frame starting with 0x55."""
    
    while True:
        if self.__ser.read(1) == b'\x55':
            break

    frame = self.__ser.read(10)
    if len(frame) != 10:
        return None

    return b'\x55' + frame

  def getOutputData(self):
    frame = self.readFrame()
    startingRegister = frame[1]

    result = [frame]
    
    frame = self.readFrame()   
    register = frame[1]
    
    while (register != startingRegister):
      result.append(frame)
      frame = self.readFrame()   
      register = frame[1]

    return result
            