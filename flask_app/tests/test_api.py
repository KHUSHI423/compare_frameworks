import os
import sys
import unittest
from pathlib import Path

# Add app directory to sys.path
APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from app import create_app

class FlaskApiTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_signup_and_login_flow(self):
        username = "flask_test_user"
        email = "flask_test@example.com"
        password = "TestPassword123!"

        # Signup
        r = self.client.post("/auth/signup", json={"username": username, "email": email, "password": password})
        self.assertIn(r.status_code, (201, 409))

        # Login
        r_login = self.client.post("/auth/login", json={"username": username, "password": password})
        self.assertEqual(r_login.status_code, 200)
        token = r_login.get_json().get("access_token")
        self.assertIsNotNone(token)

        headers = {"Authorization": f"Bearer {token}"}

        # Me
        r_me = self.client.get("/auth/me", headers=headers)
        self.assertEqual(r_me.status_code, 200)
        self.assertEqual(r_me.get_json()["username"], username)

        # Create Board
        r_board = self.client.post("/boards", json={"title": "Test Board"}, headers=headers)
        self.assertEqual(r_board.status_code, 201)
        board_id = r_board.get_json()["id"]

        # Create Task
        r_task = self.client.post(f"/boards/{board_id}/tasks", json={"title": "Test Task", "status": "todo"}, headers=headers)
        self.assertEqual(r_task.status_code, 201)

        # List Tasks
        r_tasks = self.client.get(f"/boards/{board_id}/tasks", headers=headers)
        self.assertEqual(r_tasks.status_code, 200)
        self.assertGreaterEqual(r_tasks.get_json()["total"], 1)

if __name__ == "__main__":
    unittest.main()
