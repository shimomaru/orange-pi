import time
from pyA20 import GPIO
from pyA20 import pwm

# Setup
ESC_PIN = GPIO.PC9  # Pin PA18 corresponds to PWM on Orange Pi Zero 3
GPIO.init()  # Initialize GPIO
pwm.start(ESC_PIN, 0)  # Start PWM with 0% duty cycle

# Set PWM frequency to 50 Hz (typical for ESCs)
PWM_FREQ = 50
pwm.set_pwm_freq(ESC_PIN, PWM_FREQ)

def esc_write(value):
    pwm_val = max(1, min(100, value))  # Constrain value to 1–100%
    duty_cycle = (pwm_val / 100.0) * 100  # Convert percentage to duty cycle
    pwm.set_duty_cycle(ESC_PIN, duty_cycle)
    print(f"Set PWM to {pwm_val}%")

# Arming sequence
print("Arming ESC...")
esc_write(1)  # Minimum throttle for arming
time.sleep(2)  # Minimum throttle for 2 seconds

# Interactive loop
print("Enter a duty cycle between 1 and 100 (or 'q' to quit):")

while True:
    user_input = input("Duty Cycle %: ").strip()
    
    if user_input.lower() == 'q':
        print("Exiting. Setting throttle to minimum...")
        esc_write(1)
        break

    try:
        duty = float(user_input)
        if 1 <= duty <= 100:
            esc_write(duty)
            print(f"Set PWM to {duty}%")
        else:
            print("Please enter a value between 1 and 100.")
    except ValueError:
        print("Invalid input. Enter a number between 1 and 100, or 'q' to quit.")

