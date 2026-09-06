import os
import sys

from flask import Flask

from app.main import create_app

APP_ENV: str = os.getenv("APP_ENV", "production").lower()

if APP_ENV != "development":
    print(
        f"Error: run.py is restricted to local development environments only. "
        f"Current APP_ENV is '{APP_ENV}'. Use Gunicorn to run in production.",
        file=sys.stderr,
    )
    sys.exit(1)

app: Flask = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
