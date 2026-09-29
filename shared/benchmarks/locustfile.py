import random
# pyrefly: ignore [missing-import]
from locust import HttpUser, task, between

class TaskboardBenchmarkUser(HttpUser):
    wait_time = between(0.1, 0.5)

    def on_start(self):
        self.username = f"user_{random.randint(1, 1000000)}"
        self.email = f"{self.username}@example.com"
        self.password = "BenchmarkPass123!"
        self.headers = {}

        # Signup
        res = self.client.post("/auth/signup", json={
            "username": self.username,
            "email": self.email,
            "password": self.password
        })
        if res.status_code not in (201, 200):
            # Try login if user exists
            pass

        # Login
        login_res = self.client.post("/auth/login", json={
            "username": self.username,
            "password": self.password
        })
        if login_res.status_code == 200:
            token = login_res.json().get("access_token")
            if token:
                self.headers = {"Authorization": f"Bearer {token}"}

    @task(3)
    def list_boards(self):
        self.client.get("/boards", headers=self.headers)

    @task(2)
    def create_and_manage_board(self):
        res = self.client.post("/boards", json={"title": f"Board {random.randint(1, 1000)}"}, headers=self.headers)
        if res.status_code == 201:
            board_id = res.json().get("id")
            if board_id:
                # Add a task
                t_res = self.client.post(f"/boards/{board_id}/tasks", json={
                    "title": "Bench Task",
                    "status": "todo",
                    "description": "Load test task description"
                }, headers=self.headers)
                if t_res.status_code == 201:
                    task_id = t_res.json().get("id")
                    # Update task status
                    self.client.patch(f"/boards/{board_id}/tasks/{task_id}", json={"status": "in_progress"}, headers=self.headers)
                # List tasks
                self.client.get(f"/boards/{board_id}/tasks", headers=self.headers)
                # Export CSV
                self.client.get(f"/boards/{board_id}/export", headers=self.headers)

    @task(1)
    def get_me(self):
        self.client.get("/auth/me", headers=self.headers)
