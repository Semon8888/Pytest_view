import allure
import pytest


# @pytest.mark.usefixtures("connect_db")
@allure.epic("Self learning project")
@allure.feature("Login test")
@allure.severity(allure.severity_level.BLOCKER)
class TestLogin:
    @pytest.mark.smoke
    @allure.story("user login")
    def test_login(self):
        # 增加测试步骤
        for i in range(1, 5):
            with allure.step("test step" + str(i)):
                print("test_login")

    @allure.story("get user information")
    def test_get_user(self):
        print("test_get_user")
