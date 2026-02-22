import os
from dotenv import load_dotenv

load_dotenv()

class SauceConfig:
    ENVIRONMENTS = {
        "production": "https://www.saucedemo.com"
    }

    def __init__(self, env=None):
        self.env = env or os.getenv("SAUCE_ENV", "production")
        if self.env not in self.ENVIRONMENTS:
            raise ValueError(f"Invalid environment: {self.env}. Choose from {list(self.ENVIRONMENTS.keys())}")
        self.base_url = self.ENVIRONMENTS[self.env]
    
    USERS = {
        "standard": {
            "username": os.getenv("SAUCE_STANDARD_USER", "standard_user"),
            "password": os.getenv("SAUCE_PASS", "secret_sauce")
        },
        "locked_out": {
            "username": os.getenv("SAUCE_LOCKED_USER", "locked_out_user"),
            "password": os.getenv("SAUCE_PASS", "secret_sauce")
        },
        "problem": {
            "username": os.getenv("SAUCE_PROBLEM_USER", "problem_user"),
            "password": os.getenv("SAUCE_PASS", "secret_sauce")
        }
    }

    DEFAULT_TIMEOUT = 10

    MOBILE_DEVICES = {
        "iphone_15": {
            "width": 430,
            "height": 932,
            "pixel_ratio": 3,
            "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Mobile/15E148 Safari/604.1"
        },
        "android": {
            "width": 412,
            "height": 915,
            "pixel_ratio": 2.6,
            "user_agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.7390.123 Mobile Safari/537.36"
        }
    }