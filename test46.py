import wiringpi
import time
import threading

# WiringPi Pin where ESC is connected
ESC_PIN = 2  # Update this if needed

# Setup
wiringpi.wiringPiSetup()
wiringpi.pinMode(ESC_PIN, 1)  # 1 = OUTPUT

# Shared variable for pulse width
current_pulse_width = 1000
running = True

def pwm_loop():
    """Continuously send PWM signal with the current pulse width."""
    global current_pulse_width, running
    while running:
        wiringpi.digitalWrite(ESC_PIN, 1)
        wiringpi.delayMicroseconds(current_pulse_width)
        wiringpi.digitalWrite(ESC_PIN, 0)
        wiringpi.delayMicroseconds(20000 - current_pulse_width)

def input_loop():
    """Listen for user input and update pulse width."""
    global current_pulse_width, running
    print("Enter pulse width (1000–2000µs), or 'exit' to quit:")
    while running:
        user_input = input("> ")
        if user_input.lower() == "exit":
            running = False
            break
        try:
            pulse = int(user_input)
            if 1000 <= pulse <= 2000:
                current_pulse_width = pulse
                print(f"Updated pulse width to {pulse}µs.")
            else:
                print("Please enter a value between 1000 and 2000.")
        except ValueError:
            print("Invalid input. Please enter a number between 1000 and 2000, or 'exit'.")

try:
    # Start with max and min throttle for calibration
    print("Sending 2000µs signal for 5 seconds...")
    end_time = time.time() + 5
    while time.time() < end_time:
        wiringpi.digitalWrite(ESC_PIN, 1)
        wiringpi.delayMicroseconds(2000)
        wiringpi.digitalWrite(ESC_PIN, 0)
        wiringpi.delayMicroseconds(20000 - 2000)

    print("Sending 1000µs signal for 5 seconds...")
    end_time = time.time() + 5
    while time.time() < end_time:
        wiringpi.digitalWrite(ESC_PIN, 1)
        wiringpi.delayMicroseconds(1000)
        wiringpi.digitalWrite(ESC_PIN, 0)
        wiringpi.delayMicroseconds(20000 - 1000)

    # Start PWM and input threads
    pwm_thread = threading.Thread(target=pwm_loop, daemon=True)
    input_thread = threading.Thread(target=input_loop)

    pwm_thread.start()
    input_thread.start()

    input_thread.join()  # Wait for input thread to finish

except KeyboardInterrupt:
    print("Interrupted by user. Stopping.")

finally:
    running = False
    time.sleep(0.1)  # Small delay to ensure thread stops
    wiringpi.digitalWrite(ESC_PIN, 0)
    print("Pin set to LOW. Exiting.")

