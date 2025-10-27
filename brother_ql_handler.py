"""
Brother QL/PT printer handler
Implements the printing logic with support for multiple Brother printer libraries
Supports: brother_ql (for QL series), labelprinterkit (for PT series)
"""

import base64
import io
import tempfile
import os
import socket
from typing import Dict, List, Optional
from PIL import Image, ImageDraw, ImageFont


class BrotherQLHandler:
    """Handles Brother QL/PT/QL printer operations with multiple backend support"""

    def __init__(self):
        """Initialize the Brother QL/PT handler and detect available libraries"""
        # Supported PT series models
        self.supported_pt_models = [
            'PT-P710BT', 'PT-E550W', 'PT-P750W', 'PT-P900',
            'PT-P900W', 'PT-P950NW', 'PT-H500', 'PT-P700', 'PT-P300BT'
        ]

        # Supported QL series models (compatible with brother_ql)
        self.supported_ql_models = [
            'QL-500', 'QL-550', 'QL-560', 'QL-570', 'QL-580N', 'QL-650TD',
            'QL-700', 'QL-710W', 'QL-720NW', 'QL-800', 'QL-810W', 'QL-820NWB',
            'QL-1050', 'QL-1060N', 'QL-1100', 'QL-1115NWB'
        ]

        self.supported_models = self.supported_pt_models + self.supported_ql_models

        # Detect available printer libraries
        self.has_brother_ql = self._check_brother_ql()
        self.has_labelprinterkit = self._check_labelprinterkit()

    def _check_brother_ql(self) -> bool:
        """Check if brother_ql library is available"""
        try:
            import brother_ql
            return True
        except ImportError:
            return False

    def _check_labelprinterkit(self) -> bool:
        """Check if labelprinterkit is available"""
        try:
            import labelprinterkit
            return True
        except ImportError:
            return False

    def print_text(
        self,
        printer: Dict,
        text: str,
        font_size: int = 24,
        rotate: int = 0,
        cut: bool = True,
        margin: int = 10
    ) -> Dict:
        """
        Print text on a Brother QL/PT printer

        Args:
            printer: Printer configuration dict
            text: Text to print
            font_size: Font size in points
            rotate: Rotation angle (0, 90, 180, 270)
            cut: Whether to cut the label after printing
            margin: Margin in pixels

        Returns:
            Dict with success status and optional error message
        """
        try:
            # Create image from text
            image = self._text_to_image(text, font_size, margin)

            # Rotate if needed
            if rotate in [90, 180, 270]:
                image = image.rotate(rotate, expand=True)

            # Convert image to base64 for consistency with image printing
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

            # Use the print_image method
            return self.print_image(printer, image_base64, rotate=0, cut=cut, margin=0)

        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to print text: {str(e)}'
            }

    def print_image(
        self,
        printer: Dict,
        image_base64: str,
        rotate: int = 0,
        cut: bool = True,
        margin: int = 10
    ) -> Dict:
        """
        Print an image on a Brother QL/PT/QL printer

        Args:
            printer: Printer configuration dict
            image_base64: Base64 encoded image
            rotate: Rotation angle (0, 90, 180, 270)
            cut: Whether to cut the label after printing
            margin: Margin in pixels

        Returns:
            Dict with success status and optional error message
        """
        try:
            # Decode base64 image
            image_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_data))

            # Rotate if needed
            if rotate in [90, 180, 270]:
                image = image.rotate(rotate, expand=True)

            # Convert to black and white
            image = image.convert('1')

            # Add margin
            if margin > 0:
                image = self._add_margin(image, margin)

            # Get printer connection details
            backend = printer.get('backend', 'network')
            identifier = printer.get('identifier')
            model = printer.get('model', 'QL-820NWB')
            label_size = printer.get('label_size', '62')

            if not identifier:
                return {
                    'success': False,
                    'error': 'Printer identifier not specified'
                }

            # Determine which library to use based on model
            is_ql_model = any(model.startswith(ql) for ql in ['QL-'])

            if is_ql_model and self.has_brother_ql:
                return self._print_with_brother_ql(
                    image, identifier, model, backend, label_size, cut, rotate
                )
            elif not is_ql_model and self.has_labelprinterkit:
                return self._print_with_labelprinterkit(
                    image, identifier, model, backend, cut
                )
            else:
                # Fallback to raw ESC/P commands
                return self._print_raw(image, identifier, model, backend, cut)

        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to print image: {str(e)}'
            }

    def _print_with_brother_ql(
        self,
        image: Image.Image,
        identifier: str,
        model: str,
        backend: str,
        label_size: str,
        cut: bool,
        rotate: int
    ) -> Dict:
        """Print using the brother_ql library"""
        try:
            from brother_ql.conversion import convert
            from brother_ql.backends.helpers import send
            from brother_ql.raster import BrotherQLRaster

            # Create raster instructions
            qlr = BrotherQLRaster(model)
            instructions = convert(
                qlr=qlr,
                images=[image],
                label=label_size,
                rotate='auto' if rotate == 0 else str(rotate),
                threshold=70.0,
                dither=False,
                compress=False,
                red=False,
                dpi_600=False,
                hq=True,
                cut=cut
            )

            # Send to printer
            send(
                instructions=instructions,
                printer_identifier=identifier,
                backend_identifier=backend,
                blocking=True
            )

            return {
                'success': True,
                'message': 'Print job sent successfully via brother_ql'
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'brother_ql print failed: {str(e)}'
            }

    def _print_with_labelprinterkit(
        self,
        image: Image.Image,
        identifier: str,
        model: str,
        backend: str,
        cut: bool
    ) -> Dict:
        """Print using the labelprinterkit library (for PT series)"""
        try:
            # labelprinterkit is more complex and model-specific
            # This is a placeholder for future implementation
            return {
                'success': False,
                'error': 'labelprinterkit integration not yet implemented'
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'labelprinterkit print failed: {str(e)}'
            }

    def _print_raw(
        self,
        image: Image.Image,
        identifier: str,
        model: str,
        backend: str,
        cut: bool
    ) -> Dict:
        """
        Fallback: Send raw raster data to printer via TCP
        This implements a basic version of the Brother raster protocol
        """
        try:
            if not identifier.startswith('tcp://'):
                return {
                    'success': False,
                    'error': 'Raw printing only supports TCP connections. Install brother_ql for other backends.'
                }

            # Extract host and port
            host_port = identifier.replace('tcp://', '')
            if ':' in host_port:
                host, port = host_port.rsplit(':', 1)
                port = int(port)
            else:
                host = host_port
                port = 9100  # Default Brother printer port

            # Convert image to raster data
            width, height = image.size

            # Simple raster command sequence (basic Brother ESC/P)
            commands = bytearray()

            # Initialize
            commands.extend(b'\x1B\x40')  # ESC @ - Initialize

            # For now, return error suggesting proper library
            return {
                'success': False,
                'error': (
                    'No compatible printer library installed. '
                    'Please install: pip install brother_ql (for QL models) '
                    'or pip install labelprinterkit (for PT models)'
                )
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Raw print failed: {str(e)}'
            }

    def discover_printers(self) -> List[Dict]:
        """
        Discover Brother QL/PT/QL printers on the network

        Returns:
            List of discovered printers with their details
        """
        discovered = []

        try:
            from brother_ql.backends.helpers import discover

            # Discover network printers
            network_devices = discover(backend_identifier='network')

            for device in network_devices:
                discovered.append({
                    'backend': 'network',
                    'identifier': device['identifier'],
                    'model': device.get('model', 'Unknown'),
                    'note': 'Discovered via network'
                })

        except ImportError:
            pass
        except Exception as e:
            print(f"Error during discovery: {str(e)}")

        return discovered

    def _text_to_image(self, text: str, font_size: int, margin: int) -> Image.Image:
        """Convert text to an image"""
        # Try to use a nice font, fallback to default
        try:
            # Try common font locations
            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "C:\\Windows\\Fonts\\arial.ttf",
                "/System/Library/Fonts/Helvetica.ttc"
            ]

            font = None
            for path in font_paths:
                if os.path.exists(path):
                    font = ImageFont.truetype(path, font_size)
                    break

            if font is None:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()

        # Create a temporary image to calculate text size
        temp_img = Image.new('RGB', (1, 1), color='white')
        temp_draw = ImageDraw.Draw(temp_img)

        # Get text bounding box
        bbox = temp_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Create final image with margins
        img_width = text_width + (margin * 2)
        img_height = text_height + (margin * 2)

        image = Image.new('RGB', (img_width, img_height), color='white')
        draw = ImageDraw.Draw(image)

        # Draw text centered
        draw.text((margin, margin), text, fill='black', font=font)

        return image

    def _add_margin(self, image: Image.Image, margin: int) -> Image.Image:
        """Add white margin around an image"""
        new_width = image.width + (margin * 2)
        new_height = image.height + (margin * 2)

        new_image = Image.new('1', (new_width, new_height), color=1)  # 1 = white in binary
        new_image.paste(image, (margin, margin))

        return new_image
