import subprocess

if __name__ == "__main__":
    subprocess.run(
        ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app.main:app"]
    )
