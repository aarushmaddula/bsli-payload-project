import struct

class Registers:
    TIME = 0x50
    ACCEL = 0x51
    ANG = 0x52
    GYRO = 0x53
    MAG = 0x54
    QUAT = 0x59
    READ = 0x5F

class ProtocolProcessor:

  def __init__(self, size):
    self.tempBytes = []
    self.tempData = {}
    self.PACK_SIZE = size
    self.previousRegister = None

  def checksum_ok(self, frame):
    return (sum(frame[:self.PACK_SIZE - 1]) & 0xFF) == frame[self.PACK_SIZE - 1]

  def to_int16(self, lo, hi):
    return struct.unpack('<h', bytes([lo, hi]))[0]

  def processData(self, data):
    framePackages = []

    for val in data:
      self.tempBytes.append(val)
            
      if (self.tempBytes[0] != 0x55):                   
        del self.tempBytes[0]                       
        continue

      if (len(self.tempBytes) > 1):
        isValidRegister = (0x50 <= self.tempBytes[1] and self.tempBytes[1] <= 0x5B) or self.tempBytes[1] == 0x5F

        if (not isValidRegister):  
          del self.tempBytes[0]                   
          continue

      if (len(self.tempBytes) == self.PACK_SIZE):      
        if (self.checksum_ok(self.tempBytes[0:self.PACK_SIZE])):  
          
          frameData = {}
          register = self.tempBytes[1]

          match register:
            case Registers.TIME:
              frameData = self.getTime(self.tempBytes)
            case Registers.ACCEL:
              frameData = self.getAccel(self.tempBytes)
            case Registers.ANG:
              frameData = self.getAng(self.tempBytes)
            case Registers.GYRO:
              frameData = self.getGyro(self.tempBytes)
            case Registers.MAG:
              frameData = self.getMag(self.tempBytes)
            case Registers.QUAT:
              frameData = self.getQuat(self.tempBytes)
            case Registers.READ:
              frameData = self.getRead(self.tempBytes)              

          if (self.previousRegister is not None and register <= self.previousRegister): 
            framePackages.append(self.tempData.copy())
            self.tempData.clear()
          
          self.tempData.update(frameData)
          self.previousRegister = register
          self.tempBytes.clear()
          
        else: 
          del self.tempBytes[0]    

    return framePackages               

  def getTime(self, data):
    returnData = {}

    returnData["year"] = data[2]
    returnData["month"] = data[3]
    returnData["day"] = data[4]
    returnData["hour"] = data[5]
    returnData["minute"] = data[6]
    returnData["second"] = data[7]
    returnData["millisecond"] = self.to_int16(data[8], data[9])
    
    return returnData
  
  def getAccel(self, data):
    returnData = {}

    returnData["ax"] = self.to_int16(data[2], data[3]) / 32768 * 16
    returnData["ay"] = self.to_int16(data[4], data[5]) / 32768 * 16
    returnData["az"] = self.to_int16(data[6], data[7]) / 32768 * 16
    returnData["temp"] = self.to_int16(data[8], data[9]) / 100
    
    return returnData
  
  def getAng(self, data):
    returnData = {}

    returnData["wx"] = self.to_int16(data[2], data[3]) / 32768 * 2000
    returnData["wy"] = self.to_int16(data[4], data[5]) / 32768 * 2000
    returnData["wz"] = self.to_int16(data[6], data[7]) / 32768 * 2000
    returnData["voltage"] = self.to_int16(data[8], data[9]) / 100  
    
    return returnData
  
  def getGyro(self, data):
    returnData = {}
    
    returnData["roll"] = self.to_int16(data[2], data[3]) / 32768 * 180
    returnData["pitch"] = self.to_int16(data[4], data[5]) / 32768 * 180
    returnData["yaw"] = self.to_int16(data[6], data[7]) / 32768 * 180
    returnData["version"] = self.to_int16(data[8], data[9]) 
    
    return returnData
  
  def getMag(self, data):
    returnData = {}

    returnData["hx"] = self.to_int16(data[2], data[3])
    returnData["hy"] = self.to_int16(data[4], data[5])
    returnData["hz"] = self.to_int16(data[6], data[7])
    returnData["temp"] = self.to_int16(data[8], data[9]) / 100

    return returnData
  
  def getQuat(self, data):
    returnData = {}

    returnData["q0"] = self.to_int16(data[2], data[3]) / 32768
    returnData["q1"] = self.to_int16(data[4], data[5]) / 32768
    returnData["q2"] = self.to_int16(data[6], data[7]) / 32768
    returnData["q3"] = self.to_int16(data[8], data[9]) / 32768
    
    return returnData
  
  def getRead(self, data):
    returnData = {}

    returnData["v1"] = self.to_int16(data[2], data[3])
    returnData["v2"] = self.to_int16(data[4], data[5])
    returnData["v3"] = self.to_int16(data[6], data[7])
    returnData["v4"] = self.to_int16(data[8], data[9])
    
    return returnData


  
