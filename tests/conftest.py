import warnings
import pytest
from sqlalchemy.testing import db

from bl.role_bl import RoleBL


def pytest_configure():
    warnings.filterwarnings(
        "ignore",
        category=DeprecationWarning,
        message=".*crypt.*"
    )