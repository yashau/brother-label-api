"""
Printer configuration manager
Handles loading printers from config and API key validation
"""

import json
import os
from typing import Dict, List, Optional


class PrinterManager:
    """Manages printer configurations and API key validation"""

    def __init__(self, config_file: str = 'config.json'):
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load configuration from JSON file"""
        if not os.path.exists(self.config_file):
            # Create default config if it doesn't exist
            default_config = {
                "api_keys": ["your-api-key-here"],
                "printers": []
            }
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config

        with open(self.config_file, 'r') as f:
            return json.load(f)

    def validate_api_key(self, api_key: str) -> bool:
        """Validate if the provided API key is authorized"""
        return api_key in self.config.get('api_keys', [])

    def get_all_printers(self) -> List[Dict]:
        """Get all configured printers"""
        return self.config.get('printers', [])

    def get_printer(self, printer_id: str) -> Optional[Dict]:
        """Get a specific printer by ID or name"""
        printers = self.config.get('printers', [])

        for printer in printers:
            if printer.get('id') == printer_id or printer.get('name') == printer_id:
                return printer

        return None

    def add_printer(self, printer: Dict) -> bool:
        """Add a new printer to configuration"""
        if 'id' not in printer:
            return False

        # Check if printer already exists
        if self.get_printer(printer['id']):
            return False

        self.config['printers'].append(printer)
        self._save_config()
        return True

    def remove_printer(self, printer_id: str) -> bool:
        """Remove a printer from configuration"""
        printers = self.config.get('printers', [])
        original_length = len(printers)

        self.config['printers'] = [
            p for p in printers
            if p.get('id') != printer_id and p.get('name') != printer_id
        ]

        if len(self.config['printers']) < original_length:
            self._save_config()
            return True

        return False

    def _save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
