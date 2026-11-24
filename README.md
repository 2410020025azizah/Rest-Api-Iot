# IoT REST API — Node-RED + MQTT + Dashboard

**Disusun oleh:** Siti Azizah Salsabila  
**Mata Kuliah:** Praktikum Pemrograman IoT (SIF1502)  
**Pertemuan:** 9

## Instalasi Node.js dan Node-RED

Pastikan Node.js dan npm sudah terinstal.

Cek versi:

```bash
node -v
npm -v
```

Install Node-RED:

```bash
npm install -g node-red
```

Install node SQLite:

```bash
cd C:\Users\ASUS-G531GT\.node-red
npm install node-red-node-sqlite
```

Jalankan Node-RED:

```bash
node-red
```

## Fitur Proyek

- REST API: `GET /api/suhu`, `GET /api/history`, `POST /api/kontrol`
- `PUT /api/threshold` dan `GET /api/threshold`
- Notifikasi otomatis ketika suhu melewati batas
- Grafik real-time menggunakan Chart.js
- Autentikasi API Key melalui `X-API-Key`
- WebSocket untuk pembaruan data real-time
- Penyimpanan riwayat menggunakan SQLite (`iot_history.db`)

## Struktur Proyek

```text
flows.json
simulasi_esp32.py
static/
  dashboard.html
settings-snippet.js
gen_flow.py
requirements.txt
README.md
```

## Cara Menjalankan

1. Jalankan Mosquitto:

```bash
mosquitto -v
```

2. Jalankan Node-RED:

```bash
node-red
```

3. Import `flows.json` ke Node-RED, kemudian klik Deploy.
4. Atur `httpStatic` pada `settings.js`.
5. Install library Python:

```bash
pip install -r requirements.txt
```

6. Jalankan simulator:

```bash
python simulasi_esp32.py
```

7. Buka dashboard:

```text
http://localhost:1880/dashboard.html
```

## API Key

```text
iot-kampus-2026
```

## Upload ke GitHub

```bash
git init
git add .
git commit -m "Tugas IoT REST API - Siti Azizah Salsabila"
git branch -M main
git remote add origin https://github.com/<username>/<repo>.git
git push -u origin main
```
