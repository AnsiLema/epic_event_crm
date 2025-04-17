import warnings

def pytest_configure():
    warnings.filterwarnings(
        "ignore",
        category=DeprecationWarning,
        message=".*crypt.*"
    )