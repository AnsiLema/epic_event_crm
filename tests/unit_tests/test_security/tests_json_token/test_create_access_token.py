import pytest
import time
from datetime import timedelta, datetime
from unittest.mock import patch
from jwt import ExpiredSignatureError, InvalidTokenError


from security.jwt import create_access_token, decode_access_token

@pytest.fixture
def sample_payload():
    return {"sub": "test_user", "role": "admin"}

def test_create_access_token_default_exp(sample_payload):
    token = create_access_token(data=sample_payload)
    assert isinstance(token, str), "Le token doit être une chaîne de caractères"

def test_create_access_token_custom_exp(sample_payload):
    expires_in = timedelta(minutes=60)  # expires in 60 minutes
    token = create_access_token(data=sample_payload, expires_delta=expires_in)
    assert isinstance(token, str)

def test_decode_access_token_valid(sample_payload):
    token = create_access_token(data=sample_payload)
    decoded = decode_access_token(token)
    assert decoded is not None, "Le token valide ne doit pas être None"
    for k, v in sample_payload.items():
        assert decoded[k] == v

def test_decode_access_token_expired(sample_payload, capsys):
    token = create_access_token(data=sample_payload, expires_delta=timedelta(seconds=-1))

    decoded = decode_access_token(token)
    captured = capsys.readouterr()

    assert decoded is None
    assert "Le token a expiré." in captured.out

def test_decode_access_token_invalid(capsys):
    invalid_token = "xxx.yyy.zzz"

    decoded = decode_access_token(invalid_token)
    captured = capsys.readouterr()

    assert decoded is None
    assert "Token invalide." in captured.out
