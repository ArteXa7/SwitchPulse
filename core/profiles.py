import json
from pathlib import Path
from typing import List, Optional
import keyring
from cryptography.fernet import Fernet
from pydantic import BaseModel, Field

class DeviceProfile(BaseModel):
    name: str
    host: str
    username: str
    password: str
    protocol: str = Field(default="ssh", pattern="^(ssh|telnet)$")
    port: int = 22
    vendor_template: str = "cisco_ios.yaml"
    description: Optional[str] = None

class AppSettings(BaseModel):
    theme: str = "Dark"
    mock_mode: bool = False
    timeout: int = 10
    backup_dir: str = "./backups"

class ProfileManager:
    """Manages secure device profiles and global application settings."""
    
    SERVICE_NAME = "SwitchPulse"
    KEY_NAME = "MasterKey"
    BASE_DIR = Path.home() / ".switchpulse"
    PROFILES_PATH = BASE_DIR / "profiles.json"
    SETTINGS_PATH = BASE_DIR / "settings.json"

    def __init__(self):
        self.BASE_DIR.mkdir(parents=True, exist_ok=True)
        self._key = self._get_or_init_key()
        self._fernet = Fernet(self._key)

    def _get_or_init_key(self) -> bytes:
        key = keyring.get_password(self.SERVICE_NAME, self.KEY_NAME)
        if not key:
            key = Fernet.generate_key().decode()
            keyring.set_password(self.SERVICE_NAME, self.KEY_NAME, key)
        return key.encode()

    def _encrypt(self, text: str) -> str:
        return self._fernet.encrypt(text.encode()).decode()

    def _decrypt(self, token: str) -> str:
        return self._fernet.decrypt(token.encode()).decode()

    # Settings Management
    def load_settings(self) -> AppSettings:
        if not self.SETTINGS_PATH.exists():
            return AppSettings()
        try:
            with open(self.SETTINGS_PATH, "r") as f:
                return AppSettings(**json.load(f))
        except Exception:
            return AppSettings()

    def save_settings(self, settings: AppSettings) -> None:
        with open(self.SETTINGS_PATH, "w") as f:
            json.dump(settings.model_dump(), f, indent=4)

    # Profile Management
    def save_profile(self, profile: DeviceProfile) -> None:
        profiles = self.list_profiles(decrypt=False)
        # Encrypt password before disk write
        profile.password = self._encrypt(profile.password)
        
        # Update or append
        existing_idx = next((i for i, p in enumerate(profiles) if p.name == profile.name), -1)
        if existing_idx >= 0:
            profiles[existing_idx] = profile
        else:
            profiles.append(profile)
        
        self._write_profiles(profiles)

    def list_profiles(self, decrypt: bool = True) -> List[DeviceProfile]:
        if not self.PROFILES_PATH.exists():
            return []
        try:
            with open(self.PROFILES_PATH, "r") as f:
                data = json.load(f)
                profiles = [DeviceProfile(**item) for item in data]
                if decrypt:
                    for p in profiles:
                        p.password = self._decrypt(p.password)
                return profiles
        except Exception:
            return []

    def _write_profiles(self, profiles: List[DeviceProfile]) -> None:
        with open(self.PROFILES_PATH, "w") as f:
            json.dump([p.model_dump() for p in profiles], f, indent=4)
            
    def delete_profile(self, name: str) -> bool:
        profiles = self.list_profiles(decrypt=False)
        filtered = [p for p in profiles if p.name != name]
        if len(filtered) < len(profiles):
            self._write_profiles(filtered)
            return True
        return False
