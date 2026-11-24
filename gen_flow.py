import json
Z="flow_api"
H="msg.headers={'Access-Control-Allow-Origin':'*'};"
def fn(id,name,func,x,y,wires,outputs=1):
    return {"id":id,"type":"function","z":Z,"name":name,"func":func,"outputs":outputs,"noerr":0,"x":x,"y":y,"wires":wires}
def http_in(id,name,url,method,y):
    return {"id":id,"type":"http in","z":Z,"name":name,"url":url,"method":method,"upload":False,"swaggerDoc":"","x":160,"y":y,"wires":[["auth"]]}
N=[]
N.append({"id":Z,"type":"tab","label":"IoT REST API","disabled":False,"info":""})
N.append({"id":"mqtt_broker_config","type":"mqtt-broker","name":"Local Mosquitto","broker":"localhost","port":"1883","clientid":"node-red-backend","autoConnect":True,"usetls":False,"protocolVersion":"4","keepalive":"60","cleansession":True})
N.append({"id":"ws_listener","type":"websocket-listener","path":"/ws/sensor","wholemsg":"false"})
N.append({"id":"sqlite_db","type":"sqlitedb","db":"iot_history.db","mode":"RWC"})
# init
N.append({"id":"init_inject","type":"inject","z":Z,"name":"Init (sekali)","props":[],"repeat":"","crontab":"","once":True,"onceDelay":"1","topic":"","x":150,"y":40,"wires":[["init_fn"]]})
N.append(fn("init_fn","Set Threshold Default","if (flow.get('threshold') === undefined) flow.set('threshold', 30);\nreturn msg;",360,40,[["create_table"]]))
N.append({"id":"create_table","type":"sqlite","z":Z,"mydb":"sqlite_db","sqlquery":"fixed","sql":"CREATE TABLE IF NOT EXISTS sensor_history (id INTEGER PRIMARY KEY AUTOINCREMENT, suhu REAL, kelembaban REAL, timestamp TEXT, received TEXT);","name":"Buat Tabel","x":590,"y":40,"wires":[[]]})
# sensor pipeline
N.append({"id":"mqtt_sensor_in","type":"mqtt in","z":Z,"name":"Subscribe Sensor","topic":"iot/sensor","qos":"0","datatype":"json","broker":"mqtt_broker_config","x":160,"y":120,"wires":[["proses"]]})
N.append(fn("proses","Proses Sensor",
"""const d = msg.payload;
d.received = new Date().toISOString();
flow.set('lastSensor', d);
const th = flow.get('threshold');
const dbMsg = {params: {$suhu: d.suhu, $kelembaban: d.kelembaban, $timestamp: d.timestamp, $received: d.received}};
const wsMsg = {payload: {type: 'sensor', data: d, threshold: th}};
let alertMsg = null;
const now = Date.now();
if (d.suhu > th && now - (flow.get('lastAlert') || 0) > 10000) {
  flow.set('lastAlert', now);
  alertMsg = {topic: 'iot/notifikasi', payload: {type: 'alert', message: 'Suhu ' + d.suhu + ' C melewati batas ' + th + ' C', suhu: d.suhu, threshold: th, time: d.received}};
}
return [dbMsg, wsMsg, alertMsg];""",400,120,[["sql_insert"],["ws_out","debug_sensor"],["ws_out","debug_alert","mqtt_out"]],3))
N.append({"id":"sql_insert","type":"sqlite","z":Z,"mydb":"sqlite_db","sqlquery":"prepared","sql":"INSERT INTO sensor_history (suhu,kelembaban,timestamp,received) VALUES ($suhu,$kelembaban,$timestamp,$received);","name":"Simpan ke SQLite","x":680,"y":80,"wires":[[]]})
N.append({"id":"debug_sensor","type":"debug","z":Z,"name":"Log Sensor","active":True,"complete":"payload","x":680,"y":140,"wires":[]})
N.append({"id":"debug_alert","type":"debug","z":Z,"name":"Log Notifikasi","active":True,"complete":"payload","x":690,"y":200,"wires":[]})
N.append({"id":"ws_out","type":"websocket out","z":Z,"name":"WebSocket Broadcast","server":"ws_listener","client":"","x":920,"y":140,"wires":[]})
N.append({"id":"mqtt_out","type":"mqtt out","z":Z,"name":"Publish MQTT","topic":"","qos":"0","retain":"false","broker":"mqtt_broker_config","x":920,"y":220,"wires":[]})
# http entries
N.append(http_in("h_suhu","GET /api/suhu","/api/suhu","get",300))
N.append(http_in("h_hist","GET /api/history","/api/history","get",350))
N.append(http_in("h_kontrol","POST /api/kontrol","/api/kontrol","post",400))
N.append(http_in("h_th_put","PUT /api/threshold","/api/threshold","put",450))
N.append(http_in("h_th_get","GET /api/threshold","/api/threshold","get",500))
N.append(fn("auth","Cek API Key (X-API-Key)",
"""const KEY = env.get('API_KEY') || 'iot-kampus-2026';
msg.route = msg.req.method + ' ' + msg.req.path;
if (msg.req.headers['x-api-key'] !== KEY) {
  msg.statusCode = 401;
  """+H+"""
  msg.payload = {status: 'error', message: 'API key tidak valid / tidak ada (header X-API-Key)'};
  return [null, msg];
}
return [msg, null];""",400,400,[["router"],["http_resp"]],2))
rules=[{"t":"eq","v":v,"vt":"str"} for v in ["GET /api/suhu","GET /api/history","POST /api/kontrol","PUT /api/threshold","GET /api/threshold"]]
N.append({"id":"router","type":"switch","z":Z,"name":"Router Endpoint","property":"route","propertyType":"msg","rules":rules,"checkall":"false","repair":False,"outputs":5,"x":620,"y":400,"wires":[["r_suhu"],["q_hist"],["r_kontrol"],["r_th_put"],["r_th_get"]]})
N.append(fn("r_suhu","Response Suhu","const d = flow.get('lastSensor') || {suhu: null, kelembaban: null, timestamp: null};\nmsg.statusCode = 200;\nmsg.payload = {status: 'success', data: d, threshold: flow.get('threshold'), server_time: new Date().toISOString()};\n"+H+"\nreturn msg;",860,300,[["http_resp"]]))
N.append({"id":"q_hist","type":"sqlite","z":Z,"mydb":"sqlite_db","sqlquery":"fixed","sql":"SELECT * FROM (SELECT * FROM sensor_history ORDER BY id DESC LIMIT 50) ORDER BY id ASC;","name":"Query 50 Terakhir","x":860,"y":350,"wires":[["r_hist"]]})
N.append(fn("r_hist","Response History","const rows = msg.payload || [];\nmsg.statusCode = 200;\nmsg.payload = {status: 'success', count: rows.length, data: rows};\n"+H+"\nreturn msg;",1080,350,[["http_resp"]]))
N.append(fn("r_kontrol","Validasi & Publish Kontrol",
"""const body = msg.payload || {};
"""+H+"""
if (!body.device || !body.action) {
  msg.statusCode = 400;
  msg.payload = {status: 'error', message: 'device dan action wajib diisi'};
  return [msg, null];
}
node.send([null, {topic: 'iot/kontrol', payload: body}]);
msg.statusCode = 200;
msg.payload = {status: 'success', message: 'Perintah terkirim', sent: body};
return [msg, null];""",880,400,[["http_resp"],["mqtt_out"]],2))
N.append(fn("r_th_put","Set Threshold",
"""const t = Number(msg.payload && msg.payload.threshold);
"""+H+"""
if (!isFinite(t)) {
  msg.statusCode = 400;
  msg.payload = {status: 'error', message: 'threshold wajib berupa angka'};
  return [msg, null];
}
flow.set('threshold', t);
flow.set('lastAlert', 0);
node.send([null, {payload: {type: 'threshold', threshold: t}}]);
msg.statusCode = 200;
msg.payload = {status: 'success', message: 'Batas suhu diperbarui', threshold: t};
return [msg, null];""",880,450,[["http_resp"],["ws_out"]],2))
N.append(fn("r_th_get","Get Threshold","msg.statusCode = 200;\nmsg.payload = {status: 'success', threshold: flow.get('threshold')};\n"+H+"\nreturn msg;",880,500,[["http_resp"]]))
N.append({"id":"http_resp","type":"http response","z":Z,"name":"Kirim Response","statusCode":"","headers":{},"x":1250,"y":400,"wires":[]})
# CORS
N.append({"id":"h_cors","type":"http in","z":Z,"name":"OPTIONS CORS","url":"/api/*","method":"options","upload":False,"swaggerDoc":"","x":160,"y":560,"wires":[["cors_fn"]]})
N.append(fn("cors_fn","CORS Headers","msg.statusCode = 204;\nmsg.payload = '';\nmsg.headers = {\n 'Access-Control-Allow-Origin': '*',\n 'Access-Control-Allow-Methods': 'GET, POST, PUT, OPTIONS',\n 'Access-Control-Allow-Headers': 'Content-Type, X-API-Key'\n};\nreturn msg;",400,560,[["http_resp"]]))
json.dump(N,open("flows.json","w"),indent=2,ensure_ascii=False)
