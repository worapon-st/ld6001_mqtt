import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import json
from collections import defaultdict

host = "YourIP"
port = 1234
user = "YourUsername"
password = "YourPassword"

topic_status = "radar/sensor_status"
topic_params = "radar/detect_params"

target_position = {}

plt.ion()
fig, ax = plt.subplots()
scat = ax.scatter([], [], s=50)
ax.set_xlim(-5, 5)
ax.set_ylim(0, 8)
ax.set_xlabel("X (m)")
ax.set_ylabel("Y (m)")
ax.grid(True)

def on_connect(client, userdata, flags, rc):
    print(f"MQTT connected : {rc}")
    client.subscribe(topic_params)
    
def on_message(client, userdata, msg):
    print(f"receive on {msg.topic} : {msg.payload.decode()}")
    if msg.topic == topic_params:
        try:
            data = json.loads(msg.payload.decode())
            current_targets = {}
            for target in data.get("targets", []):
                tid = target["id"]
                xs = target["x_coord"]
                ys = target["y_coord"]
                current_targets[tid] = (xs, ys)
            target_position.clear()
            target_position.update(current_targets)
            print(target_position)
            update_plot()
        except Exception as e:
            print(f'Error: {e}')

def update_plot():
    xs = [pos[0] for pos in target_position.values()]
    ys = [pos[1] for pos in target_position.values()]
    scat.set_offsets(list(zip(xs, ys)))
    scat.set_array([tid for tid in target_position.keys()])
    fig.canvas.draw()
    fig.canvas.flush_events()
    

client = mqtt.Client()
client.username_pw_set(user, password)
client.on_connect = on_connect
client.on_message = on_message

client.connect(host, port, 60)
client.loop_forever()