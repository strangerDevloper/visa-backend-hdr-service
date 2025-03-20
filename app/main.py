# app/main.py
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware  # Import CORSMiddleware
from .api import users_router, employee_router, country_router, common_router, role_router  # Import country routes 
from .database import Base, engine
from dotenv import load_dotenv
import uvicorn
import argparse

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
    expose_headers=["*"],  # Exposes all headers in the response
)

app.include_router(users_router)
app.include_router(employee_router) #Add employee router
app.include_router(country_router)  # Include country routes
app.include_router(common_router) #Add common router
app.include_router(role_router) #Add role router


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