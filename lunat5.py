import serial
import time

# ====================
# Serial Functions
# ====================
def read_tfluna_data():
    while True:
        counter = ser.in_waiting
        if counter > 8:
            bytes_serial = ser.read(9)
            ser.reset_input_buffer()

            if bytes_serial[0] == 0x59 and bytes_serial[1] == 0x59:
                distance = bytes_serial[2] + bytes_serial[3]*256
                strength = bytes_serial[4] + bytes_serial[5]*256
                temperature = bytes_serial[6] + bytes_serial[7]*256
                temperature = (temperature / 8) - 256
                return distance/100.0, strength, temperature

def set_samp_rate(samp_rate=100):
    samp_rate_packet = [0x5a, 0x06, 0x03, samp_rate, 0x00, 0x00]
    ser.write(bytearray(samp_rate_packet))

def get_version():
    info_packet = [0x5a, 0x04, 0x14, 0x00]
    ser.write(bytearray(info_packet))
    time.sleep(0.1)
    bytes_to_read = 30
    t0 = time.time()
    while (time.time() - t0) < 5:
        counter = ser.in_waiting
        if counter >= bytes_to_read:
            bytes_data = ser.read(bytes_to_read)
            ser.reset_input_buffer()
            if bytes_data[0] == 0x5a:
                try:
                    version = bytes_data[3:-1].decode('utf-8')
                    print("Version:", version)
                except Exception as e:
                    print("Failed to decode version:", e)
                return
            else:
                ser.write(bytearray(info_packet))
                time.sleep(0.1)

def set_baudrate(baud_indx=4):
    baud_hex = [
        [0x80, 0x25, 0x00],  # 9600
        [0x00, 0x4b, 0x00],  # 19200
        [0x00, 0x96, 0x00],  # 38400
        [0x00, 0xe1, 0x00],  # 57600
        [0x00, 0xc2, 0x01],  # 115200
        [0x00, 0x84, 0x03],  # 230400
        [0x00, 0x08, 0x07],  # 460800
        [0x00, 0x10, 0x0e]   # 921600
    ]

    info_packet = [0x5a, 0x08, 0x06] + baud_hex[baud_indx] + [0x00, 0x00]

    prev_ser.write(bytearray(info_packet))
    time.sleep(0.1)
    prev_ser.close()
    time.sleep(0.1)

    ser_new = serial.Serial("/dev/ttyS0", baudrates[baud_indx], timeout=0)
    if not ser_new.isOpen():
        ser_new.open()

    bytes_to_read = 8
    t0 = time.time()
    while (time.time() - t0) < 5:
        counter = ser_new.in_waiting
        if counter >= bytes_to_read:
            bytes_data = ser_new.read(bytes_to_read)
            ser_new.reset_input_buffer()
            if bytes_data[0] == 0x5a:
                indx = [
                    ii for ii in range(len(baud_hex))
                    if baud_hex[ii] == list(bytes_data[3:6])
                ]
                if indx:
                    print("Set Baud Rate =", baudrates[indx[0]])
                else:
                    print("Warning: Unexpected response for baud rate set.")
                    print("Raw bytes from device:", bytes_data.hex())
                time.sleep(0.1)
                return ser_new
            else:
                ser_new.write(bytearray(info_packet))
                time.sleep(0.1)
    print("Baud rate change may have failed, continuing...")
    return ser_new

# ====================
# Main Config
# ====================
baudrates = [9600,19200,38400,57600,115200,230400,460800,921600]
prev_indx = 4  # current baudrate
baud_indx = 4  # target baudrate (115200)
prev_ser = serial.Serial("/dev/ttyS0", baudrates[prev_indx], timeout=0)
if not prev_ser.isOpen():
    prev_ser.open()

ser = set_baudrate(baud_indx)
set_samp_rate(100)
get_version()

# ====================
# Terminal Output Loop
# ====================
print("Starting TF-Luna distance measurements...\n")
try:
    while True:
        distance, strength, temperature = read_tfluna_data()
        print(f"Distance: {distance:.2f} m | Strength: {strength} | Temp: {temperature:.1f}°C")
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nExiting...")
    ser.close()

