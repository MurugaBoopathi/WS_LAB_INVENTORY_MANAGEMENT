import copy
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
    SCHEMA_VERSION = 2
    DEFAULT_DE_SCOPE_VALUE = '__NONE__'

    def __init__(self, data_file):
        self.data_file = data_file
        self.history_file = os.path.join(
            os.path.dirname(data_file), 'history.json'
        )
        self._ensure_data_file()
        self._ensure_history_file()
        self._migrate_data_file()

    def _ensure_history_file(self):
        """Create history file if it doesn't exist."""
        if not os.path.exists(self.history_file):
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            with open(self.history_file, 'w', encoding='utf-8') as file_handle:
                json.dump({'history': []}, file_handle, indent=2)

    def _load_history(self):
        """Load history from JSON file."""
        with open(self.history_file, 'r', encoding='utf-8') as file_handle:
            return json.load(file_handle)

    def _save_history(self, data):
        """Save history to JSON file."""
        with open(self.history_file, 'w', encoding='utf-8') as file_handle:
            json.dump(data, file_handle, indent=2, ensure_ascii=False)

    def _ensure_data_file(self):
        """Create the scoped data file if it doesn't exist."""
        if not os.path.exists(self.data_file):
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            self._save_data(self._get_default_data())

    def _load_data(self):
        """Load data from JSON file."""
        with open(self.data_file, 'r', encoding='utf-8') as file_handle:
            return json.load(file_handle)

    def _save_data(self, data):
        """Save data to JSON file."""
        with open(self.data_file, 'w', encoding='utf-8') as file_handle:
            json.dump(data, file_handle, indent=2, ensure_ascii=False)

    @staticmethod
    def _normalize_scope(scope):
        """Normalize a Country / Department / Group scope."""
        scope = scope or {}
        normalized_scope = {
            'country': (scope.get('country') or '').strip().upper(),
            'department': (scope.get('department') or '').strip().upper(),
            'group': (scope.get('group') or '').strip().upper(),
        }
        if normalized_scope['country'] == 'DE':
            normalized_scope['department'] = DataManager.DEFAULT_DE_SCOPE_VALUE
            normalized_scope['group'] = DataManager.DEFAULT_DE_SCOPE_VALUE
        return normalized_scope

    @classmethod
    def _validate_scope(cls, scope):
        """Ensure a scope includes country, department, and group."""
        normalized_scope = cls._normalize_scope(scope)
        if normalized_scope['country'] == 'DE':
            return True
        return all(normalized_scope.values())

    @classmethod
    def _scope_key(cls, scope):
        """Build a stable dictionary key for a scoped inventory."""
        normalized_scope = cls._normalize_scope(scope)
        return (
            f"{normalized_scope['country']}::"
            f"{normalized_scope['department']}::"
            f"{normalized_scope['group']}"
        )

    @classmethod
    def scope_label(cls, scope):
        """Render a human-readable scope label."""
        normalized_scope = cls._normalize_scope(scope)
        if normalized_scope['country'] == 'DE':
            return normalized_scope['country']
        return (
            f"{normalized_scope['country']} / "
            f"{normalized_scope['department']} / "
            f"{normalized_scope['group']}"
        )

    @classmethod
    def _normalize_data_structure(cls, data):
        """Normalize persisted data to the scope-aware schema."""
        if 'scoped_inventories' not in data:
            return {
                'schema_version': cls.SCHEMA_VERSION,
                'legacy_cupboards': copy.deepcopy(data.get('cupboards', [])),
                'scoped_inventories': {},
            }

        normalized = {
            'schema_version': cls.SCHEMA_VERSION,
            'legacy_cupboards': copy.deepcopy(data.get('legacy_cupboards', [])),
            'scoped_inventories': {},
        }

        for key, inventory in data.get('scoped_inventories', {}).items():
            scope = cls._normalize_scope(inventory.get('scope', {}))
            normalized['scoped_inventories'][key] = {
                'scope': scope,
                'cupboards': copy.deepcopy(inventory.get('cupboards', [])),
            }

            for cupboard in normalized['scoped_inventories'][key]['cupboards']:
                cupboard.setdefault('items', [])

        return normalized

    def _migrate_data_file(self):
        """Upgrade legacy flat inventory data to the scoped schema."""
        with self._lock:
            data = self._load_data()
            normalized = self._normalize_data_structure(data)
            if normalized != data:
                self._save_data(normalized)

    def _get_scope_inventory(self, data, scope, create=False):
        """Get or create the scoped inventory bucket for a selection."""
        if not self._validate_scope(scope):
            return None

        scope_key = self._scope_key(scope)
        scoped_inventories = data.setdefault('scoped_inventories', {})
        inventory = scoped_inventories.get(scope_key)

        if inventory is None and create:
            inventory = {
                'scope': self._normalize_scope(scope),
                'cupboards': [],
            }
            scoped_inventories[scope_key] = inventory

        return inventory

    # ------------------------------------------------------------------
    # HISTORY / AUDIT LOG operations
    # ------------------------------------------------------------------

    def log_action(self, action, item_name, cupboard_name, nt_id, scope=None):
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
            if self._validate_scope(scope):
                normalized_scope = self._normalize_scope(scope)
                entry['country'] = normalized_scope['country']
                entry['department'] = normalized_scope['department']
                entry['group'] = normalized_scope['group']
                entry['scope_label'] = self.scope_label(normalized_scope)
            data.setdefault('history', []).insert(0, entry)
            self._save_history(data)

    def get_history(self, nt_id_filter=None, action_filter=None, limit=200):
        """Get audit history with optional filters, newest first."""
        with self._lock:
            data = self._load_history()
            records = data.get('history', [])

            if nt_id_filter:
                records = [
                    record for record in records
                    if record.get('nt_id', '').upper() == nt_id_filter.upper()
                ]
            if action_filter:
                records = [
                    record for record in records
                    if record.get('action') == action_filter
                ]

            return records[:limit]

    # ------------------------------------------------------------------
    # READ operations
    # ------------------------------------------------------------------

    def get_all_cupboards(self, scope):
        """Get all cupboards for a specific Country/Department/Group."""
        with self._lock:
            data = self._load_data()
            inventory = self._get_scope_inventory(data, scope)
            if not inventory:
                return []
            return copy.deepcopy(inventory.get('cupboards', []))

    # ------------------------------------------------------------------
    # LOCK / UNLOCK operations
    # ------------------------------------------------------------------

    def toggle_lock(self, scope, cupboard_id, item_id, nt_id, is_admin=False):
        """
        Toggle the lock status of an item within a selected scope.
        Returns: (action, item_name, cupboard_name) or None if not found,
                 or ('admin_only_lock', item_name, cupboard_name) if a
                 non-admin user tries to return an item.
        """
        with self._lock:
            data = self._load_data()
            inventory = self._get_scope_inventory(data, scope)
            if not inventory:
                return None

            for cupboard in inventory.get('cupboards', []):
                if cupboard['id'] != cupboard_id:
                    continue

                for item in cupboard.get('items', []):
                    if item['id'] != item_id:
                        continue

                    if item['is_locked']:
                        item['is_locked'] = False
                        item['borrowed_by'] = nt_id
                        item['borrowed_at'] = datetime.now().strftime(
                            '%Y-%m-%d %H:%M:%S'
                        )
                        action = 'unlocked'
                    else:
                        if not is_admin:
                            return (
                                'admin_only_lock',
                                item['name'],
                                cupboard['name'],
                            )
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

    def add_item(self, scope, cupboard_id, item_name):
        """Add a new item to a cupboard inside a selected scope."""
        with self._lock:
            data = self._load_data()
            inventory = self._get_scope_inventory(data, scope)
            if not inventory:
                return False

            for cupboard in inventory.get('cupboards', []):
                if cupboard['id'] != cupboard_id:
                    continue

                existing_ids = [item['id'] for item in cupboard.get('items', [])]
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

    def remove_item(self, scope, cupboard_id, item_id):
        """Remove an item from a cupboard inside a selected scope."""
        with self._lock:
            data = self._load_data()
            inventory = self._get_scope_inventory(data, scope)
            if not inventory:
                return False

            for cupboard in inventory.get('cupboards', []):
                if cupboard['id'] != cupboard_id:
                    continue

                original_count = len(cupboard.get('items', []))
                cupboard['items'] = [
                    item for item in cupboard.get('items', [])
                    if item['id'] != item_id
                ]
                if len(cupboard['items']) == original_count:
                    return False

                self._save_data(data)
                return True

            return False

    # ------------------------------------------------------------------
    # ADMIN - Cupboard operations
    # ------------------------------------------------------------------

    def add_cupboard(self, scope, cupboard_name):
        """Add a new cupboard inside a selected scope."""
        with self._lock:
            data = self._load_data()
            inventory = self._get_scope_inventory(data, scope, create=True)
            cupboards = inventory.setdefault('cupboards', [])
            new_id = max([cupboard['id'] for cupboard in cupboards], default=0) + 1
            cupboards.append({
                'id': new_id,
                'name': cupboard_name,
                'items': [],
            })
            self._save_data(data)
            return True

    def remove_cupboard(self, scope, cupboard_id):
        """Remove a cupboard and its items from a selected scope."""
        with self._lock:
            data = self._load_data()
            inventory = self._get_scope_inventory(data, scope)
            if not inventory:
                return False

            original_count = len(inventory.get('cupboards', []))
            inventory['cupboards'] = [
                cupboard for cupboard in inventory.get('cupboards', [])
                if cupboard['id'] != cupboard_id
            ]
            if len(inventory['cupboards']) == original_count:
                return False

            self._save_data(data)
            return True

    # ------------------------------------------------------------------
    # Default scoped data
    # ------------------------------------------------------------------

    @classmethod
    def _get_default_data(cls):
        """Return the scope-aware inventory schema without seeded cupboards."""
        return {
            'schema_version': cls.SCHEMA_VERSION,
            'legacy_cupboards': [],
            'scoped_inventories': {},
        }