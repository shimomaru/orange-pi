import smbus2
import time
import math

DEVICE_ADDRESS = 0x0D  # QMC5883L default I2C address
bus = smbus2.SMBus(3)

def setup():
    # Set to continuous measurement mode
    bus.write_byte_data(DEVICE_ADDRESS, 0x0B, 0x01)  # Soft reset
    time.sleep(0.1)
    bus.write_byte_data(DEVICE_ADDRESS, 0x09, 0x1D)  # 10Hz, continuous mode, 2G, 512 oversampling

def read_raw_data():
    data = bus.read_i2c_block_data(DEVICE_ADDRESS, 0x00, 6)
    x = data[1] << 8 | data[0]
    y = data[3] << 8 | data[2]
    z = data[5] << 8 | data[4]
    # Convert to signed
    if x >= 32768: x -= 65536
    if y >= 32768: y -= 65536
    if z >= 32768: z -= 65536
    return x, y, z

def get_heading():
    x, y, z = read_raw_data()
    heading_rad = math.atan2(y, x)
    heading_deg = math.degrees(heading_rad)
    if heading_deg < 0:
        heading_deg += 360
    return heading_deg

setup()

while True:
    heading = get_heading()
    print(f"Heading: {heading:.2f}°")
    time.sleep(1)

