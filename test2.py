import wiringpi
import time

# Setup
ESC_PIN = 2  # WiringPi pin 2
wiringpi.wiringPiSetup()  # Initialize WiringPi
wiringpi.softPwmCreate(ESC_PIN, 0, 100)  # pin, initial value, range (0–100)

def esc_write(value):
    """
    Write a PWM value to the ESC.
    5% = ~1ms pulse (stop)
    10% = ~2ms pulse (full throttle)
    Adjust depending on your ESC
    """
    pwm_val = max(5, min(10, value))  # constrain between 5% and 10%
    wiringpi.softPwmWrite(ESC_PIN, int(pwm_val))

# Arming sequence (typical for hobby ESCs)
print("Starting now")
time.sleep(5)
print("Arming ESC...")
esc_write(10)
time.sleep(4)  # Minimum throttle for 2 seconds
esc_write(5)
print("5% sent")
time.sleep(5)

# Ramp up
print("Throttle up")
for val in range(5, 11):
    esc_write(val)
    print(f"PWM: {val}%")
    time.sleep(0.5)

# Hold full
time.sleep(2)

# Ramp down
print("Throttle down")
for val in reversed(range(5, 11)):
    esc_write(val)
    print(f"PWM: {val}%")
    time.sleep(0.5)

# Stop
esc_write(5)
print("ESC stopped")

