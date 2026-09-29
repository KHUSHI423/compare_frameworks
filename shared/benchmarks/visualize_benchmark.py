import os
import sys
import time
import uuid
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def run_django_benchmark(iterations=100):
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
    username = f"dj_bench_{uid}"

    # Setup user
    client.post("/auth/signup/", {"username": username, "email": f"{username}@e.com", "password": "Passw0rd1!"}, format="json")
    login = client.post("/auth/login/", {"username": username, "password": "Passw0rd1!"}, format="json")
    token = login.data["access_token"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    board = client.post("/boards/", {"title": "Bench Board"}, format="json").data
    board_id = board["id"]

    latencies = []
    start_total = time.perf_counter()

    for i in range(iterations):
        t0 = time.perf_counter()
        client.post(f"/boards/{board_id}/tasks/", {"title": f"Task {i}", "status": "todo"}, format="json")
        client.get(f"/boards/{board_id}/tasks/")
        latencies.append((time.perf_counter() - t0) * 1000)

    total_time = time.perf_counter() - start_total
    rps = (iterations * 2) / total_time
    return {"rps": rps, "avg_latency_ms": np.mean(latencies), "p95_latency_ms": np.percentile(latencies, 95), "loc": 200}

def run_fastapi_benchmark(iterations=100):
    sys.path.insert(0, str(ROOT / "fastapi_app"))
    from fastapi.testclient import TestClient
    from fastapi_app.app.main import app

    latencies = []
    with TestClient(app) as client:
        uid = uuid.uuid4().hex[:6]
        username = f"fa_bench_{uid}"

        client.post("/auth/signup", json={"username": username, "email": f"{username}@e.com", "password": "Passw0rd1!"})
        login = client.post("/auth/login", json={"username": username, "password": "Passw0rd1!"})
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        board = client.post("/boards", json={"title": "Bench Board"}, headers=headers).json()
        board_id = board["id"]

        start_total = time.perf_counter()
        for i in range(iterations):
            t0 = time.perf_counter()
            client.post(f"/boards/{board_id}/tasks", json={"title": f"Task {i}", "status": "todo"}, headers=headers)
            client.get(f"/boards/{board_id}/tasks", headers=headers)
            latencies.append((time.perf_counter() - t0) * 1000)

        total_time = time.perf_counter() - start_total
        rps = (iterations * 2) / total_time
        return {"rps": rps, "avg_latency_ms": np.mean(latencies), "p95_latency_ms": np.percentile(latencies, 95), "loc": 450}

def run_flask_benchmark(iterations=100):
    sys.path.insert(0, str(ROOT / "flask_app"))
    from flask_app.app import create_app
    app = create_app()
    client = app.test_client()

    uid = uuid.uuid4().hex[:6]
    username = f"fl_bench_{uid}"

    client.post("/auth/signup", json={"username": username, "email": f"{username}@e.com", "password": "Passw0rd1!"})
    login = client.post("/auth/login", json={"username": username, "password": "Passw0rd1!"})
    token = login.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    board = client.post("/boards", json={"title": "Bench Board"}, headers=headers).get_json()
    board_id = board["id"]

    latencies = []
    start_total = time.perf_counter()

    for i in range(iterations):
        t0 = time.perf_counter()
        client.post(f"/boards/{board_id}/tasks", json={"title": f"Task {i}", "status": "todo"}, headers=headers)
        client.get(f"/boards/{board_id}/tasks", headers=headers)
        latencies.append((time.perf_counter() - t0) * 1000)

    total_time = time.perf_counter() - start_total
    rps = (iterations * 2) / total_time
    return {"rps": rps, "avg_latency_ms": np.mean(latencies), "p95_latency_ms": np.percentile(latencies, 95), "loc": 370}

def generate_visual_dashboard(results):
    # Terminal Display using Rich
    console.print(Panel.fit("[bold cyan]Taskboard Framework Benchmark - Visual Metrics Dashboard[/bold cyan]", border_style="cyan"))

    table = Table(title="Framework Benchmark Results", header_style="bold magenta")
    table.add_column("Framework", style="bold yellow")
    table.add_column("Throughput (Req/Sec)", justify="right", style="green")
    table.add_column("Avg Latency (ms)", justify="right", style="cyan")
    table.add_column("95th Percentile Latency (ms)", justify="right", style="bold red")
    table.add_column("Approx. Lines of Code (LOC)", justify="right", style="blue")

    for fw, metrics in results.items():
        table.add_row(
            fw.upper(),
            f"{metrics['rps']:.2f}",
            f"{metrics['avg_latency_ms']:.2f}",
            f"{metrics['p95_latency_ms']:.2f}",
            str(metrics['loc'])
        )

    console.print(table)

    # Generate Matplotlib Visual Charts
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    fig.suptitle("Taskboard Framework Benchmark Visual Analytics", fontsize=14, fontweight="bold")

    frameworks = list(results.keys())
    rps_values = [results[fw]["rps"] for fw in frameworks]
    avg_lat_values = [results[fw]["avg_latency_ms"] for fw in frameworks]
    p95_lat_values = [results[fw]["p95_latency_ms"] for fw in frameworks]
    loc_values = [results[fw]["loc"] for fw in frameworks]

    colors = ["#4c72b0", "#55a868", "#c44e52"]

    # Chart 1: Throughput vs Latency
    x = np.arange(len(frameworks))
    width = 0.35

    rects1 = ax1.bar(x - width/2, rps_values, width, label="Requests / Sec (RPS)", color="#2b5c8f")
    rects2 = ax1.bar(x + width/2, avg_lat_values, width, label="Avg Latency (ms)", color="#d95f02")

    ax1.set_ylabel("Metric Value")
    ax1.set_title("Throughput (RPS) vs Avg Latency (ms)")
    ax1.set_xticks(x)
    ax1.set_xticklabels([fw.upper() for fw in frameworks], fontweight="bold")
    ax1.legend()
    ax1.grid(axis="y", linestyle="--", alpha=0.7)

    for rect in rects1:
        height = rect.get_height()
        ax1.annotate(f"{height:.1f}", xy=(rect.get_x() + rect.get_width() / 2, height), xytext=(0, 3), textcoords="offset points", ha="center", va="bottom")
    for rect in rects2:
        height = rect.get_height()
        ax1.annotate(f"{height:.1f}ms", xy=(rect.get_x() + rect.get_width() / 2, height), xytext=(0, 3), textcoords="offset points", ha="center", va="bottom")

    # Chart 2: Codebase Lines of Code vs 95th Percentile Latency
    ax2.bar(frameworks, loc_values, color=colors, alpha=0.85, edgecolor="black")
    ax2.set_ylabel("Lines of Code (LOC)")
    ax2.set_title("Codebase Footprint (LOC) by Framework")
    ax2.set_xticklabels([fw.upper() for fw in frameworks], fontweight="bold")
    ax2.grid(axis="y", linestyle="--", alpha=0.7)

    for i, fw in enumerate(frameworks):
        ax2.text(i, loc_values[i] + 10, f"{loc_values[i]} LOC\n(p95: {p95_lat_values[i]:.1f}ms)", ha="center", fontweight="bold")

    plt.tight_layout()
    chart_path = ROOT / "shared" / "benchmarks" / "framework_comparison_chart.png"
    plt.savefig(chart_path, dpi=300)
    plt.close()

    console.print(f"\n[bold green]Visual chart successfully generated and saved to:[/bold green] [yellow]{chart_path}[/yellow]\n")

def main():
    console.print("[bold yellow]Running Taskboard Framework Benchmarks...[/bold yellow]")
    dj_res = run_django_benchmark(iterations=50)
    fa_res = run_fastapi_benchmark(iterations=50)
    fl_res = run_flask_benchmark(iterations=50)

    results = {
        "django": dj_res,
        "fastapi": fa_res,
        "flask": fl_res
    }

    generate_visual_dashboard(results)

if __name__ == "__main__":
    main()
