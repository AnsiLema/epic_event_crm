from datetime import datetime, timedelta, timezone
import jwt
import pytest
from jwt import ExpiredSignatureError, InvalidTokenError
from security.jwt import decode_access_token
from dotenv import load_dotenv
import os

load_dotenv()

# Mock constants to use in tests
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
ALGORITHM = "HS256"


# Helper function to create mock tokens
def create_token(expiration_seconds):
    payload = {"user_id": 123, "exp": datetime.now(timezone.utc) + timedelta(seconds=expiration_seconds)}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def test_decode_access_token_valid_token():
    token = create_token(10)
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["user_id"] == 123


def test_decode_access_token_expired_token():
    token = create_token(-10)
    decoded = decode_access_token(token)
    assert decoded is None


def test_decode_access_token_invalid_token():
    token = "invalid.token.signature"
    decoded = decode_access_token(token)
    assert decoded is None
