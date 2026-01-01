"""JWT Token Validation and Management

Secure JWT token creation, validation, and refresh logic.
Useful for API authentication and user sessions.

Dependencies:
    - PyJWT
    - python-jose
    - fastapi

Example:
    manager = JWTManager(secret_key=os.getenv('JWT_SECRET'))
    token = manager.create_token({'user_id': 123})
    payload = manager.verify_token(token)
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from functools import wraps

try:
    import jwt
    from jwt import PyJWTError
except ImportError:
    raise ImportError("Install PyJWT: pip install PyJWT")


class JWTManager:
    """JWT token management"""

    def __init__(
        self,
        secret_key: str,
        algorithm: str = 'HS256',
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7
    ):
        """Initialize JWT manager
        
        Args:
            secret_key: Secret key for signing
            algorithm: JWT algorithm (HS256, RS256, etc.)
            access_token_expire_minutes: Access token expiry
            refresh_token_expire_days: Refresh token expiry
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days

    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create access token
        
        Args:
            data: Data to encode in token
            expires_delta: Custom expiry time
            
        Returns:
            JWT token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.access_token_expire_minutes
            )
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=self.algorithm
        )
        
        return encoded_jwt

    def create_refresh_token(
        self,
        data: Dict[str, Any]
    ) -> str:
        """Create refresh token
        
        Args:
            data: Data to encode in token
            
        Returns:
            JWT refresh token
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            days=self.refresh_token_expire_days
        )
        to_encode.update({"exp": expire, "type": "refresh"})
        
        encoded_jwt = jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=self.algorithm
        )
        
        return encoded_jwt

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode token
        
        Args:
            token: JWT token
            
        Returns:
            Decoded payload
            
        Raises:
            PyJWTError: If token is invalid
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise PyJWTError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise PyJWTError(f"Invalid token: {str(e)}")

    def refresh_access_token(self, refresh_token: str) -> str:
        """Create new access token from refresh token
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access token
            
        Raises:
            PyJWTError: If refresh token is invalid
        """
        payload = self.verify_token(refresh_token)
        
        if payload.get('type') != 'refresh':
            raise PyJWTError("Not a refresh token")
        
        # Remove exp and type from payload
        payload.pop('exp', None)
        payload.pop('type', None)
        
        return self.create_access_token(payload)

    def decode_token_no_verify(self, token: str) -> Dict[str, Any]:
        """Decode token without verification (for inspection only)
        
        Args:
            token: JWT token
            
        Returns:
            Decoded payload
        """
        return jwt.decode(token, options={"verify_signature": False})

    def is_token_expired(self, token: str) -> bool:
        """Check if token is expired
        
        Args:
            token: JWT token
            
        Returns:
            True if expired, False otherwise
        """
        try:
            payload = self.verify_token(token)
            return False
        except PyJWTError:
            return True

    def get_token_expiry(self, token: str) -> Optional[datetime]:
        """Get token expiry time
        
        Args:
            token: JWT token
            
        Returns:
            Expiry datetime or None
        """
        try:
            payload = jwt.decode(
                token,
                options={"verify_signature": False}
            )
            exp_timestamp = payload.get('exp')
            if exp_timestamp:
                return datetime.fromtimestamp(exp_timestamp)
        except Exception:
            pass
        
        return None


def require_auth(jwt_manager: JWTManager):
    """Decorator for FastAPI route protection
    
    Args:
        jwt_manager: JWTManager instance
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, authorization: str = None, **kwargs):
            if not authorization:
                return {"error": "Missing authorization header"}
            
            try:
                token = authorization.replace('Bearer ', '')
                payload = jwt_manager.verify_token(token)
                kwargs['current_user'] = payload
                return await func(*args, **kwargs)
            except Exception as e:
                return {"error": str(e)}
        
        return wrapper
    return decorator


# FastAPI integration example
"""
from fastapi import FastAPI, Header, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthCredentials

app = FastAPI()
jwt_manager = JWTManager(
    secret_key=os.getenv('JWT_SECRET', 'dev-secret-key')
)
security = HTTPBearer()

@app.post('/login')
async def login(username: str, password: str):
    # Verify credentials (simplified)
    if username == 'admin' and password == 'password':
        access_token = jwt_manager.create_access_token(
            data={'sub': username, 'user_id': 1}
        )
        refresh_token = jwt_manager.create_refresh_token(
            data={'sub': username, 'user_id': 1}
        )
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'bearer'
        }
    raise HTTPException(status_code=401, detail='Invalid credentials')

@app.post('/refresh')
async def refresh(credentials: HTTPAuthCredentials = None):
    try:
        new_token = jwt_manager.refresh_access_token(credentials.credentials)
        return {'access_token': new_token, 'token_type': 'bearer'}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.get('/protected')
async def protected_route(credentials: HTTPAuthCredentials = None):
    try:
        payload = jwt_manager.verify_token(credentials.credentials)
        return {'user_id': payload.get('user_id'), 'message': 'Protected data'}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
"""


if __name__ == '__main__':
    # Example usage
    manager = JWTManager(secret_key='your-secret-key-here')
    
    # Create tokens
    data = {'user_id': 123, 'username': 'john'}
    access_token = manager.create_access_token(data)
    refresh_token = manager.create_refresh_token(data)
    
    print(f"Access Token: {access_token}")
    print(f"Refresh Token: {refresh_token}")
    
    # Verify
    try:
        payload = manager.verify_token(access_token)
        print(f"Verified Payload: {payload}")
    except Exception as e:
        print(f"Verification failed: {e}")
    
    # Check expiry
    is_expired = manager.is_token_expired(access_token)
    print(f"Is Expired: {is_expired}")
    
    # Get expiry time
    expiry = manager.get_token_expiry(access_token)
    print(f"Expiry: {expiry}")
