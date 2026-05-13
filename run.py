import subprocess

import pytest

if __name__ == '__main__':
    pytest.main()
    subprocess.run(
        "allure generate ./allure-results -o ./allure-reports --clean"
        ,shell=True
    )