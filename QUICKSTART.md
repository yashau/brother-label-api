# Quick Start Guide

Get your Brother Label API API running in **2 minutes** with Docker!

## Prerequisites

- **Docker and Docker Compose** installed ([Get Docker](https://docs.docker.com/get-docker/))
- Brother QL or PT series printer on your network
- Printer's IP address

**Don't know your printer's IP?**
- Check your router's admin page
- Windows: `arp -a` and look for Brother device
- Linux/Mac: `nmap -sn 192.168.1.0/24` (if nmap installed)

---

## Docker Method (Recommended - 2 Minutes!)

### Step 1: Configure

```bash
# Copy example config
cp config.example.json config.json
```

Edit `config.json` with your printer:

```json
{
  "api_keys": ["my-secret-key-12345"],
  "printers": [{
    "id": "my-printer",
    "name": "Office Printer",
    "model": "QL-820NWB",
    "backend": "network",
    "identifier": "tcp://192.168.1.100",
    "label_size": "62"
  }]
}
```

### Step 2: Start

```bash
docker-compose up -d
```

Done! API is running at `http://localhost:5000`

### Step 3: Test

```bash
# Check health
curl http://localhost:5000/health

# Print a test label
curl -X POST http://localhost:5000/api/print \
  -H "X-API-Key: my-secret-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "printer_id": "my-printer",
    "text": "Hello Docker!",
    "options": {"font_size": 36, "cut": true}
  }'
```

### Docker Commands

```bash
# View logs
docker-compose logs -f

# Stop
docker-compose down

# Restart
docker-compose restart

# Rebuild after code changes
docker-compose up -d --build
```

---

## Python Method (Alternative)

If you prefer running directly with Python:

### Requirements
- Python 3.9-3.14+ installed

### Install

```bash
# Create virtual environment
python -m venv venv

# Activate
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install
pip install -r requirements.txt
```

### Configure

```bash
cp config.example.json config.json
# Edit config.json with your printer
```

### Run

```bash
python app.py
```

---

## API Usage Examples

### Print Text

```bash
curl -X POST http://localhost:5000/api/print \
  -H "X-API-Key: my-secret-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "printer_id": "my-printer",
    "text": "Product: ABC-123\nPrice: $19.99",
    "options": {"font_size": 28, "cut": true}
  }'
```

### Print Image

First, encode your image:
```bash
base64 label.png > label.b64
```

Then print:
```bash
curl -X POST http://localhost:5000/api/print \
  -H "X-API-Key: my-secret-key-12345" \
  -H "Content-Type: application/json" \
  -d "{
    \"printer_id\": \"my-printer\",
    \"image_base64\": \"$(cat label.b64 | tr -d '\n')\",
    \"options\": {\"cut\": true, \"margin\": 10}
  }"
```

### From Python

```python
import requests
import base64

url = "http://localhost:5000/api/print"
headers = {
    "X-API-Key": "my-secret-key-12345",
    "Content-Type": "application/json"
}

# Print text
response = requests.post(url, headers=headers, json={
    "printer_id": "my-printer",
    "text": "Hello from Python!",
    "options": {"font_size": 30, "cut": True}
})
print(response.json())

# Print image
with open("label.png", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

response = requests.post(url, headers=headers, json={
    "printer_id": "my-printer",
    "image_base64": img_b64,
    "options": {"cut": True}
})
print(response.json())
```

### From JavaScript/Node.js

```javascript
const axios = require('axios');
const fs = require('fs');

const url = 'http://localhost:5000/api/print';
const headers = {
  'X-API-Key': 'my-secret-key-12345',
  'Content-Type': 'application/json'
};

// Print text
axios.post(url, {
  printer_id: 'my-printer',
  text: 'Hello from Node.js!',
  options: { font_size: 30, cut: true }
}, { headers })
  .then(res => console.log(res.data))
  .catch(err => console.error(err.response.data));

// Print image
const imageBuffer = fs.readFileSync('label.png');
const imageBase64 = imageBuffer.toString('base64');

axios.post(url, {
  printer_id: 'my-printer',
  image_base64: imageBase64,
  options: { cut: true, margin: 10 }
}, { headers })
  .then(res => console.log(res.data));
```

---

## Troubleshooting

### "Connection refused" to printer

```bash
# Test printer connectivity
ping 192.168.1.100
telnet 192.168.1.100 9100
```

- Verify printer is powered on
- Check printer IP address
- Ensure printer is on same network

### "Invalid API key"

- Check `config.json` has correct API key
- Ensure you're using the same key in API calls

### Docker container won't start

```bash
# Check logs
docker-compose logs

# Rebuild
docker-compose down
docker-compose up -d --build
```

### Can't find docker-compose

Try `docker compose` (without dash) on newer Docker versions:
```bash
docker compose up -d
```

---

## Next Steps

- 📖 Read [README.md](README.md) for complete API documentation
- 🔧 Check [COMPATIBILITY.md](COMPATIBILITY.md) for Python compatibility
- 🖨️ Add more printers to `config.json`
- 🚀 Deploy to production with reverse proxy (nginx)

---

## Why Docker?

✅ **No Python version issues** - Uses Python 3.13 image (3.14+ also supported)
✅ **Consistent environment** - Works everywhere
✅ **Easy deployment** - One command to start
✅ **Automatic restarts** - `restart: unless-stopped`
✅ **Health checks** - Built-in monitoring

---

**That's it!** Your Brother label printer now has a REST API. 🎉

For detailed documentation, see [README.md](README.md).
