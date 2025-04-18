import wiringpi
import time

# WiringPi Pin where ESC is connected
ESC_PIN = 2  # Update this if needed

# Setup
wiringpi.wiringPiSetup()
wiringpi.pinMode(ESC_PIN, 1)  # 1 = OUTPUT

def send_esc_pulse(pulse_width_us, duration_s):
    """
    Manually sends a PWM signal to the ESC.
    pulse_width_us: pulse width in microseconds (e.g. 1000 to 2000)
    duration_s: how long to keep sending the signal (in seconds)
    """
    print(f"Sending {pulse_width_us}µs pulses for {duration_s} seconds...")
    end_time = time.time() + duration_s
    while time.time() < end_time:
        wiringpi.digitalWrite(ESC_PIN, 1)
        wiringpi.delayMicroseconds(pulse_width_us)
        wiringpi.digitalWrite(ESC_PIN, 0)
        # Wait remaining time in the 20ms frame
        wiringpi.delayMicroseconds(20000 - pulse_width_us)

try:
    # Max throttle (2ms pulse)
    send_esc_pulse(2000, 5)

    # Min throttle (1ms pulse)
    send_esc_pulse(1000, 5)

    print("Done sending ESC signals.")

except KeyboardInterrupt:
    print("Interrupted by user. Stopping.")

finally:
    wiringpi.digitalWrite(ESC_PIN, 0)
    print("Pin set to LOW. Exiting.")

