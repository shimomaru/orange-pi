import wiringpi
import time
import threading

# List of WiringPi pins connected to ESCs
ESC_PINS = [2, 5, 7, 8]

# Setup
wiringpi.wiringPiSetup()
for pin in ESC_PINS:
    wiringpi.pinMode(pin, 1)  # Set each pin to OUTPUT

# Shared state
current_pulse_width = 1000
running = True

def pwm_loop():
    """Continuously send PWM signals to all ESCs with the current pulse width."""
    global current_pulse_width, running
    while running:
        for pin in ESC_PINS:
            wiringpi.digitalWrite(pin, 1)
        wiringpi.delayMicroseconds(current_pulse_width)
        for pin in ESC_PINS:
            wiringpi.digitalWrite(pin, 0)
        wiringpi.delayMicroseconds(20000 - current_pulse_width)

def input_loop():
    """Update the pulse width based on user input."""
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

def send_initial_pulse(pulse_width, duration):
    """Send initial calibration pulse to all ESCs for specified time."""
    end_time = time.time() + duration
    print(f"Sending {pulse_width}µs to all ESCs for {duration} seconds...")
    while time.time() < end_time:
        for pin in ESC_PINS:
            wiringpi.digitalWrite(pin, 1)
        wiringpi.delayMicroseconds(pulse_width)
        for pin in ESC_PINS:
            wiringpi.digitalWrite(pin, 0)
        wiringpi.delayMicroseconds(20000 - pulse_width)

try:
    # ESC Calibration steps
    send_initial_pulse(2000, 5)  # Max throttle
    send_initial_pulse(1000, 5)  # Min throttle

    # Start the continuous PWM thread and input thread
    pwm_thread = threading.Thread(target=pwm_loop, daemon=True)
    input_thread = threading.Thread(target=input_loop)

    pwm_thread.start()
    input_thread.start()

    input_thread.join()  # Wait until input loop exits

except KeyboardInterrupt:
    print("Interrupted by user. Stopping...")

finally:
    running = False
    time.sleep(0.1)  # Allow threads to stop cleanly
    for pin in ESC_PINS:
        wiringpi.digitalWrite(pin, 0)
    print("All ESC pins set to LOW. Exiting.")

