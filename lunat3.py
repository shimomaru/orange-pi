######################################################
# Copyright (c) 2021 Maker Portal LLC
# Author: Joshua Hrisko
######################################################
#
# TF-Luna Mini LiDAR wired to a Raspberry Pi via UART
# --- Configuring the TF-Luna's baudrate, sample rate,
# --- and printing out the device version info
#
######################################################

import serial
import time
import numpy as np

############################
# Serial Functions
############################

def read_tfluna_data():
    while True:
        counter = ser.in_waiting  # count the number of bytes in the serial port
        bytes_to_read = 9
        if counter > bytes_to_read - 1:
            bytes_serial = ser.read(bytes_to_read)  # read 9 bytes
            ser.reset_input_buffer()  # reset buffer

            if bytes_serial[0] == 0x59 and bytes_serial[1] == 0x59:  # check first two bytes
                distance = bytes_serial[2] + bytes_serial[3] * 256  # distance in next two bytes
                strength = bytes_serial[4] + bytes_serial[5] * 256  # signal strength in next two bytes
                temperature = bytes_serial[6] + bytes_serial[7] * 256  # temp in next two bytes
                temperature = (temperature / 8) - 256  # temp scaling and offset
                return distance / 100.0, strength, temperature

def set_samp_rate(samp_rate=100):
    ##########################
    # change the sample rate
    samp_rate_packet = [0x5a, 0x06, 0x03, samp_rate, 0x00, 0x00]  # sample rate byte array
    ser.write(bytearray(samp_rate_packet))  # send sample rate instruction
    time.sleep(0.1)  # wait for change to take effect
    return

def get_version():
    ##########################
    # get version info
    info_packet = [0x5a, 0x04, 0x14, 0x00]

    ser.write(bytearray(info_packet))
    time.sleep(0.1)
    bytes_to_read = 30
    t0 = time.time()
    while (time.time() - t0) < 5:
        counter = ser.in_waiting
        if counter > bytes_to_read:
            bytes_data = ser.read(bytes_to_read)
            ser.reset_input_buffer()
            if bytes_data[0] == 0x5a:
                try:
                    version = bytes_data[3:-1].decode('utf-8', errors='ignore')
                    print(f'Version: {version}')
                except UnicodeDecodeError as e:
                    print(f"Failed to decode version: {e}")
                return
            else:
                ser.write(bytearray(info_packet))
                time.sleep(0.1)

def set_baudrate(baud_indx=4):
    ##########################
    # set the baudrate
    baud_hex = [
        [0x80, 0x25, 0x00],  # 9600
        [0x00, 0x4b, 0x00],  # 19200
        [0x00, 0x96, 0x00],  # 38400
        [0x00, 0xe1, 0x00],  # 57600
        [0x00, 0xc2, 0x01],  # 115200
        [0x00, 0x84, 0x03],  # 230400
        [0x00, 0x08, 0x07],  # 460800
        [0x00, 0x10, 0x0e],  # 921600
    ]
    
    info_packet = [0x5a, 0x08, 0x06, baud_hex[baud_indx][0], baud_hex[baud_indx][1],
                   baud_hex[baud_indx][2], 0x00, 0x00]  # instruction packet
    
    ser.write(bytearray(info_packet))  # change the baud rate
    time.sleep(0.1)  # wait for change to take effect
    ser.close()  # close the old serial port
    time.sleep(0.1)  # wait to settle
    ser_new = serial.Serial("/dev/ttyS0", baudrates[baud_indx], timeout=0)  # new serial device
    if not ser_new.isOpen():
        ser_new.open()  # open serial port if not open
    bytes_to_read = 8
    t0 = time.time()
    while (time.time() - t0) < 5:
        counter = ser_new.in_waiting
        if counter > bytes_to_read:
            bytes_data = ser_new.read(bytes_to_read)
            ser_new.reset_input_buffer()
            if bytes_data[0] == 0x5a:
                indx = [ii for ii in range(0, len(baud_hex)) if
                        baud_hex[ii][0] == bytes_data[3] and
                        baud_hex[ii][1] == bytes_data[4] and
                        baud_hex[ii][2] == bytes_data[5]]
                print(f'Baud Rate = {baudrates[indx[0]]}')
                time.sleep(0.1)
                return ser_new
            else:
                ser_new.write(bytearray(info_packet))  # try again if wrong data received
                time.sleep(0.1)  # wait 100ms
                continue

############################
# Configurations
############################

baudrates = [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]  # baud rates
prev_indx = 4  # previous baud rate index (current TF-Luna baudrate)
ser = serial.Serial("/dev/ttyS0", baudrates[prev_indx], timeout=0)  # serial device for communication
if not ser.isOpen():
    ser.open()  # open serial port if not open

baud_indx = 4  # baud rate to be changed to (new baudrate for TF-Luna)
ser = set_baudrate(baud_indx)  # set baudrate, get new serial at new baudrate
set_samp_rate(100)  # set sample rate 1-250
get_version()  # print version info for TF-Luna
time.sleep(0.1)  # wait 100ms to settle

############################
# Testing the TF-Luna Output
############################

tot_pts = 100  # points for sample rate test
t0 = time.time()  # for timing
dist_array = []  # for storing values

while len(dist_array) < tot_pts:
    try:
        distance, strength, temperature = read_tfluna_data()  # read values
        dist_array.append(distance)  # append to array
    except Exception as e:
        print(f"Error reading data: {e}")
        continue

print(f'Sample Rate: {len(dist_array) / (time.time() - t0):.0f} Hz')  # print sample rate
ser.close()  # close serial port

