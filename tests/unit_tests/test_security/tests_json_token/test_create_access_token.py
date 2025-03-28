import pytest
from passlib.hash import bcrypt
from security.password import verify_password


def test_verify_password_correct_match():
    plain_password = "correct_password"
    hashed_password = bcrypt.hash(plain_password)
    assert verify_password(plain_password, hashed_password) is True


def test_verify_password_incorrect_match():
    plain_password = "correct_password"
    hashed_password = bcrypt.hash(plain_password)
    assert verify_password("wrong_password", hashed_password) is False


def test_verify_password_empty_plain_password():
    plain_password = ""
    hashed_password = bcrypt.hash("some_password")
    assert verify_password(plain_password, hashed_password) is False


def test_verify_password_empty_hashed_password():
    plain_password = "some_password"
    hashed_password = ""
    with pytest.raises(ValueError):
        verify_password(plain_password, hashed_password)


def test_verify_password_invalid_hash_format():
    plain_password = "password"
    hashed_password = "not_a_valid_hash"
    with pytest.raises(ValueError):
        verify_password(plain_password, hashed_password)
