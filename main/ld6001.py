import serial
import datetime
from enum import Enum
from typing import List, NamedTuple

# Head and Tail of Protocol
HEAD_HOST_TO_MODULE = 0x44 
HEAD_MODULE_TO_HOST = 0x4D
TAIL_HOST_TO_MODULE = 0x4B
TAIL_MODULE_TO_HOST = 0x4A

# Sensor Sensitivity Configuration
class SensorSensitivity(Enum):
    NORMAL = 0x10
    HIGH   = 0x20

# Module Version
class LD6001status(NamedTuple):
    sw_minor: int                    # Software minor version
    sw_major: int                    # Software major version
    hw_minor: int                    # Hardware minor version
    hw_major: int                    # Hardware major version
    ini_stat: int                    # Initialization status

# Detection infomation
class TargetProperty(NamedTuple):
    id: int                          # Person Tracking ID
    distance: float                  # Detected Range from module
    pitch: int                       # Vertical axis (Up/Down)
    yaw: int                         # Horizon axis (Left/Right)
    x_coord: float                   # X-Coordinate
    y_coord: float                   # Y-Coordinate

# Module Data output 
class LD6001receive(NamedTuple):
    fault_status: int                # Error condition
    target_amount: int               # Amount of target in range
    targets: List[TargetProperty]

class LD6001:
    def __init__(self, port:str="/dev/ttyS1", baudrate:int=9600):
        # This configuration of UART must be fixed.
        self.ser = serial.Serial(
            port     = port,
            baudrate = baudrate,
            bytesize = serial.EIGHTBITS,
            parity   = serial.PARITY_EVEN,
            stopbits = serial.STOPBITS_ONE,
            timeout  = 1.0
        )

    def send_command(self, message_id:int, data:bytes = b'') -> bytes:
        # Use for send command to Module for request data out.
        #   - message_id    : request mode (status/data) 
        #   - data          : transmit data (if it needed)
        
        data_len:int = len(data)

        message = bytearray()
        message.append(HEAD_HOST_TO_MODULE)
        message.append(message_id)
        message.append(data_len)
        message.append(0x00)
        message.extend(data)

        checksum:int = sum(message) & 0xFF
        message.append(checksum)
        message.append(TAIL_HOST_TO_MODULE)

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"{timestamp}"," -> ",[f"{byte:02X}" for byte in message])
        self.ser.write(message)
        
        response = bytearray()
        received_data = self.ser.read(255)
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"{timestamp}"," <- ",[f"{byte:02X}" for byte in received_data], end="\n\n")

        if received_data: 
            response.extend(received_data) 

        if not response:
            raise ValueError('Cannot receive serial data')

        if response[0] != HEAD_MODULE_TO_HOST:
            raise ValueError('Invalid response header')
        
        if response[1] != message_id:
            raise ValueError('Invalid response message id')
        
        response_checksum = sum(response[0:-2]) & 0xFF
        if response[-2] != response_checksum:
            raise ValueError(f'Data loss expected {response_checksum} got {response[-2]}')
        
        response_data_len = response[2]
        response_data = response[4:4+response_data_len]

        return response_data

    def ld6001_request_status(self) -> LD6001status:
        # Use for request the status from module, for debugging only.
        #   > send 0x11 for status request mode

        response = self.send_command(0x11)
        if len(response) != 8:
            raise ValueError(f'Request Status: data loss, expected 8 bytes got {len(response)} bytes')
        
        print(f'STATUS| SW: {response[0]},{response[1]} | HW: {response[2]}{response[3]} | Initialization: {"initialized" if response[5] == 0 else "initializing..."}')

        return LD6001status(
            sw_minor= response[0],
            sw_major= response[1],
            hw_minor= response[2],
            hw_major= response[3],
            ini_stat= response[5]
        )

    def ld6001_request_data(self, sensitive:SensorSensitivity = SensorSensitivity.NORMAL) -> LD6001receive:
        # Use for request the detected data from module.
        #   > send 0x11 for status request mode
        #   - sensitive     : detection sensitive.
        command_data = bytearray([sensitive.value, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        response = self.send_command(0x62, command_data)

        if response[0] != 0:
            raise ValueError('Request Data: error appeared')
        
        targets = []
        byte_per_target = 8
        for i in range(response[1]):
            start_index = 8 + i * byte_per_target
            end_index = start_index + byte_per_target
            
            if end_index > len(response):
                break

            target_info = response[start_index:end_index]

            target = TargetProperty(
                id= target_info[0],
                distance= target_info[1] * 0.1,
                pitch= target_info[2],
                yaw= target_info[3],
                x_coord= int.from_bytes([target_info[6]], 'big', signed=True) * 0.1,
                y_coord= int.from_bytes([target_info[7]], 'big', signed=True) * 0.1
            )
            targets.append(target)

        print(f'ID: {target.id} | Distance: {target.distance:.2f}m | Pitch: {target.pitch}° | Yaw: {target.yaw}° | X: {target.x_coord:.2f}m | Y: {target.y_coord:.2f}m')

        return LD6001receive(
            fault_status= response[0],
            target_amount= response[1],
            targets= targets
        )
    
    def close(self) -> None:
        self.ser.close()