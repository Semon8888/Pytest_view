import pytest


def pytest_configure(config):
    """
    pytest 启动时自动调用
    :param config:
    :return:
    """
    print("\n ==== 全局配置启动中 ====")
    # 注册自定义marker
    config.addinivalue_line(
        "markers", "smoke: mark test as smoke test"
    )

def pytest_unconfigure(config):
    """
    测试结束时自动调用
    :param config:
    :return:
    """
    print("\n ==== 全局配置结束 ====")

@pytest.fixture(scope="function")
def connect_db():
    print("Starting connect DB")
    yield
    print("Finished connect DB")