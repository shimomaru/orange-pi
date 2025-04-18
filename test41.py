import wiringpi
import time

PIN = 3  # WiringPi pin number

wiringpi.wiringPiSetup()
wiringpi.pinMode(PIN, 1)  # 1 = OUTPUT

print("Toggling pin HIGH for 1ms, then LOW")
wiringpi.digitalWrite(PIN, 1)
wiringpi.delayMicroseconds(1000)
wiringpi.digitalWrite(PIN, 0)

