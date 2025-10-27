"""
Brother QL/PT Label Printer REST API
A Flask-based REST API for controlling Brother QL/PT label printers
"""

from flask import Flask, request, jsonify
from functools import wraps
import json
import os
from printer_manager import PrinterManager
from brother_ql_handler import BrotherQLHandler

app = Flask(__name__)

# Load configuration
CONFIG_FILE = os.getenv('CONFIG_FILE', 'config.json')
printer_manager = PrinterManager(CONFIG_FILE)
ql_handler = BrotherQLHandler()


def require_api_key(f):
    """Decorator to validate API key"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')

        if not api_key:
            return jsonify({'error': 'API key is missing'}), 401

        if not printer_manager.validate_api_key(api_key):
            return jsonify({'error': 'Invalid API key'}), 403

        return f(*args, **kwargs)

    return decorated_function


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'brother-label-api'}), 200


@app.route('/api/printers', methods=['GET'])
@require_api_key
def list_printers():
    """List all configured printers"""
    printers = printer_manager.get_all_printers()
    return jsonify({'printers': printers}), 200


@app.route('/api/printers/<printer_id>', methods=['GET'])
@require_api_key
def get_printer(printer_id):
    """Get details of a specific printer"""
    printer = printer_manager.get_printer(printer_id)

    if not printer:
        return jsonify({'error': 'Printer not found'}), 404

    return jsonify({'printer': printer}), 200


@app.route('/api/print', methods=['POST'])
@require_api_key
def print_label():
    """
    Print a label on a Brother QL/PT printer

    Expected JSON payload:
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

    Or with image:
    {
        "printer_id": "office-printer",
        "image_base64": "base64_encoded_image_data",
        "options": {
            "rotate": 0,
            "cut": true,
            "margin": 10
        }
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        printer_id = data.get('printer_id')
        if not printer_id:
            return jsonify({'error': 'printer_id is required'}), 400

        # Get printer configuration
        printer = printer_manager.get_printer(printer_id)
        if not printer:
            return jsonify({'error': f'Printer {printer_id} not found'}), 404

        # Extract print options
        options = data.get('options', {})

        # Handle text or image based printing
        if 'text' in data:
            result = ql_handler.print_text(
                printer=printer,
                text=data['text'],
                font_size=options.get('font_size', 24),
                rotate=options.get('rotate', 0),
                cut=options.get('cut', True),
                margin=options.get('margin', 10)
            )
        elif 'image_base64' in data:
            result = ql_handler.print_image(
                printer=printer,
                image_base64=data['image_base64'],
                rotate=options.get('rotate', 0),
                cut=options.get('cut', True),
                margin=options.get('margin', 10)
            )
        else:
            return jsonify({'error': 'Either text or image_base64 is required'}), 400

        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Print job sent successfully',
                'printer_id': printer_id
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error')
            }), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/discover', methods=['GET'])
@require_api_key
def discover_printers():
    """Discover Brother QL/PT printers on the network"""
    try:
        printers = ql_handler.discover_printers()
        return jsonify({'discovered': printers}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'

    print(f"Starting Brother Label API API on port {port}")
    print(f"Loaded {len(printer_manager.get_all_printers())} configured printers")

    app.run(host='0.0.0.0', port=port, debug=debug)
