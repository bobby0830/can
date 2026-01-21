import requests
import json
import unittest
import time

BASE_URL = "http://127.0.0.1:5000"

class TestCalendarAPI(unittest.TestCase):
    
    def test_01_index(self):
        """測試伺服器是否運行"""
        response = requests.get(f"{BASE_URL}/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Calendar Suggestion API is running", response.text)

    def test_02_save_profile(self):
        """測試儲存用戶興趣"""
        payload = {
            "username": "test_user",
            "interests": ["AI", "Machine Learning"]
        }
        response = requests.post(
            f"{BASE_URL}/user/profile",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")

    def test_03_get_recommendations(self):
        """測試獲取推薦事件"""
        # 確保用戶已存在
        requests.post(
            f"{BASE_URL}/user/profile",
            json={"username": "test_user", "interests": ["AI"]},
            headers={"Content-Type": "application/json"}
        )
        
        response = requests.get(f"{BASE_URL}/recommendations?username=test_user")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("events", data)
        self.assertIsInstance(data["events"], list)
        
        if len(data["events"]) > 0:
            event = data["events"][0]
            self.assertIn("title", event)
            self.assertIn("date", event)
            self.assertIn("reason", event)
            self.assertIn("score", event)

if __name__ == "__main__":
    print("Starting API Tests...")
    unittest.main()








