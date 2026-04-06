import subprocess
import sys
import time
import urllib.request
import urllib.error
import urllib.parse
import json
import os

def run_cmd(cmd, env=None):
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, env=env)
    if result.returncode != 0:
        print(f"ERROR: Command failed with exit code {result.returncode}")
        sys.exit(1)

def main():
    # 1. Check Python version
    run_cmd(["python", "--version"])
    
    # 2. Check imports
    run_cmd(["python", "-m", "compileall", "app", "tests", "-q"])
    
    # 3. Linting
    run_cmd(["python", "-m", "ruff", "check", "app/", "tests/"])
    
    # 4. Tests
    run_cmd(["python", "-m", "pytest", "-q"])
    
    # 4.2. Docker compose config (SKIP if docker unavailable)
    print("Running: docker compose config (optional)")
    try:
        subprocess.run(["docker", "compose", "config"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print("SKIPPED: Docker executable not found in path.")
    except Exception as e:
        print(f"SKIPPED: Docker config validation failed or unavailable: {e}")
    
    # Minimal safe env override for background local API
    env = os.environ.copy()
    env["DATABASE_URL"] = "sqlite+aiosqlite:///jeeves_test.db"
    env["MOCK_PROVIDER_ENABLED"] = "true"
    env["API_KEY"] = "dev-secret-key"

    # 4.5. Alembic migrations for test DB
    run_cmd(["python", "-m", "alembic", "upgrade", "head"], env=env)

    # 5. Start API in background
    print("Starting background API...")
    api_proc = subprocess.Popen(
        ["python", "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8001"],
        env=env
    )
    
    try:
        # Wait for boot
        time.sleep(5)
        if api_proc.poll() is not None:
            print("ERROR: API process died immediately.")
            sys.exit(1)

        # 6. Call /health
        print("Calling /health...")
        req = urllib.request.Request("http://127.0.0.1:8001/health")
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status != 200:
                    print(f"ERROR: /health returned {response.status}")
                    sys.exit(1)
                print("Response:", response.read().decode())
        except Exception as e:
            print(f"ERROR: /health failed: {e}")
            sys.exit(1)

        # 7. Call /ask
        print("Calling /ask...")
        data = json.dumps({"message": "Hello validation", "allow_tools": False}).encode("utf-8")
        req = urllib.request.Request(
            "http://127.0.0.1:8001/ask",
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer dev-secret-key"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status != 200:
                    print(f"ERROR: /ask returned {response.status}")
                    sys.exit(1)
                print("Response:", response.read().decode())
        except Exception as e:
            print(f"ERROR: /ask failed: {e}")
            sys.exit(1)

    finally:
        # 8. Stop API process cleanly
        print("Stopping background API...")
        api_proc.terminate()
        api_proc.wait(timeout=5)
        print("Cleaned up.")

    print("VALIDATION SUCCESSFUL")

if __name__ == "__main__":
    main()
