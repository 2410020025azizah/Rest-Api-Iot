import json, time, random
from datetime import datetime
import paho.mqtt.client as mqtt

BROKER = "localhost"
TOPIC_SENSOR = "iot/sensor"
TOPIC_KONTROL = "iot/kontrol"
TOPIC_NOTIF = "iot/notifikasi"

try:  # paho-mqtt >= 2.0
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="ESP32-Simulator")
    V2 = True
except AttributeError:  # paho-mqtt 1.x
    client = mqtt.Client("ESP32-Simulator")
    V2 = False

def on_connect(client, userdata, flags, rc, properties=None):
    print("Terhubung ke MQTT Broker!")
    client.subscribe([(TOPIC_KONTROL, 0), (TOPIC_NOTIF, 0)])

def on_message(client, userdata, msg):
    label = "KONTROL" if msg.topic == TOPIC_KONTROL else "NOTIF"
    print(f"<- [{label}] {msg.payload.decode()}")

client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, 1883, 60)
client.loop_start()
print("ESP32 Simulator berjalan... Ctrl+C untuk stop")
try:
    while True:
        data = {
            "suhu": round(random.uniform(25, 34), 1),  # sesekali > 30 agar notifikasi muncul
            "kelembaban": round(random.uniform(55, 80), 1),
            "timestamp": datetime.now().isoformat(),
        }
        client.publish(TOPIC_SENSOR, json.dumps(data))
        print(f"-> Publish: {data}")
        time.sleep(3)
except KeyboardInterrupt:
    client.loop_stop()
    client.disconnect()
