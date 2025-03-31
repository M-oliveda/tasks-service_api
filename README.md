# TasksService API

A RESTful API service for managing personal tasks with user authentication, categories, tags, priorities, and statuses.

## Technologies Used

- **Backend**: Python, Flask, SQLAlchemy, Pydantic
- **Database**: PostgreSQL
- **Authentication**: JWT
- **Containerization**: Docker, Docker Compose
- **Testing**: Pytest

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL
- Docker and Docker Compose
- Git

### Local Development Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/mauricio/tasksservice/api.git
   cd tasksservice/api
   ```

2. Create a virtual environment in a `.env` folder:

   ```bash
   python -m venv .env
   ```

3. Activate the virtual environment:

   - On Windows:

     ```bash
     .env\Scripts\activate
     ```

   - On macOS and Linux:

     ```bash
     source .env/bin/activate
     ```

4. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Create a `.env` file based on the example:

   ```bash
   cp .env.example .env
   ```

6. Update the environment variables in the `.env` file as needed. See [.env.example](./.env.example) for the list of required variables.

7. Run database migrations:

   ```bash
   flask db upgrade
   ```

8. Start the development server:

   ```bash
   flask run
   ```

### Docker Setup

1. Create a `.env` file based on the example:

   ```bash
   cp .env.example .env
   ```

2. Update the environment variables in the `.env` file as needed.

3. Build and start the containers:

   ```bash
   docker-compose up -d
   ```

4. Apply database migrations:

   ```bash
   docker-compose exec api alembic upgrade head
   ```

5. Access the API at `http://localhost:5000`

### Development Commands

- Run tests:

  ```bash
  # Local
  pytest

  # Docker
  docker-compose exec api pytest
  ```

- Create a new migration:

  ```bash
  # Local
  flask db revision -m "description"

  # Docker
  docker-compose exec api alembic revision -m "description"
  ```

- Format code:

  ```bash
  # Local
  black app
  isort app

  # Docker
  docker-compose exec api black app
  docker-compose exec api isort app
  ```

## API Documentation

API documentation is available at `/api/v1/docs` when the service is running.

## Environment Variables

Checkout the [`.env.example`](./.env.example) file to get all the environment variables.
