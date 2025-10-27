#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify Brother Label API installation
Run this before starting the API server
"""

import sys
import os

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    if sys.stdout.encoding != 'utf-8':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_installation():
    """Test all required dependencies"""
    print("Brother Label API - Installation Test")
    print("=" * 50)
    print(f"Python version: {sys.version}")
    print()

    all_ok = True

    # Test brother_ql
    print("[1/5] Testing brother_ql library...")
    try:
        import brother_ql
        version = getattr(brother_ql, '__version__', 'version unknown')
        print(f"  ✓ brother_ql installed: {version}")

        # Verify it's the fixed version
        if version == '0.9.5.1':
            print(f"  ✓ Using FIXED version (bundled in this project)")
        elif version in ('0.9.5', '0.9.4', '0.9.dev0'):
            print(f"  ⚠ WARNING: Using OLD/WRONG version from PyPI (not the fixed version)")
            print(f"  → Reinstall with: pip install -r requirements.txt")
            all_ok = False
        else:
            print(f"  ⚠ WARNING: Unknown version: {version}")
            print(f"  → Expected version: 0.9.5.1 (fixed version)")
            all_ok = False

        # Check for python-future dependency (should NOT be present)
        try:
            import future
            print(f"  ⚠ WARNING: python-future is installed (should not be needed)")
        except ImportError:
            print(f"  ✓ python-future not installed (correct!)")

        from brother_ql.raster import BrotherQLRaster
        from brother_ql.conversion import convert

        # Test common QL model support
        try:
            qlr = BrotherQLRaster('QL-820NWB')
            print(f"  ✓ QL series models supported")
        except Exception as e:
            print(f"  ⚠ QL-820NWB test failed: {e}")

    except ImportError as e:
        print(f"  ✗ brother_ql not available: {e}")
        print(f"  → Install with: pip install -r requirements.txt")
        all_ok = False
    except Exception as e:
        print(f"  ✗ brother_ql error: {e}")
        all_ok = False

    print()

    # Test Pillow
    print("[2/5] Testing Pillow (PIL) library...")
    try:
        import PIL
        from PIL import Image, ImageDraw, ImageFont
        print(f"  ✓ Pillow installed: {PIL.__version__}")

        # Test image creation
        img = Image.new('RGB', (100, 50), color='white')
        print(f"  ✓ Image creation works")

    except ImportError as e:
        print(f"  ✗ Pillow not available: {e}")
        print(f"  → Install with: pip install Pillow")
        all_ok = False
    except Exception as e:
        print(f"  ✗ Pillow error: {e}")
        all_ok = False

    print()

    # Test Flask
    print("[3/5] Testing Flask framework...")
    try:
        import flask
        try:
            from importlib.metadata import version
            flask_version = version('flask')
        except Exception:
            flask_version = getattr(flask, '__version__', 'unknown')
        print(f"  ✓ Flask installed: {flask_version}")

        from flask import Flask, request, jsonify
        print(f"  ✓ Flask imports work")

    except ImportError as e:
        print(f"  ✗ Flask not available: {e}")
        print(f"  → Install with: pip install Flask")
        all_ok = False
    except Exception as e:
        print(f"  ✗ Flask error: {e}")
        all_ok = False

    print()

    # Test labelprinterkit (optional)
    print("[4/5] Testing labelprinterkit (optional for PT series)...")
    try:
        import labelprinterkit
        print(f"  ✓ labelprinterkit installed")
    except ImportError:
        print(f"  ℹ labelprinterkit not installed (only needed for PT series)")
        print(f"  → Optional install: pip install labelprinterkit")

    print()

    # Test config file
    print("[5/5] Testing configuration...")
    if os.path.exists('config.json'):
        print(f"  ✓ config.json exists")
        try:
            import json
            with open('config.json', 'r') as f:
                config = json.load(f)

            if 'api_keys' in config and len(config['api_keys']) > 0:
                # Check if using new format with named keys
                first_key = config['api_keys'][0]
                if isinstance(first_key, dict):
                    # New format: {"name": "...", "key": "..."}
                    if first_key.get('key') == 'your-api-key-here':
                        print(f"  ⚠ Using default API key - please change it!")
                    else:
                        print(f"  ✓ API keys configured ({len(config['api_keys'])} key(s))")
                        # Show key names
                        for key_obj in config['api_keys']:
                            if isinstance(key_obj, dict):
                                name = key_obj.get('name', 'unnamed')
                                print(f"     - {name}")
                else:
                    print(f"  ⚠ Old API key format detected - please update to new format")
                    print(f"  → See README.md for new format with names")
            else:
                print(f"  ⚠ No API keys found in config.json")

            if 'printers' in config:
                print(f"  ✓ {len(config['printers'])} printer(s) configured")
                for printer in config['printers']:
                    model = printer.get('model', 'Unknown')
                    identifier = printer.get('identifier', 'No identifier')
                    print(f"     - {model}: {identifier}")
            else:
                print(f"  ⚠ No printers configured")

        except Exception as e:
            print(f"  ✗ Error reading config.json: {e}")
            all_ok = False
    else:
        print(f"  ⚠ config.json not found")
        print(f"  → Create one with: cp config.example.json config.json")

    print()
    print("=" * 50)

    if all_ok:
        print("✅ All required dependencies are installed!")
        print()
        print("Next steps:")
        print("1. Configure your printers in config.json")
        print("2. Start the server: python app.py")
        print("3. Test the API: curl http://localhost:5000/health")
        return 0
    else:
        print("❌ Some required dependencies are missing")
        print()
        print("Install all dependencies with:")
        print("  pip install -r requirements.txt")
        return 1


if __name__ == '__main__':
    sys.exit(test_installation())
