import allure

from utils.send_requests import HttpRequests


@allure.epic("Self learning project")
@allure.feature("Logout test")
class TestLogout:
    @allure.story("user logout")
    def test_logout(self):
        print("test_logout")

    @allure.story("click element")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_click_element(self):
        print("test_click_element")

    def test_connect_baidu(self):
        res = HttpRequests().get(
            "https://www.baidu.com")

        assert 200 == res.status_code
