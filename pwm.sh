#!/bin/bash

# This script allows you to control the duty cycle of PWM3 on Orange Pi Zero 3
# Set PWM period (50Hz)
PWM_PIN=2
PERIOD=20000000  # 50 Hz (20 ms period)

# Export the PWM pin if it's not already exported
if [ ! -e /sys/class/pwm/pwmchip0/pwm${PWM_PIN} ]; then
    echo ${PWM_PIN} > /sys/class/pwm/pwmchip0/export
    echo "PWM${PWM_PIN} exported."
fi

# Set the period for 50Hz (20ms) - Ensure it is in microseconds
echo ${PERIOD} > /sys/class/pwm/pwmchip0/pwm${PWM_PIN}/period
if [ $? -ne 0 ]; then
    echo "Failed to set period. Exiting..."
    exit 1
fi
echo "PWM${PWM_PIN} period set to ${PERIOD} (50Hz)."

# Enable the PWM pin (disabled by default)
echo 1 > /sys/class/pwm/pwmchip0/pwm${PWM_PIN}/enable
if [ $? -ne 0 ]; then
    echo "Failed to enable PWM. Exiting..."
    exit 1
fi
echo "PWM${PWM_PIN} enabled."

# Function to set the duty cycle
set_duty_cycle() {
    local duty=$1
    local duty_cycle=$((duty * PERIOD / 100))
    
    # Ensure the duty cycle value is valid and within the period range
    if [ ${duty_cycle} -gt ${PERIOD} ] || [ ${duty_cycle} -lt 0 ]; then
        echo "Invalid duty cycle value: ${duty_cycle}. It must be between 0 and ${PERIOD}."
        return 1
    fi
    
    # Set the duty cycle (in microseconds)
    echo ${duty_cycle} > /sys/class/pwm/pwmchip0/pwm${PWM_PIN}/duty_cycle
    if [ $? -ne 0 ]; then
        echo "Failed to set duty cycle. Exiting..."
        exit 1
    fi
    echo "PWM${PWM_PIN} duty cycle set to ${duty}% (${duty_cycle} microseconds)."
}

# Interactive loop to control duty cycle
echo "Enter a duty cycle between 0 and 100 (or 'q' to quit):"

while true; do
    read -p "Duty Cycle: " duty
    if [ "$duty" == "q" ]; then
        echo "Exiting. Disabling PWM${PWM_PIN}..."
        echo 0 > /sys/class/pwm/pwmchip0/pwm${PWM_PIN}/enable
        break
    fi

    # Validate input and set duty cycle
    if [[ "$duty" =~ ^[0-9]+$ ]] && [ "$duty" -ge 0 ] && [ "$duty" -le 100 ]; then
        set_duty_cycle $duty
    else
        echo "Invalid input. Please enter a number between 0 and 100."
    fi
done

