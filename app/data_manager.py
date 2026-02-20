import json
import os
import threading
from datetime import datetime


class DataManager:
    """
    Manages inventory data stored in a JSON file.
    Thread-safe operations for concurrent access.
    No database required - all data persisted in JSON.
    """

    _lock = threading.Lock()

    def __init__(self, data_file):
        self.data_file = data_file
        self.history_file = os.path.join(
            os.path.dirname(data_file), 'history.json'
        )
        self._ensure_data_file()
        self._ensure_history_file()

    def _ensure_history_file(self):
        """Create history file if it doesn't exist."""
        if not os.path.exists(self.history_file):
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump({"history": []}, f, indent=2)

    def _load_history(self):
        """Load history from JSON file."""
        with open(self.history_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_history(self, data):
        """Save history to JSON file."""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ------------------------------------------------------------------
    # HISTORY / AUDIT LOG operations
    # ------------------------------------------------------------------

    def log_action(self, action, item_name, cupboard_name, nt_id):
        """Record a borrow/return action in the history log."""
        with self._lock:
            data = self._load_history()
            entry = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'action': action,
                'item_name': item_name,
                'cupboard_name': cupboard_name,
                'nt_id': nt_id,
            }
            data.setdefault('history', []).insert(0, entry)  # newest first
            self._save_history(data)

    def get_history(self, nt_id_filter=None, action_filter=None, limit=200):
        """
        Get audit history with optional filters.
        Returns newest entries first.
        """
        with self._lock:
            data = self._load_history()
            records = data.get('history', [])

            if nt_id_filter:
                records = [
                    r for r in records
                    if r.get('nt_id', '').upper() == nt_id_filter.upper()
                ]
            if action_filter:
                records = [
                    r for r in records
                    if r.get('action') == action_filter
                ]

            return records[:limit]

    def _ensure_data_file(self):
        """Create data file with default sample data if it doesn't exist."""
        if not os.path.exists(self.data_file):
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            self._save_data(self._get_default_data())

    def _load_data(self):
        """Load data from JSON file."""
        with open(self.data_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_data(self, data):
        """Save data to JSON file."""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ------------------------------------------------------------------
    # READ operations
    # ------------------------------------------------------------------

    def get_all_cupboards(self):
        """Get all cupboards with their items."""
        with self._lock:
            data = self._load_data()
            return data.get('cupboards', [])

    # ------------------------------------------------------------------
    # LOCK / UNLOCK operations
    # ------------------------------------------------------------------

    def toggle_lock(self, cupboard_id, item_id, nt_id, is_admin=False):
        """
        Toggle the lock status of an item.
        Returns: (action, item_name, cupboard_name) or None if not found,
                 or ('not_authorized', item_name, cupboard_name) if user
                 tries to return an item they didn't borrow.
        """
        with self._lock:
            data = self._load_data()
            for cupboard in data.get('cupboards', []):
                if cupboard['id'] == cupboard_id:
                    for item in cupboard.get('items', []):
                        if item['id'] == item_id:
                            if item['is_locked']:
                                # UNLOCK (borrow) the item
                                item['is_locked'] = False
                                item['borrowed_by'] = nt_id
                                item['borrowed_at'] = datetime.now().strftime(
                                    '%Y-%m-%d %H:%M:%S'
                                )
                                action = 'unlocked'
                            else:
                                # Only the borrower or admin can return
                                if item['borrowed_by'] != nt_id and not is_admin:
                                    return (
                                        'not_authorized',
                                        item['name'],
                                        cupboard['name'],
                                    )
                                # LOCK (return) the item
                                item['is_locked'] = True
                                item['borrowed_by'] = None
                                item['borrowed_at'] = None
                                action = 'locked'
                            self._save_data(data)
                            return action, item['name'], cupboard['name']
            return None

    # ------------------------------------------------------------------
    # ADMIN - Item operations
    # ------------------------------------------------------------------

    def add_item(self, cupboard_id, item_name):
        """Add a new item to a cupboard."""
        with self._lock:
            data = self._load_data()
            for cupboard in data.get('cupboards', []):
                if cupboard['id'] == cupboard_id:
                    existing_ids = [i['id'] for i in cupboard.get('items', [])]
                    new_num = 1
                    while f"C{cupboard_id}_{new_num:03d}" in existing_ids:
                        new_num += 1
                    new_item = {
                        'id': f"C{cupboard_id}_{new_num:03d}",
                        'name': item_name,
                        'is_locked': True,
                        'borrowed_by': None,
                        'borrowed_at': None,
                    }
                    cupboard.setdefault('items', []).append(new_item)
                    self._save_data(data)
                    return True
            return False

    def remove_item(self, cupboard_id, item_id):
        """Remove an item from a cupboard."""
        with self._lock:
            data = self._load_data()
            for cupboard in data.get('cupboards', []):
                if cupboard['id'] == cupboard_id:
                    cupboard['items'] = [
                        i for i in cupboard.get('items', []) if i['id'] != item_id
                    ]
                    self._save_data(data)
                    return True
            return False

    # ------------------------------------------------------------------
    # ADMIN - Cupboard operations
    # ------------------------------------------------------------------

    def add_cupboard(self, cupboard_name):
        """Add a new cupboard."""
        with self._lock:
            data = self._load_data()
            cupboards = data.get('cupboards', [])
            new_id = max([c['id'] for c in cupboards], default=0) + 1
            cupboards.append({
                'id': new_id,
                'name': cupboard_name,
                'items': [],
            })
            data['cupboards'] = cupboards
            self._save_data(data)
            return True

    def remove_cupboard(self, cupboard_id):
        """Remove a cupboard and all its items."""
        with self._lock:
            data = self._load_data()
            data['cupboards'] = [
                c for c in data.get('cupboards', []) if c['id'] != cupboard_id
            ]
            self._save_data(data)
            return True

    # ------------------------------------------------------------------
    # Default sample data
    # ------------------------------------------------------------------

    @staticmethod
    def _get_default_data():
        """Return default inventory data with 9 cupboards."""
        return {
            "cupboards": [
                {
                    "id": 1,
                    "name": "Cupboard 1 - Measurement Equipment",
                    "items": [
                        {"id": "C1_001", "name": "Digital Oscilloscope 100MHz",
                         "is_locked": True, "borrowed_by": None, "borrowed_at": None},
                        {"id": "C1_002", "name": "Digital Multimeter",
                         "is_locked": True, "borrowed_by": None, "borrowed_at": None},
                        {"id": "C1_003", "name": "Function Generator",
                         "is_locked": True, "borrowed_by": None, "borrowed_at": None},
                        {"id": "C1_004", "name": "Logic Analyzer",
                         "is_locked": True, "borrowed_by": None, "borrowed_at": None},
                    ],
                },
                {
                    "id": 2,
                    "name": "Cupboard 2 - Power Supplies",
                    "items": [
                        {"id": "C2_001", "name": "DC Power Supply 30V/5A",
                         "is_locked": True, "borrowed_by": None, "borrowed_at": None},
                        {"id": "C2_002", "name": "Variable Power Supply",
                         "is_locked": True, "borrowed_by": None, "borrowed_at": None},
                        {"id": "C2_003", "name": "Battery Charger",
                         "is_locked": True, "borrowed_by": None, "borrowed_at": None},
                    ],
                },
                {
                    "id": 3,
                    "name": "Cupboard 3 - Development Boards",
                    "items": [
                        {"id": "C3_001", "name": "Arduino Mega",
                         "is_locked": True, "borrowed_by": None, "borrowed_at": None},
                        {"id": "C3_002", "name": "Raspberry Pi 4",
                         "is_locked": True, "borrowed_by": None, "borrowed_at": None},
                        {"id": "C3_003", "name": "STM32 Nucleo Board",
                         "is_locked": True, "borrowed_by": None, "borrowed_at": None},
                        {"id": "C3_004", "name": "ESP32 Dev Kit",
                         "is_locked": True, "borrowed_by": None, "borrowed_at": None},
                    ],
                },
                {
                    "id": 4,
                    "name": "Cupboard 4 - Networking Equipment",
                    "items": [
                        {"id": "C4_001", "name": "Ethernet Switch 8-Port",
                         "is_locked": True, "borrowed_by": None, "borrowed_at": None},
                        {"id": "C4_002", "name": "Wi-Fi Router",
                         "is_locked": True, "borrowed_by": None, "borrowed_at": None},
                        {"id": "C4_003", "name": "Network Cable Tester",
                         "is_locked": True, "borrowed_by": None, "borrowed_at": None},
                    ],
                },
                {
                    "id": 5,
                    "name": "Cupboard 5 - Testing Tools",
                    "items": [
                        {"id": "C5_001", "name": "JTAG Debugger",
                         "is_locked": True, "borrowed_by": None, "borrowed_at": None},
                        {"id": "C5_002", "name": "USB Protocol Analyzer",
                         "is_locked": True, "borrowed_by": None, "borrowed_at": None},
                        {"id": "C5_003", "name": "CAN Bus Analyzer",
                         "is_locked": True, "borrowed_by": None, "borrowed_at": None},
                        {"id": "C5_004", "name": "Spectrum Analyzer",
                         "is_locked": True, "borrowed_by": None, "borrowed_at": None},
                    ],
                },
                {
                    "id": 6,
                    "name": "Cupboard 6 - Cables & Connectors",
                    "items": [
                        {"id": "C6_001", "name": "USB-A to USB-B Cable Set",
                         "is_locked": True, "borrowed_by": None, "borrowed_at": None},
                        {"id": "C6_002", "name": "HDMI Cable Set",
                         "is_locked": True, "borrowed_by": None, "borrowed_at": None},
                        {"id": "C6_003", "name": "Jumper Wire Kit",
                         "is_locked": True, "borrowed_by": None, "borrowed_at": None},
                        {"id": "C6_004", "name": "BNC Cable Set",
                         "is_locked": True, "borrowed_by": None, "borrowed_at": None},
                    ],
                },
                {
                    "id": 7,
                    "name": "Cupboard 7 - Safety Equipment",
                    "items": [
                        {"id": "C7_001", "name": "ESD Wrist Strap",
                         "is_locked": True, "borrowed_by": None, "borrowed_at": None},
                        {"id": "C7_002", "name": "Safety Goggles",
                         "is_locked": True, "borrowed_by": None, "borrowed_at": None},
                        {"id": "C7_003", "name": "Anti-Static Mat",
                         "is_locked": True, "borrowed_by": None, "borrowed_at": None},
                    ],
                },
                {
                    "id": 8,
                    "name": "Cupboard 8 - Hand Tools",
                    "items": [
                        {"id": "C8_001", "name": "Soldering Station",
                         "is_locked": True, "borrowed_by": None, "borrowed_at": None},
                        {"id": "C8_002", "name": "Precision Screwdriver Set",
                         "is_locked": True, "borrowed_by": None, "borrowed_at": None},
                        {"id": "C8_003", "name": "Wire Stripper",
                         "is_locked": True, "borrowed_by": None, "borrowed_at": None},
                        {"id": "C8_004", "name": "Heat Gun",
                         "is_locked": True, "borrowed_by": None, "borrowed_at": None},
                    ],
                },
                {
                    "id": 9,
                    "name": "Cupboard 9 - Miscellaneous",
                    "items": [
                        {"id": "C9_001", "name": "Label Printer",
                         "is_locked": True, "borrowed_by": None, "borrowed_at": None},
                        {"id": "C9_002", "name": "USB Hub 7-Port",
                         "is_locked": True, "borrowed_by": None, "borrowed_at": None},
                        {"id": "C9_003", "name": "SD Card Reader",
                         "is_locked": True, "borrowed_by": None, "borrowed_at": None},
                    ],
                },
            ]
        }
