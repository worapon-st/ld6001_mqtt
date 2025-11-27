from ld6001 import LD6001, SensorSensitivity
import paho.mqtt.client as mqtt
import datetime
import json

radar = LD6001(port= "/dev/ttyS1", baudrate= 9600)

client = mqtt.Client()
host = "YourIP"
port = 1234
user = "YourUsername"
password = "YourPassword"

topic_status = "radar/sensor_status"
topic_params = "radar/detect_params"

def main():
    try:
        client.username_pw_set(user, password)
        client.connect(host= host, port= port)

        status = radar.ld6001_request_status()
        status_publish = json.dumps({
            "timestamp"    : datetime.datetime.now().strftime("%d/%m/%y %A:%H:%M:%S"),
            "software_minor" : status.sw_minor,
            "software_major" : status.sw_major,
            "hardware_minor" : status.hw_minor,
            "hardware_major" : status.hw_major,
            "initial_status" : "initialized" if status.ini_stat == 0 else 'initializing'
        })
        client.publish(topic= topic_status, payload= status_publish)

        data = radar.ld6001_request_data(sensitive=SensorSensitivity.NORMAL)
        ctrl_temp = 27
        if data.target_amount >= 6:
            ctrl_temp = 27
        elif data.target_amount >= 4:
            ctrl_temp = 26
        else:
            ctrl_temp = 25

        data_publish = json.dumps({
            "timestamp"    : datetime.datetime.now().strftime("%d/%m/%y %A:%H:%M:%S"),
            "fault_status" : 'no fault' if data.fault_status == 0 else 'fault',
            "target_amount": data.target_amount,
            "temp_control" : ctrl_temp,
            "targets" : [{
                "id"       : target.id,
                "distance" : round(target.distance, 2),
                "pitch"    : target.pitch,
                "yaw"      : target.yaw,
                "x_coord"  : round(target.x_coord, 2),
                "y_coord"  : round(target.y_coord, 2)
                } for target in data.targets ]
        })
        client.publish(topic= topic_params, payload= data_publish)

    except ValueError as e:
        print(f'Error : {e}')
        radar.close()
        client.disconnect()
        
if __name__ == "__main__":
    try:  
        while True:
            main()
    except KeyboardInterrupt:
        radar.close()
        client.disconnect()