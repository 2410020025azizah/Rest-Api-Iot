# IoT REST API — Node-RED + MQTT + Dashboard

Praktikum Pemrograman IoT (SIF1502) Pertemuan 9.
ESP32 (simulator) → MQTT → Node-RED (REST API + WebSocket + SQLite) → Web Dashboard.

## Fitur
- REST API: `GET /api/suhu`, `GET /api/history`, `POST /api/kontrol`
- **Nilai tambah**
  1. `PUT /api/threshold` (+ `GET /api/threshold`) — set batas suhu, notifikasi otomatis (WebSocket, MQTT `iot/notifikasi`, banner dashboard)
  2. Grafik real-time Chart.js
  3. Autentikasi API key via header `X-API-Key` (default `iot-kampus-2026`, bisa diganti lewat env `API_KEY`)
  4. WebSocket `ws://localhost:1880/ws/sensor` (polling hanya sebagai fallback)
  5. History disimpan di SQLite (`iot_history.db`)

## Struktur
```
flows.json            -> import ke Node-RED
simulasi_esp32.py     -> simulator ESP32 (paho-mqtt v2)
static/dashboard.html -> dashboard (tema baby pink)
settings-snippet.js   -> contoh httpStatic di settings.js
gen_flow.py           -> generator flows.json (opsional)
```

## Cara Menjalankan
1. Install node SQLite: `cd ~/.node-red && npm install node-red-node-sqlite`
2. Jalankan broker: `mosquitto -v`
3. Jalankan Node-RED: `node-red` → menu ☰ → Import → pilih `flows.json` → Deploy
   (jika SQLite error, buka node "Simpan ke SQLite" dan isi path absolut database, mis. `C:/node-red-static/iot_history.db`)
4. Salin `static/dashboard.html` ke folder static Node-RED (lihat `settings-snippet.js`), restart Node-RED
5. `pip install -r requirements.txt` lalu `python simulasi_esp32.py`
6. Buka `http://localhost:1880/dashboard.html`

## Testing (curl)
```bash
KEY="iot-kampus-2026"
curl -H "X-API-Key: $KEY" http://localhost:1880/api/suhu
curl -H "X-API-Key: $KEY" http://localhost:1880/api/history
curl -X POST http://localhost:1880/api/kontrol -H "Content-Type: application/json" -H "X-API-Key: $KEY" -d '{"device":"lamp","action":"on"}'
curl -X PUT  http://localhost:1880/api/threshold -H "Content-Type: application/json" -H "X-API-Key: $KEY" -d '{"threshold":29}'
curl http://localhost:1880/api/suhu   # tanpa key -> 401
```

## Upload ke GitHub
```bash
git init && git add . && git commit -m "Tugas IoT REST API Node-RED"
git branch -M main
git remote add origin https://github.com/<username>/<repo>.git
git push -u origin main
```
