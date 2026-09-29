import os
import sys
import uuid
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

class FrameworkRouteParityTests(unittest.TestCase):
    def test_django_routes(self):
        sys.path.insert(0, str(ROOT / "django_app"))
        os.environ["DJANGO_SETTINGS_MODULE"] = "taskboard_django.settings"
        import django
        django.setup()
        from django.conf import settings
        settings.DATABASES["default"]["NAME"] = ":memory:"
        from django.core.management import call_command
        call_command("migrate", run_syncdb=True, verbosity=0)

        from rest_framework.test import APIClient
        client = APIClient()

        uid = uuid.uuid4().hex[:6]
        username = f"user_dj_{uid}"
        email = f"user_dj_{uid}@example.com"

        # Signup
        signup = client.post(
            "/auth/signup/",
            {"username": username, "email": email, "password": "Passw0rd1!"},
            format="json",
        )
        self.assertEqual(signup.status_code, 201)

        # Duplicate signup -> 409
        dup_signup = client.post(
            "/auth/signup/",
            {"username": username, "email": f"other_{uid}@example.com", "password": "Passw0rd1!"},
            format="json",
        )
        self.assertEqual(dup_signup.status_code, 409)

        # Login
        login = client.post(
            "/auth/login/",
            {"username": username, "password": "Passw0rd1!"},
            format="json",
        )
        self.assertEqual(login.status_code, 200)
        token = login.data["access_token"]
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        # Me
        me = client.get("/auth/me/")
        self.assertEqual(me.status_code, 200)

        # Create Board
        board = client.post("/boards/", {"title": "Parity Board"}, format="json")
        self.assertEqual(board.status_code, 201)
        board_id = board.data["id"]

        # Create Task
        task = client.post(
            f"/boards/{board_id}/tasks/",
            {"title": "Parity Task", "status": "todo"},
            format="json",
        )
        self.assertEqual(task.status_code, 201)

        # List Tasks
        tasks = client.get(f"/boards/{board_id}/tasks/")
        self.assertEqual(tasks.status_code, 200)

    def test_fastapi_routes(self):
        sys.path.insert(0, str(ROOT / "fastapi_app"))
        from fastapi.testclient import TestClient
        from fastapi_app.app.main import app

        with TestClient(app) as client:
            uid = uuid.uuid4().hex[:6]
            username = f"user_fa_{uid}"
            email = f"user_fa_{uid}@example.com"

            signup = client.post(
                "/auth/signup",
                json={"username": username, "email": email, "password": "Passw0rd1!"},
            )
            self.assertEqual(signup.status_code, 201)

            dup_signup = client.post(
                "/auth/signup",
                json={"username": username, "email": f"other_{uid}@example.com", "password": "Passw0rd1!"},
            )
            self.assertEqual(dup_signup.status_code, 409)

            login = client.post(
                "/auth/login",
                json={"username": username, "password": "Passw0rd1!"},
            )
            self.assertEqual(login.status_code, 200)
            headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

            me = client.get("/auth/me", headers=headers)
            self.assertEqual(me.status_code, 200)

            board = client.post("/boards", json={"title": "Parity Board"}, headers=headers)
            self.assertEqual(board.status_code, 201)
            board_id = board.json()["id"]

            task = client.post(
                f"/boards/{board_id}/tasks",
                json={"title": "Parity Task", "status": "todo"},
                headers=headers,
            )
            self.assertEqual(task.status_code, 201)

            tasks = client.get(f"/boards/{board_id}/tasks", headers=headers)
            self.assertEqual(tasks.status_code, 200)

    def test_flask_routes(self):
        sys.path.insert(0, str(ROOT / "flask_app"))
        from flask_app.app import create_app
        app = create_app()
        client = app.test_client()

        uid = uuid.uuid4().hex[:6]
        username = f"user_fl_{uid}"
        email = f"user_fl_{uid}@example.com"

        signup = client.post(
            "/auth/signup",
            json={"username": username, "email": email, "password": "Passw0rd1!"},
        )
        self.assertEqual(signup.status_code, 201)

        dup_signup = client.post(
            "/auth/signup",
            json={"username": username, "email": f"other_{uid}@example.com", "password": "Passw0rd1!"},
        )
        self.assertEqual(dup_signup.status_code, 409)

        login = client.post(
            "/auth/login",
            json={"username": username, "password": "Passw0rd1!"},
        )
        self.assertEqual(login.status_code, 200)
        headers = {"Authorization": f"Bearer {login.get_json()['access_token']}"}

        me = client.get("/auth/me", headers=headers)
        self.assertEqual(me.status_code, 200)

        board = client.post("/boards", json={"title": "Parity Board"}, headers=headers)
        self.assertEqual(board.status_code, 201)
        board_id = board.get_json()["id"]

        task = client.post(
            f"/boards/{board_id}/tasks",
            json={"title": "Parity Task", "status": "todo"},
            headers=headers,
        )
        self.assertEqual(task.status_code, 201)

        tasks = client.get(f"/boards/{board_id}/tasks", headers=headers)
        self.assertEqual(tasks.status_code, 200)

if __name__ == "__main__":
    unittest.main()