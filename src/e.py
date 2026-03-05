import time
import Servo

s = Servo.Servo("/dev/ttyUSB1", 115200, 1)

print(s.turnMotorOn().hex(" "))
print(s.setMultiLoopAngle(-180).hex(" "))
print(s.readMultiLoopAngle().hex(" "))
print(s.turnMotorOff().hex(" "))

# print(bytes(frame).hex(" "))
