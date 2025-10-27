# Brother Label API

A modern REST API for controlling Brother PT/QL label printers. This replaces the outdated CLI tool with a HTTP-based service that supports multiple printers, API key authentication, and both text and image printing.

**[Quick Start](QUICKSTART.md)** | [API Documentation](#api-endpoints) | [Configuration](#configuration)

## Features

- REST API for Brother PT/QL label printers
- API key authentication with named keys
- Multiple printer support with JSON configuration
- Print text, images, or PDFs (multi-page support)
- Auto-discovery of network printers
- OpenTelemetry metrics for monitoring and observability
- Support for QL series (QL-820NWB, QL-810W, QL-700, etc.)
- Basic support for PT series (PT-P710BT, PT-P750W, etc.)
- Works with modern Python (3.9-3.14+)

## Requirements

- **Python**: 3.9, 3.10, 3.11, 3.12, 3.13, or 3.14+ (all supported!)
- **Printer**: Brother QL or PT series with network connectivity

## Installation

### Quick Start

1. **Clone this repository**:
```bash
git clone <your-repo-url>
cd brother-label-api
```

2. **Create a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

This installs everything needed, including our **bundled fixed `brother_ql`** that works with Python 3.9-3.13+!

4. **Create configuration file**:
```bash
cp config.example.json config.json
```

5. **Edit [config.json](config.json) with your printers and API keys**

### What's Included

This project bundles a fixed version of `brother_ql` in [brother_ql_fixed/](brother_ql_fixed/) that:
- ✅ Works with Python 3.9 through 3.13+
- ✅ Removes obsolete `python-future` dependency
- ✅ Preserves all original functionality
- ✅ Installs automatically with `pip install -r requirements.txt`

No extra steps, patches, or workarounds needed!

### Alternative: Docker

For hassle-free deployment, use Docker:
```bash
docker-compose up
```

### Testing Installation

Run the test script to verify everything is installed correctly:

```bash
python test_printer.py
```

Expected output:
```
✓ brother_ql installed: 0.9.5.1
✓ Using FIXED version (bundled in this project)
✓ QL series models supported
✓ Pillow installed: 12.0.0
✓ Flask installed: 3.1.0
```

## Configuration

Edit `config.json` to add your printers and API keys:

```json
{
  "api_keys": [
    {
      "name": "production-app",
      "key": "your-secret-api-key-here"
    },
    {
      "name": "staging-env",
      "key": "another-api-key"
    }
  ],
  "printers": [
    {
      "id": "office-printer",
      "name": "Office PT-P710BT",
      "model": "PT-P710BT",
      "backend": "network",
      "identifier": "tcp://192.168.1.100"
    }
  ]
}
```

### API Key Configuration

Each API key requires:
- `name`: A descriptive name/alias for the API key (e.g., "production-app", "mobile-client")
- `key`: The actual API key string used for authentication

The `name` field is useful for:
- Identifying which application/client is making requests
- Tracking usage per client in logs and telemetry
- Managing and rotating keys

### Printer Configuration Fields

- `id`: Unique identifier for the printer (used in API calls)
- `name`: Human-readable name
- `model`: Brother printer model (PT-P710BT, PT-P750W, etc.)
- `backend`: Connection type (`network`, `pyusb`, `linux_kernel`)
- `identifier`: Connection string
  - Network: `tcp://192.168.1.100`
  - USB: `usb://0x04f9:0x2042`
  - Serial: `file:///dev/usb/lp0`

## Usage

### Start the Server

```bash
python app.py
```

Or with environment variables:
```bash
PORT=8080 DEBUG=True python app.py
```

The server will start on `http://localhost:5000` by default.

## API Endpoints

### Health Check
```bash
GET /health
```

No authentication required.

### List Printers
```bash
GET /api/printers
Headers:
  X-API-Key: your-api-key-here
```

Returns all configured printers.

### Get Printer Details
```bash
GET /api/printers/{printer_id}
Headers:
  X-API-Key: your-api-key-here
```

### Print Text
```bash
POST /api/print
Headers:
  X-API-Key: your-api-key-here
  Content-Type: application/json

Body:
{
  "printer_id": "office-printer",
  "text": "Hello World",
  "options": {
    "font_size": 24,
    "rotate": 0,
    "cut": true,
    "margin": 10
  }
}
```

### Print Image
```bash
POST /api/print
Headers:
  X-API-Key: your-api-key-here
  Content-Type: application/json

Body:
{
  "printer_id": "office-printer",
  "image_base64": "iVBORw0KGgoAAAANSUhEUgA...",
  "options": {
    "rotate": 0,
    "cut": true,
    "margin": 10
  }
}
```

### Print PDF
```bash
POST /api/print
Headers:
  X-API-Key: your-api-key-here
  Content-Type: application/json

Body:
{
  "printer_id": "office-printer",
  "pdf_base64": "JVBERi0xLjQKJeLjz9MK...",
  "options": {
    "rotate": 0,
    "cut": true,
    "margin": 10,
    "dpi": 300
  }
}
```

**Note**: Multi-page PDFs are supported - each page will be printed as a separate label.

Response for PDF printing includes page details:
```json
{
  "success": true,
  "message": "Print job sent successfully",
  "printer_id": "office-printer",
  "pages_total": 3,
  "pages_successful": 3,
  "pages_failed": 0,
  "page_results": [
    {"page": 1, "success": true, "error": null},
    {"page": 2, "success": true, "error": null},
    {"page": 3, "success": true, "error": null}
  ]
}
```

### Discover Printers
```bash
GET /api/discover
Headers:
  X-API-Key: your-api-key-here
```

Discovers Brother printers on the network.

## API Examples

### Using curl

**Print text:**
```bash
curl -X POST http://localhost:5000/api/print \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "printer_id": "office-printer",
    "text": "Test Label",
    "options": {
      "font_size": 30,
      "cut": true
    }
  }'
```

**Discover printers:**
```bash
curl http://localhost:5000/api/discover \
  -H "X-API-Key: your-api-key-here"
```

### Using Python

```python
import requests
import base64

API_URL = "http://localhost:5000"
API_KEY = "your-api-key-here"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Print text
response = requests.post(
    f"{API_URL}/api/print",
    headers=headers,
    json={
        "printer_id": "office-printer",
        "text": "Hello from Python!",
        "options": {
            "font_size": 28,
            "cut": True
        }
    }
)
print(response.json())

# Print image
with open("label.png", "rb") as f:
    image_data = base64.b64encode(f.read()).decode()

response = requests.post(
    f"{API_URL}/api/print",
    headers=headers,
    json={
        "printer_id": "office-printer",
        "image_base64": image_data,
        "options": {
            "cut": True,
            "margin": 5
        }
    }
)
print(response.json())

# Print PDF (each page becomes a separate label)
with open("document.pdf", "rb") as f:
    pdf_data = base64.b64encode(f.read()).decode()

response = requests.post(
    f"{API_URL}/api/print",
    headers=headers,
    json={
        "printer_id": "office-printer",
        "pdf_base64": pdf_data,
        "options": {
            "cut": True,
            "margin": 5,
            "dpi": 300
        }
    }
)
result = response.json()
print(f"Printed {result['pages_successful']} of {result['pages_total']} pages")
```

### Using JavaScript/Node.js

```javascript
const axios = require('axios');
const fs = require('fs');

const API_URL = 'http://localhost:5000';
const API_KEY = 'your-api-key-here';

const headers = {
  'X-API-Key': API_KEY,
  'Content-Type': 'application/json'
};

// Print text
axios.post(`${API_URL}/api/print`, {
  printer_id: 'office-printer',
  text: 'Hello from Node.js!',
  options: {
    font_size: 28,
    cut: true
  }
}, { headers })
  .then(response => console.log(response.data))
  .catch(error => console.error(error.response.data));

// Print image
const imageBuffer = fs.readFileSync('label.png');
const imageBase64 = imageBuffer.toString('base64');

axios.post(`${API_URL}/api/print`, {
  printer_id: 'office-printer',
  image_base64: imageBase64,
  options: {
    cut: true,
    margin: 5
  }
}, { headers })
  .then(response => console.log(response.data))
  .catch(error => console.error(error.response.data));
```

## Print Options

- `font_size` (int): Font size for text printing (default: 24)
- `rotate` (int): Rotation angle in degrees - 0, 90, 180, or 270 (default: 0)
- `cut` (bool): Cut the label after printing (default: true)
- `margin` (int): Margin around the content in pixels (default: 10)

## Supported Printer Models

### QL Series (Fully Supported via brother_ql) ✅

- QL-820NWB (Two-color, Network, Wireless, Bluetooth)
- QL-1115NWB (Wide format, Network, Wireless, Bluetooth)
- QL-810W (Two-color, Wireless)
- QL-800 (Two-color)
- QL-720NW (Network, Wireless)
- QL-710W (Wireless)
- QL-700
- QL-1060N (Wide format, Network)
- QL-1050 (Wide format)
- QL-580N (Network)
- QL-570
- QL-560
- QL-550
- QL-500

### PT Series (Basic Support) ⚠️

- PT-P710BT
- PT-E550W
- PT-P750W
- PT-P900
- PT-P900W
- PT-P950NW
- PT-H500
- PT-P700
- PT-P300BT

The API primarily uses the `brother_ql` library for QL series printers, which provides full support with network, USB, and serial backends. PT series support is available through alternative libraries or custom implementation.

## Environment Variables

### Server Configuration
- `PORT`: Server port (default: 5000)
- `DEBUG`: Enable debug mode (default: False)
- `CONFIG_FILE`: Path to configuration file (default: config.json)

### OpenTelemetry Configuration
- `OTEL_ENABLED`: Enable telemetry export (`true`/`false`, default: `false`)
- `OTEL_EXPORTER_OTLP_ENDPOINT`: OTLP HTTP endpoint URL
- `OTEL_EXPORTER_OTLP_HEADERS`: Headers for authentication (format: `key1=value1,key2=value2`)
- `OTEL_SERVICE_NAME`: Service name in telemetry (default: `brother-label-api`)
- `OTEL_ENVIRONMENT`: Deployment environment (default: `production`)
- `OTEL_EXPORT_INTERVAL_MS`: Metric export interval in milliseconds (default: `60000`)

See [`.env.example`](.env.example) for a complete configuration template.

## OpenTelemetry Metrics

The API includes comprehensive OpenTelemetry instrumentation for monitoring and observability. Metrics are exported via OTLP HTTP protocol, compatible with Grafana Cloud, Datadog, New Relic, and other observability platforms.

### Enabling Telemetry

1. **Set environment variables**:
```bash
export OTEL_ENABLED=true
export OTEL_EXPORTER_OTLP_ENDPOINT=https://otlp-gateway-prod-us-central-0.grafana.net/otlp
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Bearer <your-token>"
```

2. **Or use a `.env` file**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

### Metrics Collected

#### Counters (always increasing)
- `api.requests.total` - Total API requests
  - Labels: `endpoint`, `method`, `status_code`, `api_key_name`
- `prints.total` - Total print jobs attempted
  - Labels: `printer_id`, `printer_model`, `label_type`, `api_key_name`
- `prints.success` - Successful print jobs
  - Labels: `printer_id`, `printer_model`, `label_type`, `api_key_name`
- `prints.failed` - Failed print jobs
  - Labels: `printer_id`, `printer_model`, `error_type`, `api_key_name`
- `errors.total` - Total errors by type
  - Labels: `error_type`, `endpoint`, `api_key_name`

#### Histograms (distribution of values)
- `http.request.duration` - HTTP request duration (ms)
  - Labels: `endpoint`, `method`, `status_code`
- `print.duration` - Print job duration (ms)
  - Labels: `printer_id`, `printer_model`, `result`
- `image.generation.duration` - Label image generation time (ms)
  - Labels: `label_type`
- `printer.response.time` - Printer response time (ms)
  - Labels: `printer_id`, `printer_model`

#### Gauges (current value)
- `printers.configured` - Number of configured printers
- `api_keys.configured` - Number of configured API keys

### Grafana Cloud Example

```bash
# 1. Get your Grafana Cloud credentials
# - Endpoint: https://otlp-gateway-prod-<region>.grafana.net/otlp
# - Token: From Grafana Cloud → Configuration → API Keys

# 2. Set environment variables
export OTEL_ENABLED=true
export OTEL_EXPORTER_OTLP_ENDPOINT=https://otlp-gateway-prod-us-central-0.grafana.net/otlp
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Bearer glc_<your-token>"
export OTEL_SERVICE_NAME=brother-label-api
export OTEL_ENVIRONMENT=production

# 3. Start the server
python app.py
```

### Privacy & Security

The telemetry implementation is designed with privacy in mind:
- ✅ **API key names** are included (e.g., "production-app") for tracking
- ❌ **API key values** are never sent
- ❌ **Label content** (text/images) is never sent
- ✅ **Printer metadata** (ID, model) is included for diagnostics
- ✅ **Error types** and metrics are included for monitoring

### Disabling Telemetry

Telemetry is **disabled by default**. To keep it disabled:
- Don't set `OTEL_ENABLED=true`
- Or explicitly set `OTEL_ENABLED=false`

When disabled, the API uses no-op metrics collectors with zero performance impact.

## Docker Deployment

For production or to avoid Python version issues, use Docker:

### Using Docker Compose (Recommended)

```bash
# Create config.json first
cp config.example.json config.json
# Edit config.json with your settings

# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

### Using Docker Directly

```bash
# Build image
docker build -t brother-label-api .

# Run container
docker run -d \
  --name brother-label-api \
  -p 5000:5000 \
  -v $(pwd)/config.json:/app/config/config.json:ro \
  brother-label-api

# View logs
docker logs -f brother-label-api
```

The Docker image uses Python 3.11 for maximum stability and compatibility.

## Security Considerations

1. Keep your `config.json` file secure and never commit it to version control
2. Use strong, randomly generated API keys
3. Consider using HTTPS in production (use a reverse proxy like nginx)
4. Restrict network access to the API server
5. Regularly rotate API keys

## Troubleshooting

### Printer not found
- Verify the printer is powered on and connected to the network
- Check the IP address or USB identifier in `config.json`
- Use the `/api/discover` endpoint to find network printers

### brother_ql library errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- For USB printers, you may need to install libusb drivers
- Check printer model compatibility

### Permission errors (Linux)
For USB printers, you may need to add udev rules:
```bash
echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="04f9", MODE="0666"' | sudo tee /etc/udev/rules.d/99-brother-printer.rules
sudo udevadm control --reload-rules
```

## Development

To run in development mode:
```bash
DEBUG=True python app.py
```

## License

MIT License - See LICENSE file for details

## Credits

Based on the original `brother_pt` CLI tool by treideme, modernized into a REST API with updated dependencies.

Uses the `brother_ql` library for printer communication.
