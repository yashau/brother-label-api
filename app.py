"""
Brother QL/PT Label Printer REST API
A Flask-based REST API for controlling Brother QL/PT label printers
"""

from flask import Flask, request, jsonify, g
from functools import wraps
import json
import os
import time
from printer_manager import PrinterManager
from brother_ql_handler import BrotherQLHandler
from telemetry import init_telemetry, get_telemetry

app = Flask(__name__)

# Load configuration
CONFIG_FILE = os.getenv('CONFIG_FILE', 'config.json')
printer_manager = PrinterManager(CONFIG_FILE)
ql_handler = BrotherQLHandler()

# Initialize telemetry
telemetry = init_telemetry()

# Update config gauges
telemetry.update_config_gauges(
    printers_count=len(printer_manager.get_all_printers()),
    api_keys_count=len(printer_manager._api_key_map)
)


@app.before_request
def before_request():
    """Store request start time for metrics"""
    g.start_time = time.time()


@app.after_request
def after_request(response):
    """Record request metrics after each request"""
    if hasattr(g, 'start_time'):
        duration_ms = (time.time() - g.start_time) * 1000

        # Get endpoint (route pattern) for better grouping
        endpoint = request.endpoint or request.path

        telemetry.record_http_duration(
            duration_ms=duration_ms,
            endpoint=endpoint,
            method=request.method,
            status_code=response.status_code
        )

        # Record API request counter
        api_key_name = g.get('api_key_name')
        telemetry.record_api_request(
            endpoint=endpoint,
            method=request.method,
            status_code=response.status_code,
            api_key_name=api_key_name
        )

    return response


def require_api_key(f):
    """Decorator to validate API key and store context"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')

        if not api_key:
            telemetry.record_error('missing_api_key', request.endpoint or request.path)
            return jsonify({'error': 'API key is missing'}), 401

        if not printer_manager.validate_api_key(api_key):
            telemetry.record_error('invalid_api_key', request.endpoint or request.path)
            return jsonify({'error': 'Invalid API key'}), 403

        # Store API key name in Flask's g object for use in request handlers
        g.api_key_name = printer_manager.get_api_key_name(api_key)
        g.api_key = api_key  # Store actual key (useful for logging but be careful not to expose)

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

    Supports text, images, and PDFs (multi-page PDFs print each page as a separate label)

    Text printing:
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

    Image printing:
    {
        "printer_id": "office-printer",
        "image_base64": "base64_encoded_image_data",
        "options": {
            "rotate": 0,
            "cut": true,
            "margin": 10
        }
    }

    PDF printing (each page = one label):
    {
        "printer_id": "office-printer",
        "pdf_base64": "base64_encoded_pdf_data",
        "options": {
            "rotate": 0,
            "cut": true,
            "margin": 10,
            "dpi": 300
        }
    }
    """
    print_start_time = time.time()
    printer_id = None
    printer_model = None
    label_type = None
    api_key_name = g.get('api_key_name')

    try:
        data = request.get_json()

        if not data:
            telemetry.record_error('no_json_data', 'print_label', api_key_name)
            return jsonify({'error': 'No JSON data provided'}), 400

        printer_id = data.get('printer_id')
        if not printer_id:
            telemetry.record_error('missing_printer_id', 'print_label', api_key_name)
            return jsonify({'error': 'printer_id is required'}), 400

        # Get printer configuration
        printer = printer_manager.get_printer(printer_id)
        if not printer:
            telemetry.record_error('printer_not_found', 'print_label', api_key_name)
            return jsonify({'error': f'Printer {printer_id} not found'}), 404

        printer_model = printer.get('model', 'unknown')

        # Determine label type
        label_type = 'text' if 'text' in data else 'image' if 'image_base64' in data else 'unknown'

        # Record print attempt
        telemetry.record_print_attempt(
            printer_id=printer_id,
            printer_model=printer_model,
            label_type=label_type,
            api_key_name=api_key_name
        )

        # Extract print options
        options = data.get('options', {})

        # Handle text, image, or PDF based printing
        if 'text' in data:
            # Measure image generation time
            image_gen_start = time.time()
            result = ql_handler.print_text(
                printer=printer,
                text=data['text'],
                font_size=options.get('font_size', 24),
                rotate=options.get('rotate', 0),
                cut=options.get('cut', True),
                margin=options.get('margin', 10)
            )
            image_gen_duration = (time.time() - image_gen_start) * 1000
            telemetry.record_image_generation(image_gen_duration, 'text')

        elif 'image_base64' in data:
            image_gen_start = time.time()
            result = ql_handler.print_image(
                printer=printer,
                image_base64=data['image_base64'],
                rotate=options.get('rotate', 0),
                cut=options.get('cut', True),
                margin=options.get('margin', 10)
            )
            image_gen_duration = (time.time() - image_gen_start) * 1000
            telemetry.record_image_generation(image_gen_duration, 'image')

        elif 'pdf_base64' in data:
            image_gen_start = time.time()
            result = ql_handler.print_pdf(
                printer=printer,
                pdf_base64=data['pdf_base64'],
                rotate=options.get('rotate', 0),
                cut=options.get('cut', True),
                margin=options.get('margin', 10),
                dpi=options.get('dpi', 300)
            )
            image_gen_duration = (time.time() - image_gen_start) * 1000
            telemetry.record_image_generation(image_gen_duration, 'pdf')

        else:
            telemetry.record_error('invalid_print_data', 'print_label', api_key_name)
            return jsonify({'error': 'Either text, image_base64, or pdf_base64 is required'}), 400

        # Calculate total print duration
        print_duration_ms = (time.time() - print_start_time) * 1000

        if result['success']:
            # Record success metrics
            telemetry.record_print_success(
                printer_id=printer_id,
                printer_model=printer_model,
                label_type=label_type,
                duration_ms=print_duration_ms,
                api_key_name=api_key_name
            )

            response_data = {
                'success': True,
                'message': 'Print job sent successfully',
                'printer_id': printer_id
            }

            # Add PDF-specific info if available
            if 'pages_total' in result:
                response_data['pages_total'] = result['pages_total']
                response_data['pages_successful'] = result['pages_successful']
                response_data['pages_failed'] = result['pages_failed']
                if result.get('page_results'):
                    response_data['page_results'] = result['page_results']

            return jsonify(response_data), 200
        else:
            # Record failure metrics
            error_type = result.get('error_type', 'unknown_error')
            telemetry.record_print_failure(
                printer_id=printer_id,
                printer_model=printer_model,
                error_type=error_type,
                duration_ms=print_duration_ms,
                api_key_name=api_key_name
            )
            telemetry.record_error(error_type, 'print_label', api_key_name)

            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error')
            }), 500

    except Exception as e:
        # Record exception
        print_duration_ms = (time.time() - print_start_time) * 1000

        if printer_id and printer_model:
            telemetry.record_print_failure(
                printer_id=printer_id,
                printer_model=printer_model,
                error_type='exception',
                duration_ms=print_duration_ms,
                api_key_name=api_key_name
            )

        telemetry.record_error('exception', 'print_label', api_key_name)
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

    print(f"Starting Brother Label API on port {port}")
    print(f"Loaded {len(printer_manager.get_all_printers())} configured printers")
    print(f"Loaded {len(printer_manager._api_key_map)} configured API keys")

    if telemetry.enabled:
        print(f"✓ Telemetry enabled - exporting to {os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT')}")
    else:
        print("✗ Telemetry disabled (set OTEL_ENABLED=true to enable)")

    app.run(host='0.0.0.0', port=port, debug=debug)
