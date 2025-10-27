# Brother Label API - Project Summary

## What We Built

A modern REST API for Brother PT/QL label printers that replaces the outdated CLI tool from https://github.com/treideme/brother_pt.

## Key Features

### REST API
- ✅ HTTP-based service (not CLI)
- ✅ API key authentication
- ✅ Multiple printer support via JSON config
- ✅ Print text with custom fonts
- ✅ Print images (base64 encoded)
- ✅ Network printer discovery
- ✅ Rotation, margins, auto-cut options

### Printer Support
- ✅ **QL Series**: Full support (QL-820NWB, QL-810W, QL-700, etc.)
- ⚠️ **PT Series**: Basic support (PT-P710BT, PT-P750W, etc.)
- ✅ Network (TCP), USB, and serial backends

### Python Compatibility
- ✅ **Python 3.9-3.14+**: Fully supported
- ✅ **Bundled fixed brother_ql**: Works with all versions
- ✅ **No python-future dependency**: Clean modern Python

## Project Structure

```
brother-label-api/
├── app.py                      # Main Flask REST API server
├── brother_pt_handler.py       # Printer communication logic
├── printer_manager.py          # Configuration & API key management
├── brother_ql_fixed/           # Bundled fixed brother_ql package ⭐
│   ├── brother_ql/             # Fixed source code
│   ├── setup.py                # No python-future dependency
│   └── README.md               # Fix documentation
├── requirements-fixed.txt      # Recommended (Python 3.9-3.14+)
├── requirements.txt            # Original (Python 3.9-3.11)
├── requirements-py312.txt      # Alternative fork option
├── config.example.json         # Printer configuration template
├── test_printer.py             # Installation verification
├── Dockerfile                  # Docker deployment
├── docker-compose.yml          # Docker Compose setup
├── README.md                   # Main documentation
├── QUICKSTART.md               # 5-minute setup guide
├── COMPATIBILITY.md            # Detailed compatibility info
├── PYTHON312_FIX.md            # Python 3.12+ fix guide
└── WHY_NOT_FORK.md             # Why we bundled the fix
```

## The Python 3.12+ Fix

### Problem
The original `brother_ql` library depends on `python-future`, created in 2013 for Python 2/3 compatibility. This package:
- Is obsolete (Python 2 EOL in 2020)
- Breaks on Python 3.13
- Prevents modern Python usage

### Our Solution
We bundled a fixed version of `brother_ql` in `brother_ql_fixed/` that:
1. ✅ Removes `python-future` dependency
2. ✅ Removes Python 2 compatibility code
3. ✅ Removes `from __future__ import` statements
4. ✅ Preserves ALL functionality
5. ✅ Works with Python 3.9-3.14+

### Installation
```bash
pip install -r requirements-fixed.txt
```

That's it! No extra steps, no patching scripts, no workarounds needed.

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Health check |
| `/api/printers` | GET | List all configured printers |
| `/api/printers/{id}` | GET | Get specific printer details |
| `/api/print` | POST | Print text or image |
| `/api/discover` | GET | Discover network printers |

## Example Usage

### Print Text
```bash
curl -X POST http://localhost:5000/api/print \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "printer_id": "office-printer",
    "text": "Hello World",
    "options": {"font_size": 36, "cut": true}
  }'
```

### Print Image
```python
import requests, base64

with open("label.png", "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode()

requests.post("http://localhost:5000/api/print",
    headers={"X-API-Key": "your-key"},
    json={
        "printer_id": "office-printer",
        "image_base64": image_b64,
        "options": {"cut": True}
    })
```

## Deployment Options

### Option 1: Direct Python (Recommended)
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements-fixed.txt
python app.py
```

### Option 2: Docker
```bash
docker-compose up -d
```

### Option 3: Docker Manual
```bash
docker build -t brother-label-api .
docker run -p 5000:5000 -v ./config.json:/app/config/config.json brother-label-api
```

## Configuration

[config.json](config.json):
```json
{
  "api_keys": ["your-secret-key"],
  "printers": [
    {
      "id": "office-printer",
      "name": "Office QL-820NWB",
      "model": "QL-820NWB",
      "backend": "network",
      "identifier": "tcp://192.168.1.100",
      "label_size": "62"
    }
  ]
}
```

## Documentation Files

| File | Purpose |
|---|---|
| **README.md** | Main documentation with API examples |
| **QUICKSTART.md** | 5-minute getting started guide |
| **COMPATIBILITY.md** | Python version compatibility details |
| **PYTHON312_FIX.md** | Detailed Python 3.12+ fix explanation |
| **brother_ql_fixed/README.md** | Fixed brother_ql package documentation |
| **WHY_NOT_FORK.md** | Why we bundled vs external fork |

## Key Improvements Over Original

| Feature | Original brother_pt | This Project |
|---|---|---|
| **Interface** | CLI | REST API ✅ |
| **Python 3.12+** | ❌ Broken | ✅ Works |
| **Python 3.13+** | ❌ Broken | ✅ Works |
| **python-future** | Required | ✅ Removed |
| **Multiple Printers** | Single | ✅ JSON config |
| **Authentication** | None | ✅ API keys |
| **Text Printing** | Images only | ✅ Direct text |
| **Image Printing** | CLI | ✅ Base64 API |
| **Docker Support** | No | ✅ Included |
| **Documentation** | Basic | ✅ Comprehensive |

## Testing

```bash
# Test installation
python test_printer.py

# Test API
curl http://localhost:5000/health

# Test printing
curl -X POST http://localhost:5000/api/print \
  -H "X-API-Key: your-key" \
  -d '{"printer_id":"test", "text":"Test"}'
```

## Requirements

- Python 3.9-3.14+
- Brother QL or PT series printer
- Network connectivity to printer

## License

- **This project**: MIT License
- **brother_ql (bundled)**: GPL License (from original)

## Credits

- **Original brother_pt**: https://github.com/treideme/brother_pt
- **brother_ql library**: https://github.com/pklaus/brother_ql (Philipp Klaus)
- **Python 3.12+ fix**: Bundled in this project
- **REST API**: Built for this project

## Quick Start Summary

1. **Install**:
   ```bash
   pip install -r requirements-fixed.txt
   ```

2. **Configure**:
   ```bash
   cp config.example.json config.json
   # Edit with your printers
   ```

3. **Run**:
   ```bash
   python app.py
   ```

4. **Test**:
   ```bash
   curl http://localhost:5000/health
   ```

That's it! 🎉

## Why This Project?

The original `brother_pt` was:
- Outdated (doesn't work with latest packages)
- CLI only (not API-friendly)
- Python 3.12+ incompatible

This project:
- ✅ Works with modern Python (3.9-3.14+)
- ✅ Provides REST API
- ✅ Bundles fixed dependencies
- ✅ Supports multiple printers
- ✅ Well documented
- ✅ Production ready

## Support & Issues

- Check [COMPATIBILITY.md](COMPATIBILITY.md) for common issues
- Review [QUICKSTART.md](QUICKSTART.md) for setup help
- See [brother_ql_fixed/README.md](brother_ql_fixed/README.md) for library details

## Future Enhancements

Potential improvements:
- [ ] Enhanced PT series support
- [ ] QR code generation
- [ ] Barcode support
- [ ] Template system
- [ ] Web UI
- [ ] Print queue management
- [ ] Printer status monitoring

## Summary

This is a **modern, working, Python 3.13-compatible REST API** for Brother label printers that bundles all necessary fixes and works out of the box. No complicated setup, no version juggling, just install and use!
