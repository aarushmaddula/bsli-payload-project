import serial
import time

class Servo:
    HEAD_BYTE = 0x3E

    def __init__(self, port: str, baud: int, id: int):
        self.deviceId = id
        self.ser = serial.Serial(port, baud, timeout=0.5)

    def checksum_ok(self, frame):
        return (sum(frame[:self.PACK_SIZE - 1]) & 0xFF) == frame[self.PACK_SIZE - 1]

    def calculateChecksum(self, data: list) -> int:
        return sum(data) & 0xFF

    def toTwoComplement(self, num: int, numBytes: int) -> list:
        return list(num.to_bytes(numBytes, byteorder="little", signed=True))

    def buildFrame(self, commandByte: int, data=None) -> list[int]:
        data = data or []

        frameCommand = [self.HEAD_BYTE, commandByte, self.deviceId, len(data)]
        frameCommand.append(self.calculateChecksum(frameCommand))

        frameData = []

        if data:
            frameData += data + [self.calculateChecksum(data)]

        return frameCommand + frameData

    def sendCommand(self, frame: list, recieveDataLength: int = 0) -> bytes:
        self.ser.write(bytes(frame))

        readBytes = 5
        if recieveDataLength > 0:
            readBytes += recieveDataLength + 1
        
        return self.ser.read(readBytes)

    def turnMotorOff(self) -> bytes:
        frame = self.buildFrame(0x80)
        return self.sendCommand(frame)

    def stopMotor(self) -> bytes:
        frame = self.buildFrame(0x81)
        return self.sendCommand(frame)

    def turnMotorOn(self) -> bytes:
        frame = self.buildFrame(0x88)
        return self.sendCommand(frame)

    def setTorque(self, torqueData: int) -> bytes:
        frame = self.buildFrame(0xA1, [torqueData & 0xFF, torqueData >> 8])
        return self.sendCommand(frame, 2)

    def setMultiLoopAngle(self, angle: int) -> bytes:
        frame = self.buildFrame(0xA3, self.toTwoComplement(angle, 8))
        return self.sendCommand(frame, 7)

    def setMultiLoopAngleSpeed(self, angle: int, maxSpeed: int) -> bytes:
        frame = self.buildFrame(0xA4, [*self.toTwoComplement(angle, 8), *self.toTwoComplement(maxSpeed, 4)])
        return self.sendCommand(frame, 7)
        
    def setSingleLoopAngle(self, angle: int, spinDirection: bool = 0x00) -> bytes:
        frame = self.buildFrame(0xA5, [spinDirection, angle & 0xFF, angle >> 8, 0x00])
        return self.sendCommand(frame, 7)
    
    def setIncrementAngle(self, angle) -> bytes:
        frame = self.buildFrame(0xA7, self.toTwoComplement(angle, 4))
        return self.sendCommand(frame, 8)

    def readSingleLoopAngle(self) -> bytes:
        frame = self.buildFrame(0x94)
        return self.sendCommand(frame, 4)

    def readMultiLoopAngle(self) -> bytes:
        frame = self.buildFrame(0x92)
        return self.sendCommand(frame, 8)
    
