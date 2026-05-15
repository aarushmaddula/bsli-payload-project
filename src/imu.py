import logging
import struct

from serial import Serial
from serial import SerialException

READ = 0x03
WRITE = 0x06

class IMU:

  serialPort = None

  def __init__(self, port, baud, id):
        self.isOpen = False
        self.port = port
        self.baud = baud
        self.id = id

  def to_int16(self, hi, lo):
    return struct.unpack('<h', bytes([lo, hi]))[0]
  
  def to_int32(self, b3, b2, b1, b0):
    return struct.unpack('>i', struct.pack('>BBBB', b3, b2, b1, b0))[0]

  def modbus_crc(self, data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001  # reversed poly
            else:
                crc >>= 1
    return crc

  def write(self, functionCode, register, data):
    frame = bytes([
        self.id,
        functionCode,
        (register >> 8) & 0xFF,
        register & 0xFF,
        (data >> 8) & 0xFF,
        data & 0xFF
    ])

    crc = self.modbus_crc(frame)
    self.serialPort.write(frame + bytes([crc & 0xFF, (crc >> 8) & 0xFF]))

  def unlock(self):
    self.write(WRITE, 0x69, 0xB588)

  def save(self):
    self.write(WRITE, 0x00, 0x00)

  def calibrate(self, mode):
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
        mode (int):
            One of the calibration modes
      """
      self.unlock()
      self.write(WRITE, 0x01, mode)
      self.save()

  def set_bandwidth(self, bandwidth):
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
    self.write(WRITE, 0x1F, bandwidth)
    self.save()

  def set_baud(self, baud):
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
    self.write(WRITE, 0x04, baud)
    self.save()

    print("Changed Baud")
  
  def sleep(self):
    self.write(WRITE, 0x22, 0x01)

  def parse_time(self, data: list, pos: int):
    time = {}

    time["year"] = data[pos + 1]
    time["month"] = data[pos + 0]
    time["day"] = data[pos + 3]
    time["hour"] = data[pos + 2]
    time["minute"] = data[pos + 5]
    time["second"] = data[pos + 4]
    time["millisecond"] = self.to_int16(data[pos + 6], data[pos + 7])

    return time

  def parse_acceleration(self, data: list, pos: int):
    accel = {}

    accel["x"] = self.to_int16(data[pos], data[pos + 1]) / 32768 * 16 * 9.8
    accel["y"] = self.to_int16(data[pos + 2], data[pos + 3]) / 32768 * 16 * 9.8
    accel["z"] = self.to_int16(data[pos + 4], data[pos + 5]) / 32768 * 16 * 9.8

    return accel
  
  def parse_angular_velocity(self, data: list, pos: int):
    angularVelocity = {}

    angularVelocity["x"] = self.to_int16(data[pos], data[pos + 1]) / 32768 * 2000
    angularVelocity["y"] = self.to_int16(data[pos + 2], data[pos + 3]) / 32768 * 2000
    angularVelocity["z"] = self.to_int16(data[pos + 4], data[pos + 5]) / 32768 * 2000

    return angularVelocity
  
  def parse_magnetic_field(self, data: list, pos: int):
    magneticField = {}

    magneticField["x"] = self.to_int16(data[pos], data[pos + 1])
    magneticField["y"] = self.to_int16(data[pos + 2], data[pos + 3])
    magneticField["z"] = self.to_int16(data[pos + 4], data[pos + 5])

    return magneticField
  
  def parse_angle(self, data: list, pos: int):
    angle = {}

    angle["roll"]  = self.to_int32(data[pos], data[pos + 1], data[pos + 2], data[pos + 3]) / 1000
    angle["pitch"] = self.to_int32(data[pos + 4], data[pos + 5], data[pos + 6], data[pos + 7]) / 1000
    angle["yaw"]   = self.to_int32(data[pos + 8], data[pos + 9], data[pos + 10], data[pos + 11]) / 1000

    return angle
  
  def parse_quaternion(self, data: list, pos: int):
    quaternion = {}

    quaternion["0"] = self.to_int16(data[pos], data[pos + 1]) / 32768
    quaternion["1"] = self.to_int16(data[pos + 2], data[pos + 3]) / 32768
    quaternion["2"] = self.to_int16(data[pos + 4], data[pos + 5]) / 32768
    quaternion["3"] = self.to_int16(data[pos + 6], data[pos + 7]) / 32768

    return quaternion

  def read_sensor(self, register, length):
    self.write(READ, register, length)

    expected = 3 + length * 2 + 2
    response = self.serialPort.read(expected)

    if len(response) < expected:
        logging.warning(f"Short response: got {len(response)}/{expected} bytes")
        return []

    resp_id = response[0]
    resp_fc = response[1]

    if (resp_id != self.id or resp_fc != READ): 
        logging.warning(f"Bad header: id={resp_id:#x} fc={resp_fc:#x}")
        return []
    
    calc = self.modbus_crc(response[:-2])
    recv = response[-2] | (response[-1] << 8)
    if calc != recv:
        print(f"CRC mismatch: calc={calc:#06x} recv={recv:#06x}")
        return []

    data = {}

    raw = response[3 : 3 + length * 2]

    data["time"]             = self.parse_time(raw, 0)
    data["acceleration"]     = self.parse_acceleration(raw, 8)
    data["angular_velocity"] = self.parse_angular_velocity(raw, 14)
    data["magnetic_field"]   = self.parse_magnetic_field(raw, 20)
    data["angle"]            = self.parse_angle(raw, 26)
    data["temp"]             = self.to_int16(raw[38], raw[39]) / 100
    data["quaternion"]       = self.parse_quaternion(raw, 66)
    
    return data

  def read_data(self):
    return self.read_sensor(0x30, 0x25)

  def open_device(self):
    self.close_device()

    try:
      self.serialPort = Serial(self.port, self.baud, timeout=1.1)
      self.isOpen = True
    except SerialException as ex:
      print(ex)
        
  def close_device(self):
    if self.serialPort:
      self.sleep()
      self.serialPort.close()
    
    self.isOpen = False