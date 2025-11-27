import serial

ser = serial.Serial(
    port="COM6",
    baudrate=9600,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_EVEN,
    stopbits=serial.STOPBITS_ONE,
    timeout=1
)

def get_status():
    cmd = bytearray()
    cmd.append(0x44)
    cmd.append(0x11)
    cmd.append(0x00)
    cmd.append(0x00)
    checksum = sum(cmd) & 0xFF
    cmd.append(checksum)
    cmd.append(0x4B)
    
    print(list(cmd))

    ser.write(cmd)
    resp = ser.read(255)
    print(list(resp))

    print(f'sw: {(resp[4])}|{resp[5]} hw: {resp[6]}|{resp[7]} state: {resp[9]}')

def get_data():
    cmd = bytearray()
    cmd.append(0x44)
    cmd.append(0x62)
    cmd.append(0x08)
    cmd.append(0x00)
    cmd.append(0x10)
    cmd.append(0x00); cmd.append(0x00); cmd.append(0x00); cmd.append(0x00) 
    cmd.append(0x00); cmd.append(0x00); cmd.append(0x00)
    checksum = sum(cmd) & 0xFF
    cmd.append(checksum)
    cmd.append(0x4B)
    
    print(list(cmd))

    ser.write(cmd)
    resp = ser.read(255)
    print(list(resp))

if __name__ == "__main__":
    get_status()
    get_data()




