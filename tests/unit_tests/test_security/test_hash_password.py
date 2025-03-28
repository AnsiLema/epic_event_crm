import pytest
from passlib.hash import bcrypt
from security.password import hash_password


def test_hash_password_returns_string():
    password = "example_password"
    hashed_password = hash_password(password)
    assert isinstance(hashed_password, str)


def test_hash_password_creates_valid_hash():
    password = "example_password"
    hashed_password = hash_password(password)
    assert bcrypt.verify(password, hashed_password)


def test_hash_password_creates_unique_hashes():
    password = "example_password"
    hash_1 = hash_password(password)
    hash_2 = hash_password(password)
    assert hash_1 != hash_2
