
# FastAPI backendservices

This project is a FastAPI backend application built using SQLAlchemy for database interactions and a domain-driven folder structure for better organization and maintainability.

## Features

* FastAPI framework for building APIs with Python.
* SQLAlchemy ORM for database interactions.
* Domain-driven folder structure for organized code.
* `.env` file for configuration management.
* Alembic for database migrations.
* Health check endpoint.

## Prerequisites
* Python 3.10+
* pip
* A database (PostgreSQL, MySQL, SQLite, etc.)

## Installation

1.  **Clone the repository:**

    ```bash
    git clone <your-repository-url>
    cd fastapi-sqlalchemy-project
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On macOS/Linux
    # venv\Scripts\activate  # On Windows
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Create a `.env` file:**

    Copy the `.env.example` file to `.env` and fill in the required environment variables:

    ```
    DATABASE_URL=postgresql://user:password@host/database_name
    JWT_SECRET_KEY=YOUR_VERY_STRONG_SECRET_KEY
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    AWS_ACCESS_KEY_ID=your-access-key-id
    AWS_SECRET_ACCESS_KEY=your-secret-access-key
    AWS_REGION_NAME=your-region
    AWS_BUCKET_NAME=your-bucket-name
    ```

    Replace the placeholder values with your actual database credentials and secret key.

5.  **Run database migrations:**

    ```bash
    alembic upgrade head
    ```

6.  **Run the application:**

    ```bash
    uvicorn app.main:app --reload --port 8000
    ```

    The application will be accessible at `http://127.0.0.1:8000`.

7.  **Access the API documentation:**

    Open your browser and navigate to `http://127.0.0.1:8000/docs` to view the Swagger UI documentation.

## Folder Structure Diagram
```
BACKENDSERVICES/
├── app/
│   ├── init.py               # Package initialization
│   ├── main.py               # FastAPI application entry point
│   ├── config/               # Service Config
│   │   ├── aws.py
│   │   └── database.py       # Database connection and session management
│   ├── models/               # SQLAlchemy models
│   │   ├── init.py
│   │   └── users.py          # User models
│   ├── api/                  # API endpoints
│   │   ├── init.py
│   │   └── user/             # User domain API
│   │       ├── init.py
│   │       ├── user_routes.py  # User API routes
│   │       ├── user.service.py # User business logic
│   │       └── user.types.py   # User Pydantic schemas/types
│   ├── helpers/                 # utilities
│   │   ├── init.py
│   │   └── auth_utils.py      # Authentication helper functions
├── alembic/                # Alembic migration files
├── venv/                   # Virtual environment
├── .env                    # Environment variables
├── requirements.txt        # Project dependencies
└── README.md               # Project documentation

```