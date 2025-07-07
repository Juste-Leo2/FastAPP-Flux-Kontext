# src/utils/settings.py
import json
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SETTINGS_FILE = os.path.join(PROJECT_ROOT, 'settings.json')

class SettingsManager:
    """Gère le chargement et la sauvegarde des paramètres de l'application."""
    def __init__(self):
        self._defaults = self._get_defaults()
        self.settings = self._load_settings()

    def _get_defaults(self):
        """Retourne un dictionnaire des paramètres par défaut."""
        return {
            "accessibility": {
                "language": "en",
                "theme": "dark", # dark, light
                "color": "blue"  # blue, green, dark-blue
            },
            "generation": {
                "steps": 10,
                "cfg": 1.0,
                "size": "1024x1024"
            },
            "edition": {
                "steps": 10,
                "cfg": 1.0,
                "denoise": 1.0,
                "guidance": 2.5
            },
            "correction": {
                "steps": 3,
                "cfg": 1.0,
                "denoise": 0.2
            }
        }

    def _load_settings(self):
        """Charge les paramètres. Retourne des valeurs par défaut si le fichier est absent ou corrompu."""
        defaults = self._get_defaults()
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # Fusionne récursivement les paramètres chargés avec les défauts pour garantir que toutes les clés existent
                    return self._update_dict(defaults, loaded_settings)
            return defaults
        except (FileNotFoundError, json.JSONDecodeError):
            return defaults

    def _update_dict(self, d, u):
        """Met à jour récursivement un dictionnaire."""
        for k, v in u.items():
            if isinstance(v, dict):
                d[k] = self._update_dict(d.get(k, {}), v)
            else:
                d[k] = v
        return d

    def _save_settings(self):
        """Sauvegarde les paramètres actuels dans le fichier JSON."""
        try:
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des paramètres : {e}")

    def get(self, key, default=None):
        """Récupère une valeur de paramètre. Utilise des points pour la notation. Ex: 'generation.steps'"""
        keys = key.split('.')
        val = self.settings
        try:
            for k in keys:
                val = val[k]
            return val
        except KeyError:
            return default

    def set(self, key, value):
        """Définit une valeur de paramètre et la sauvegarde. Utilise des points pour la notation."""
        keys = key.split('.')
        d = self.settings
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        d[keys[-1]] = value
        self._save_settings()