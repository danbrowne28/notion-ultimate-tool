"""Password Hashing with Bcrypt

Secure password hashing, verification, and strength checking.
Best practice for user authentication.

Dependencies:
    - bcrypt
    - passlib

Example:
    hasher = PasswordHasher()
    hashed = hasher.hash_password('password123')
    is_valid = hasher.verify_password('password123', hashed)
"""

import os
import re
from typing import Optional

try:
    from passlib.context import CryptContext
    from passlib.exc import InvalidToken
except ImportError:
    raise ImportError("Install passlib: pip install passlib bcrypt")


class PasswordHasher:
    """Password hashing and verification"""

    def __init__(self, rounds: int = 12):
        """Initialize password hasher
        
        Args:
            rounds: Bcrypt rounds (higher = slower = more secure)
        """
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
            bcrypt__rounds=rounds
        )

    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters")
        
        return self.pwd_context.hash(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash
        
        Args:
            password: Plain text password
            hashed_password: Hashed password
            
        Returns:
            True if password matches
        """
        try:
            return self.pwd_context.verify(password, hashed_password)
        except (InvalidToken, ValueError):
            return False

    def needs_rehashing(self, hashed_password: str) -> bool:
        """Check if password hash needs updating
        
        Args:
            hashed_password: Hashed password
            
        Returns:
            True if should be rehashed
        """
        return self.pwd_context.needs_update(hashed_password)


class PasswordValidator:
    """Password strength validation"""

    def __init__(
        self,
        min_length: int = 8,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_digits: bool = True,
        require_special: bool = True
    ):
        """Initialize validator
        
        Args:
            min_length: Minimum password length
            require_uppercase: Must contain uppercase
            require_lowercase: Must contain lowercase
            require_digits: Must contain digits
            require_special: Must contain special characters
        """
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digits = require_digits
        self.require_special = require_special

    def validate(self, password: str) -> tuple[bool, str]:
        """Validate password strength
        
        Args:
            password: Password to validate
            
        Returns:
            (is_valid, error_message)
        """
        if not password:
            return False, "Password cannot be empty"
        
        if len(password) < self.min_length:
            return False, f"Password must be at least {self.min_length} characters"
        
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            return False, "Password must contain uppercase letters"
        
        if self.require_lowercase and not re.search(r'[a-z]', password):
            return False, "Password must contain lowercase letters"
        
        if self.require_digits and not re.search(r'\d', password):
            return False, "Password must contain digits"
        
        if self.require_special:
            if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'"<>,.?/]', password):
                return False, "Password must contain special characters"
        
        return True, "Password is valid"

    def get_strength(self, password: str) -> str:
        """Get password strength rating
        
        Args:
            password: Password to rate
            
        Returns:
            'weak', 'fair', 'good', or 'strong'
        """
        score = 0
        
        # Length
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if len(password) >= 16:
            score += 1
        
        # Character variety
        if re.search(r'[a-z]', password):
            score += 1
        if re.search(r'[A-Z]', password):
            score += 1
        if re.search(r'\d', password):
            score += 1
        if re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'"<>,.?/]', password):
            score += 1
        
        if score <= 2:
            return 'weak'
        elif score <= 4:
            return 'fair'
        elif score <= 6:
            return 'good'
        else:
            return 'strong'


class PasswordManager:
    """Complete password management system"""

    def __init__(self, rounds: int = 12):
        """Initialize password manager
        
        Args:
            rounds: Bcrypt rounds
        """
        self.hasher = PasswordHasher(rounds=rounds)
        self.validator = PasswordValidator()
        self.password_history = {}  # user_id -> [old_hashes]

    def register_user(self, user_id: str, password: str) -> dict:
        """Register new user with password
        
        Args:
            user_id: User identifier
            password: Password
            
        Returns:
            {success: bool, hash: str, error: str}
        """
        # Validate
        is_valid, msg = self.validator.validate(password)
        if not is_valid:
            return {'success': False, 'error': msg}
        
        # Check strength
        strength = self.validator.get_strength(password)
        if strength not in ['good', 'strong']:
            return {
                'success': False,
                'error': f'Password strength is {strength}, must be good or strong'
            }
        
        # Hash
        hashed = self.hasher.hash_password(password)
        self.password_history[user_id] = [hashed]
        
        return {'success': True, 'hash': hashed}

    def change_password(
        self,
        user_id: str,
        old_password: str,
        new_password: str,
        current_hash: str
    ) -> dict:
        """Change user password
        
        Args:
            user_id: User identifier
            old_password: Current password
            new_password: New password
            current_hash: Current password hash
            
        Returns:
            {success: bool, hash: str, error: str}
        """
        # Verify old password
        if not self.hasher.verify_password(old_password, current_hash):
            return {'success': False, 'error': 'Current password is incorrect'}
        
        # Validate new password
        is_valid, msg = self.validator.validate(new_password)
        if not is_valid:
            return {'success': False, 'error': msg}
        
        # Check not used before (last 3 passwords)
        if user_id in self.password_history:
            old_hashes = self.password_history[user_id][-3:]
            for old_hash in old_hashes:
                if self.hasher.verify_password(new_password, old_hash):
                    return {
                        'success': False,
                        'error': 'Cannot reuse recent passwords'
                    }
        
        # Hash new password
        new_hash = self.hasher.hash_password(new_password)
        
        # Update history
        if user_id not in self.password_history:
            self.password_history[user_id] = []
        self.password_history[user_id].append(new_hash)
        
        return {'success': True, 'hash': new_hash}

    def verify_login(self, user_id: str, password: str, stored_hash: str) -> dict:
        """Verify login attempt
        
        Args:
            user_id: User identifier
            password: Provided password
            stored_hash: Stored password hash
            
        Returns:
            {success: bool, needs_rehash: bool, error: str}
        """
        # Verify password
        if not self.hasher.verify_password(password, stored_hash):
            return {'success': False, 'error': 'Invalid password'}
        
        # Check if hash needs updating
        needs_rehash = self.hasher.needs_rehashing(stored_hash)
        
        return {'success': True, 'needs_rehash': needs_rehash}


# FastAPI integration example
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
password_manager = PasswordManager()

class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post('/register')
async def register(req: RegisterRequest):
    result = password_manager.register_user(req.username, req.password)
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    return {'message': 'User registered successfully'}

@app.post('/login')
async def login(req: LoginRequest):
    # Get stored hash from database
    # stored_hash = database.get_password_hash(req.username)
    result = password_manager.verify_login(req.username, req.password, stored_hash)
    if not result['success']:
        raise HTTPException(status_code=401, detail=result['error'])
    return {'message': 'Login successful'}
"""


if __name__ == '__main__':
    # Example usage
    pm = PasswordManager()
    
    # Register
    reg = pm.register_user('john', 'SecurePass123!@')
    print(f"Register: {reg}")
    
    # Verify login
    login = pm.verify_login('john', 'SecurePass123!@', reg['hash'])
    print(f"Login: {login}")
    
    # Validate strength
    validator = PasswordValidator()
    strength = validator.get_strength('SecurePass123!@')
    print(f"Strength: {strength}")
