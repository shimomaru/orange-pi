import spidev
import smbus2
import time
import math
import numpy as np

# --------- MPU6500 (SPI) SETUP ---------
spi = spidev.SpiDev()
spi.open(1, 1)  # bus 0, device 0
spi.max_speed_hz = 1000000

MPU6500_ADDR = 0x68
MPU_PWR_MGMT_1 = 0x6B

def spi_write(reg, value):
    spi.xfer2([reg & 0x7F, value])

def spi_read(reg):
    resp = spi.xfer2([reg | 0x80, 0x00])
    return resp[1]

def spi_read_bytes(reg, length):
    return spi.xfer2([reg | 0x80] + [0x00]*length)[1:]

def mpu6500_setup():
    spi_write(MPU_PWR_MGMT_1, 0x00)  # Wake up sensor
    time.sleep(0.1)

def read_mpu6500():
    data = spi_read_bytes(0x3B, 14)
    accel = [int.from_bytes(data[i:i+2], 'big', signed=True) for i in range(0, 6, 2)]
    temp  = int.from_bytes(data[6:8], 'big', signed=True)
    gyro  = [int.from_bytes(data[i:i+2], 'big', signed=True) for i in range(8, 14, 2)]
    return accel, gyro

# --------- QMC5883L (I2C) SETUP ---------
I2C_ADDR = 0x0D
bus = smbus2.SMBus(3)

def qmc5883l_setup():
    bus.write_byte_data(I2C_ADDR, 0x0B, 0x01)
    time.sleep(0.1)
    bus.write_byte_data(I2C_ADDR, 0x09, 0x1D)  # Continuous mode

def read_qmc5883l():
    data = bus.read_i2c_block_data(I2C_ADDR, 0x00, 6)
    x = data[1] << 8 | data[0]
    y = data[3] << 8 | data[2]
    z = data[5] << 8 | data[4]
    if x >= 32768: x -= 65536
    if y >= 32768: y -= 65536
    if z >= 32768: z -= 65536
    return x, y, z

# --------- Orientation Calculation ---------
def calculate_orientation(accel, gyro, mag, dt, prev_angle):
    ax, ay, az = [a / 16384.0 for a in accel]  # assuming ±2g
    gx, gy, gz = [g / 131.0 for g in gyro]     # assuming ±250°/s

    # Accelerometer angle (pitch and roll)
    pitch_acc = math.atan2(-ax, math.sqrt(ay**2 + az**2)) * 180 / math.pi
    roll_acc  = math.atan2(ay, az) * 180 / math.pi

    # Complementary filter
    alpha = 0.98
    pitch = alpha * (prev_angle['pitch'] + gy * dt) + (1 - alpha) * pitch_acc
    roll  = alpha * (prev_angle['roll'] + gx * dt) + (1 - alpha) * roll_acc

    # Tilt-compensated magnetometer for yaw
    mx, my, mz = mag
    mx, my, mz = mx / 3000.0, my / 3000.0, mz / 3000.0  # normalize

    pitch_rad = math.radians(pitch)
    roll_rad = math.radians(roll)

    xh = mx * math.cos(pitch_rad) + mz * math.sin(pitch_rad)
    yh = mx * math.sin(roll_rad) * math.sin(pitch_rad) + my * math.cos(roll_rad) - mz * math.sin(roll_rad) * math.cos(pitch_rad)
    yaw = math.degrees(math.atan2(yh, xh))
    if yaw < 0:
        yaw += 360

    return {'pitch': pitch, 'roll': roll, 'yaw': yaw}

# --------- Main Loop ---------
mpu6500_setup()
qmc5883l_setup()

angle = {'pitch': 0, 'roll': 0, 'yaw': 0}
last_time = time.time()

print("Starting IMU loop...")
while True:
    try:
        now = time.time()
        dt = now - last_time
        last_time = now

        accel, gyro = read_mpu6500()
        mag = read_qmc5883l()

        angle = calculate_orientation(accel, gyro, mag, dt, angle)

        print(f"Pitch: {angle['pitch']:.2f}°, Roll: {angle['roll']:.2f}°, Yaw: {angle['yaw']:.2f}°")
        time.sleep(0.05)

    except KeyboardInterrupt:
        print("Exiting...")
        break

