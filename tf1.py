import serial
import numpy as np
import matplotlib.pyplot as plt
import re
import math

# Serial config (adjust your port)
PORT = 'COM8'  # or 'COM3' on Windows
BAUD = 115200
ser = serial.Serial(PORT, BAUD, timeout=1)

# Convert degrees to radians
def to_radians(deg):
    return math.radians(deg)

# Convert polar to Cartesian (for 3D plotting)
def polar_to_cartesian(tilt_deg, pan_deg, distance_cm):
    r = distance_cm
    tilt = to_radians(tilt_deg)
    pan = to_radians(pan_deg)

    x = r * math.cos(tilt) * math.cos(pan)
    y = r * math.cos(tilt) * math.sin(pan)
    z = r * math.sin(tilt)
    return x, y, z

# Plot setup
plt.ion()
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_xlim([-200, 200])
ax.set_ylim([-200, 200])
ax.set_zlim([0, 200])
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")

x_vals, y_vals, z_vals = [], [], []

try:
    print("Listening for LiDAR scan data...")
    while True:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        match = re.search(r'Tilt: (\d+), Pan: (\d+), Distance: (\d+)', line)
        if match:
            tilt = int(match.group(1))
            pan = int(match.group(2))
            dist = int(match.group(3))

            x, y, z = polar_to_cartesian(tilt, pan, dist)
            x_vals.append(x)
            y_vals.append(y)
            z_vals.append(z)

            ax.clear()
            ax.set_xlim([-200, 200])
            ax.set_ylim([-200, 200])
            ax.set_zlim([0, 200])
            ax.set_xlabel("X")
            ax.set_ylabel("Y")
            ax.set_zlabel("Z")
            ax.scatter(x_vals, y_vals, z_vals, c='red', s=5)
            plt.draw()
            plt.pause(0.01)

except KeyboardInterrupt:
    print("\n[EXIT] User interrupted.")
    ser.close()
