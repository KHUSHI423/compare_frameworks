import os
import sys
import unittest
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from fastapi.testclient import TestClient
from app.main import app

class FastAPIApiTests(unittest.TestCase):
    def test_signup_and_login_flow(self):
        with TestClient(app) as client:
            username = "fastapi_test_user"
            email = "fastapi_test@example.com"
            password = "TestPassword123!"

            # Signup
            r = client.post("/auth/signup", json={"username": username, "email": email, "password": password})
            self.assertIn(r.status_code, (201, 409))

            # Login
            r_login = client.post("/auth/login", json={"username": username, "password": password})
            self.assertEqual(r_login.status_code, 200)
            token = r_login.json().get("access_token")
            self.assertIsNotNone(token)

            headers = {"Authorization": f"Bearer {token}"}

            # Me
            r_me = client.get("/auth/me", headers=headers)
            self.assertEqual(r_me.status_code, 200)
            self.assertEqual(r_me.json()["username"], username)

            # Create Board
            r_board = client.post("/boards", json={"title": "Test Board"}, headers=headers)
            self.assertEqual(r_board.status_code, 201)
            board_id = r_board.json()["id"]

            # Create Task
            r_task = client.post(f"/boards/{board_id}/tasks", json={"title": "Test Task", "status": "todo"}, headers=headers)
            self.assertEqual(r_task.status_code, 201)

            # List Tasks
            r_tasks = client.get(f"/boards/{board_id}/tasks", headers=headers)
            self.assertEqual(r_tasks.status_code, 200)
            self.assertGreaterEqual(r_tasks.json()["total"], 1)

if __name__ == "__main__":
    unittest.main()
