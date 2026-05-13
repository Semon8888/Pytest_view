import pytest


@pytest.fixture(scope="class", autouse=True)
def clean_environment():
    print("starting clean_environment")
    yield
    print("finished clean_environment")
