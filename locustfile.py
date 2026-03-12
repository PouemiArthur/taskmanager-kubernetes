from locust import HttpUser, task

class TaskUser(HttpUser):
    @task(1)
    def view_tasks(self):
        self.client.get("/api/tasks")

    @task(2)
    def create_task(self):
        self.client.post("/api/tasks", json={
            "title": "Simulated Task",
            "description": "Testing load"
        })
