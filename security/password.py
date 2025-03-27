from passlib.context import CryptContext

# Initialize hashing context with bcrypt algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hash the given password using a secure hashing algorithm.

    This function utilizes a password hashing context to securely hash the
    input password string. The resulting hash is robust and designed for
    secure storage and comparison.

    :param password: Password string to be hashed.
    :type password: str
    :return: A securely hashed representation of the input password.
    :rtype: str
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain text password against a hashed password using a password
    context's verification function. This function is typically used in scenarios
    where confirming user identity or credentials is required.

    :param plain_password: The plain text password to verify.
    :param hashed_password: The hashed password to verify the plain text password
        against.
    :return: True if the plain text password matches the hashed password;
        otherwise, False.
    :rtype: bool
    """
    return pwd_context.verify(plain_password, hashed_password)