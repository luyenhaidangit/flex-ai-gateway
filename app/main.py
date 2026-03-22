from fastapi import FastAPI

from app.bootstrap.factory import create_application

app: FastAPI = create_application()
