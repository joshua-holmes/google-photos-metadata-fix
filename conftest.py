import os


def pytest_sessionstart():
    os.environ["ROOT_DIR"] = os.path.dirname(os.path.abspath(__file__))
