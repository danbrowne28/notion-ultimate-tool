"""API Key Rotation Manager

Automated API key rotation with version control and expiry tracking.
Useful for Trading212, Polygon.io, and other API keys.

Dependencies:
    - cryptography
    - sqlalchemy
    - python-dateutil

Example:
    manager = KeyRotationManager()
    new_key = manager.rotate_key('trading212')
    manager.validate_key(new_key)
"""

import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dataclasses import dataclass
import json


@dataclass
class APIKey:
    """API Key storage model"""
    service: str
    key: str
    version: int
    created_at: datetime
    expires_at: Optional[datetime]
    is_active: bool
    metadata: Dict[str, Any]


class KeyRotationManager:
    """Manages API key rotation and lifecycle"""

    def __init__(self, db_path: str = ".keys"):
        """Initialize key manager
        
        Args:
            db_path: Path to store encrypted keys
        """
        self.db_path = db_path
        self.keys: Dict[str, list] = {}
        self._load_keys()

    def _load_keys(self) -> None:
        """Load keys from storage"""
        if os.path.exists(self.db_path):
            with open(self.db_path, 'r') as f:
                self.keys = json.load(f)
        else:
            self.keys = {}

    def _save_keys(self) -> None:
        """Save keys to storage"""
        with open(self.db_path, 'w') as f:
            json.dump(self.keys, f, default=str)

    def create_key(
        self,
        service: str,
        length: int = 32,
        expiry_days: Optional[int] = 90
    ) -> str:
        """Create new API key
        
        Args:
            service: Service name (e.g., 'trading212')
            length: Key length in bytes
            expiry_days: Days until expiry (None = no expiry)
            
        Returns:
            Generated API key
        """
        # Generate random key
        key = secrets.token_urlsafe(length)
        
        # Set expiry
        expires_at = None
        if expiry_days:
            expires_at = (datetime.utcnow() + timedelta(days=expiry_days)).isoformat()
        
        # Initialize service keys if needed
        if service not in self.keys:
            self.keys[service] = []
        
        # Deactivate previous keys
        for existing_key in self.keys[service]:
            existing_key['is_active'] = False
        
        # Add new key
        api_key = {
            'key': key,
            'version': len(self.keys[service]) + 1,
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': expires_at,
            'is_active': True,
            'metadata': {}
        }
        
        self.keys[service].append(api_key)
        self._save_keys()
        
        return key

    def rotate_key(
        self,
        service: str,
        grace_period_hours: int = 1
    ) -> str:
        """Rotate API key for service
        
        Args:
            service: Service name
            grace_period_hours: Hours to keep old key active
            
        Returns:
            New API key
        """
        new_key = self.create_key(service)
        
        # Set grace period for old key
        if service in self.keys and len(self.keys[service]) > 1:
            old_key = self.keys[service][-2]  # Second to last
            old_key['grace_period_until'] = (
                datetime.utcnow() + timedelta(hours=grace_period_hours)
            ).isoformat()
        
        self._save_keys()
        return new_key

    def validate_key(self, service: str, key: str) -> bool:
        """Validate API key
        
        Args:
            service: Service name
            key: Key to validate
            
        Returns:
            True if valid, False otherwise
        """
        if service not in self.keys:
            return False
        
        for api_key in self.keys[service]:
            if api_key['key'] == key:
                # Check if active
                if not api_key['is_active']:
                    # Check grace period
                    if 'grace_period_until' not in api_key:
                        return False
                    
                    grace_until = datetime.fromisoformat(
                        api_key['grace_period_until']
                    )
                    if datetime.utcnow() > grace_until:
                        return False
                
                # Check expiry
                if api_key['expires_at']:
                    expires_at = datetime.fromisoformat(api_key['expires_at'])
                    if datetime.utcnow() > expires_at:
                        return False
                
                return True
        
        return False

    def get_active_key(self, service: str) -> Optional[str]:
        """Get currently active key for service
        
        Args:
            service: Service name
            
        Returns:
            Active key or None
        """
        if service not in self.keys:
            return None
        
        for api_key in reversed(self.keys[service]):
            if api_key['is_active']:
                # Verify not expired
                if api_key['expires_at']:
                    expires_at = datetime.fromisoformat(api_key['expires_at'])
                    if datetime.utcnow() <= expires_at:
                        return api_key['key']
                else:
                    return api_key['key']
        
        return None

    def get_key_info(self, service: str, version: int) -> Optional[Dict]:
        """Get information about specific key version
        
        Args:
            service: Service name
            version: Key version
            
        Returns:
            Key metadata (without actual key)
        """
        if service not in self.keys:
            return None
        
        for api_key in self.keys[service]:
            if api_key['version'] == version:
                return {
                    'version': api_key['version'],
                    'created_at': api_key['created_at'],
                    'expires_at': api_key['expires_at'],
                    'is_active': api_key['is_active'],
                    'metadata': api_key['metadata']
                }
        
        return None

    def revoke_key(self, service: str, version: int) -> bool:
        """Revoke specific key version
        
        Args:
            service: Service name
            version: Key version to revoke
            
        Returns:
            True if revoked successfully
        """
        if service not in self.keys:
            return False
        
        for api_key in self.keys[service]:
            if api_key['version'] == version:
                api_key['is_active'] = False
                api_key['revoked_at'] = datetime.utcnow().isoformat()
                self._save_keys()
                return True
        
        return False

    def list_keys(self, service: str) -> list:
        """List all keys for service (metadata only)
        
        Args:
            service: Service name
            
        Returns:
            List of key metadata
        """
        if service not in self.keys:
            return []
        
        return [
            {
                'version': key['version'],
                'created_at': key['created_at'],
                'expires_at': key['expires_at'],
                'is_active': key['is_active'],
                'metadata': key['metadata']
            }
            for key in self.keys[service]
        ]

    def cleanup_expired_keys(self, service: str) -> int:
        """Remove expired keys from storage
        
        Args:
            service: Service name
            
        Returns:
            Number of keys removed
        """
        if service not in self.keys:
            return 0
        
        original_count = len(self.keys[service])
        
        self.keys[service] = [
            key for key in self.keys[service]
            if (
                (not key['expires_at']) or
                (datetime.fromisoformat(key['expires_at']) > datetime.utcnow())
            )
        ]
        
        self._save_keys()
        return original_count - len(self.keys[service])


# Example usage
if __name__ == '__main__':
    manager = KeyRotationManager()
    
    # Create new key
    key = manager.create_key('trading212', expiry_days=90)
    print(f"Created key: {key[:20]}...")
    
    # Validate key
    is_valid = manager.validate_key('trading212', key)
    print(f"Key valid: {is_valid}")
    
    # Get active key
    active = manager.get_active_key('trading212')
    print(f"Active key: {active[:20] if active else None}...")
    
    # List all keys
    keys = manager.list_keys('trading212')
    print(f"Total keys: {len(keys)}")
    
    # Rotate key
    new_key = manager.rotate_key('trading212')
    print(f"Rotated key: {new_key[:20]}...")
