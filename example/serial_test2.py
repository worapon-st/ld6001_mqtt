import serial
import matplotlib.pyplot as plt
import time

def calc_checksum(data: bytes) -> int:
    """Sum from Byte0 to Byte(N-3), take low 8 bits"""
    return sum(data) & 0xFF

# ----------------------
# Serial setup
# ----------------------
ser = serial.Serial(
    port="COM8",   # change to /dev/ttyUSB0 if using USB-UART
    baudrate=9600,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_EVEN,
    stopbits=serial.STOPBITS_ONE,
    timeout=0.5
)

# ----------------------
# Command: get radar detection data (0x62)
# ----------------------
def make_radar_cmd():
    cmd = bytearray([
        0x44, 0x62, 0x08, 0x00,
        0x10,   # sensitivity: 0x10 normal, 0x20 high
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ])
    cmd.append(calc_checksum(cmd))
    cmd.append(0x4B)
    return cmd

# ----------------------
# Parse radar response
# ----------------------
def parse_targets(resp: bytes):
    targets = []
    if len(resp) < 14:
        return targets
    if resp[0] != 0x4D or resp[1] != 0x62:
        return targets
    num_targets = resp[5]
    offset = 12
    for i in range(num_targets):
        if offset + 8 > len(resp):
            break
        tid   = resp[offset]
        dist  = resp[offset+1] * 0.1   # meters
        pitch = resp[offset+2]
        horiz = resp[offset+3]
        x     = int.from_bytes([resp[offset+6]], "big", signed=True) * 0.1
        y     = int.from_bytes([resp[offset+7]], "big", signed=True) * 0.1
        targets.append((tid, dist, pitch, horiz, x, y))
        offset += 8
    return targets

# ----------------------
# Live visualization
# ----------------------
plt.ion()
fig, ax = plt.subplots()
scat = ax.scatter([], [])
ax.set_xlim(-5, 5)   # adjust depending on expected range
ax.set_ylim(0, 8)
ax.set_xlabel("X (m)")
ax.set_ylabel("Y (m)")
ax.set_title("HLK-LD6001 Radar Targets")

try:
    while True:
        ser.write(make_radar_cmd())
        resp = ser.read(128)  # read response
        targets = parse_targets(resp)

        if targets:
            xs = [t[4] for t in targets]
            ys = [t[5] for t in targets]
            scat.set_offsets(list(zip(xs, ys)))
        else:
            #scat.set_offsets([])
            pass

        fig.canvas.draw()
        fig.canvas.flush_events()
        time.sleep(0.2)  # polling interval

except KeyboardInterrupt:
    print("Stopped by user.")
finally:
    ser.close()
