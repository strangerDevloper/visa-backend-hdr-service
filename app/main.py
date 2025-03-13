# app/main.py
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from . import models, database
from .api import  users_router
from .database import Base, engine
from dotenv import load_dotenv
import uvicorn
import argparse

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users_router)

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """
    Endpoint to check the health of the API.
    """
    return JSONResponse(content={"status": "ok"})

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    config = uvicorn.Config("app.main:app", port=args.port, log_level="info", reload=True)
    server = uvicorn.Server(config)
    print(f"Server is running at http://127.0.0.1:{config.port}")
    server.run()