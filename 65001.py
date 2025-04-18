import spidev
import time
import numpy as np
from math import atan2, degrees

# === SPI SETUP ===
spi = spidev.SpiDev()
spi.open(0, 0)  # (bus 0, device 0) - Use SPI0 with CS0
spi.max_speed_hz = 1000000  # 1 MHz
spi.mode = 0b00

# === MPU-6500 REGISTERS ===
PWR_MGMT_1   = 0x6B
ACCEL_XOUT_H = 0x3B
WHO_AM_I     = 0x75
READ_FLAG    = 0x80

# === HELPER FUNCTIONS ===
def write_register(reg, value):
    spi.xfer2([reg, value])

def read_registers(start_addr, length):
    return spi.xfer2([start_addr | READ_FLAG] + [0x00] * length)[1:]

def combine_bytes(high, low):
    value = (high << 8) | low
    return value - 65536 if value > 32767 else value

# === INIT MPU ===
write_register(PWR_MGMT_1, 0x00)
time.sleep(0.1)

# === SENSOR READ FUNCTION ===
def read_sensor_data():
    data = read_registers(ACCEL_XOUT_H, 14)
    
    accel = np.array([
        combine_bytes(data[0], data[1]),
        combine_bytes(data[2], data[3]),
        combine_bytes(data[4], data[5])
    ]) / 16384.0  # Convert to g

    gyro = np.array([
        combine_bytes(data[8], data[9]),
        combine_bytes(data[10], data[11]),
        combine_bytes(data[12], data[13])
    ]) / 131.0  # Convert to °/s

    return accel, gyro

# === COMPLEMENTARY FILTER ===
def complementary_filter(accel, gyro, dt, last_angles):
    ax, ay, az = accel
    gx, gy, gz = gyro

    roll_gyro = last_angles[0] + gx * dt
    pitch_gyro = last_angles[1] + gy * dt

    roll_acc = degrees(atan2(ay, az))
    pitch_acc = degrees(atan2(-ax, np.sqrt(ay**2 + az**2)))

    alpha = 0.96
    roll = alpha * roll_gyro + (1 - alpha) * roll_acc
    pitch = alpha * pitch_gyro + (1 - alpha) * pitch_acc

    return (roll, pitch)

# === MAIN LOOP ===
last_angles = (0.0, 0.0)
yaw = 0.0
last_time = time.time()

try:
    while True:
        accel, gyro = read_sensor_data()
        now = time.time()
        dt = now - last_time
        last_time = now

        # Compute roll and pitch with complementary filter
        roll, pitch = complementary_filter(accel, gyro, dt, last_angles)
        last_angles = (roll, pitch)

        # Integrate gyro Z for relative yaw
        yaw += gyro[2] * dt  # gz * delta time

        print(f"Roll: {roll:.2f}°, Pitch: {pitch:.2f}°, Yaw (relative): {yaw:.2f}°")
        time.sleep(0.01)

except KeyboardInterrupt:
    spi.close()
    print("\nExiting cleanly.")

