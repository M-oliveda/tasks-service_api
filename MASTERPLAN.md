# MASTERPLAN.md - TasksService API

## Project Overview

TasksService is a RESTful API service that allows users to manage their personal tasks. The service provides functionality for user registration and authentication, task creation and management with categories, tags, priorities, due dates, and statuses. The API is designed to be secure, performant, and containerized for easy deployment.

## Technology Stack

### Backend

- **Python 3.10+**
- **Flask** - Web framework
- **Flask-RESTful** - REST API extension for Flask
- **Pydantic** - Data validation and schema definition
- **SQLAlchemy** - ORM for database interactions
- **Alembic** - Database migration tool
- **PyJWT** - JWT authentication
- **Gunicorn** - WSGI HTTP Server for production
- **Pytest** - Testing framework
- **Flask-Swagger-UI** - API documentation

### Database

- **PostgreSQL** - Relational database

### DevOps

- **Docker** - Containerization
- **Docker Compose** - Local development environment

### Development Tools

- **Black** - Python code formatter
- **Isort** - Import sorting
- **Git** - Version control (GitFlow workflow)

## Project Structure

```text
mauricio/tasks-service/api/
├── .env.example              # Example environment variables
├── .gitignore                # Git ignore file
├── README.md                 # Project documentation
├── Dockerfile                # Docker configuration
├── docker-compose.yml        # Docker Compose configuration
├── requirements.txt          # Python dependencies
├── alembic.ini               # Alembic configuration
├── setup.py                  # Package configuration
├── .pre-commit-config.yaml   # Pre-commit hooks
├── .pylintrc                 # Pylint configuration
├── pyproject.toml            # Black, isort configuration
├── migrations/               # Database migrations
│   └── ...
└── app/                      # Application code
    ├── __init__.py           # Application factory
    ├── config.py             # Configuration settings
    ├── wsgi.py               # WSGI entry point
    ├── db.py                 # Database setup
    ├── extensions.py         # Flask extensions
    ├── api/                  # API resources
    │   ├── __init__.py
    │   ├── v1/               # API v1 endpoints
    │   │   ├── __init__.py
    │   │   ├── auth.py       # Authentication endpoints
    │   │   ├── tasks.py      # Task endpoints
    │   │   ├── categories.py # Category endpoints
    │   │   ├── tags.py       # Tag endpoints
    │   │   └── health.py     # Health check endpoint
    ├── models/               # Database models
    │   ├── __init__.py
    │   ├── user.py
    │   ├── task.py
    │   ├── category.py
    │   └── tag.py
    ├── schemas/              # Pydantic schemas
    │   ├── __init__.py
    │   ├── user.py
    │   ├── task.py
    │   ├── category.py
    │   └── tag.py
    ├── services/             # Business logic
    │   ├── __init__.py
    │   ├── auth.py
    │   └── task.py
    ├── utils/                # Utility functions
    │   ├── __init__.py
    │   ├── security.py       # Security helpers
    │   └── logging.py        # Logging configuration
    └── tests/                # Test suite
        ├── conftest.py       # Test configuration
        ├── test_auth.py      # Auth tests
        ├── test_tasks.py     # Task tests
        └── ...
```

## Database Schema

### Users Table

- id (PK)
- username
- email
- password_hash
- created_at
- updated_at
- last_login
- role (admin/user)

### Categories Table

- id (PK)
- name
- description
- user_id (FK)
- created_at
- updated_at

### Tags Table

- id (PK)
- name
- user_id (FK)
- created_at
- updated_at

### Tasks Table

- id (PK)
- title
- description
- status (To Do, In Progress, Ready)
- priority (Low, Medium, High)
- due_date
- category_id (FK)
- user_id (FK)
- created_at
- updated_at

### TaskTags Table (Many-to-Many)

- task_id (FK)
- tag_id (FK)

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token
- `POST /api/v1/auth/refresh` - Refresh JWT token

### Tasks

- `GET /api/v1/tasks` - List all tasks for authenticated user
- `POST /api/v1/tasks` - Create new task
- `GET /api/v1/tasks/{id}` - Get task by ID
- `PUT /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task
- `GET /api/v1/tasks/search` - Search tasks with filters

### Categories

- `GET /api/v1/categories` - List all categories
- `POST /api/v1/categories` - Create new category
- `GET /api/v1/categories/{id}` - Get category by ID
- `PUT /api/v1/categories/{id}` - Update category
- `DELETE /api/v1/categories/{id}` - Delete category

### Tags

- `GET /api/v1/tags` - List all tags
- `POST /api/v1/tags` - Create new tag
- `GET /api/v1/tags/{id}` - Get tag by ID
- `PUT /api/v1/tags/{id}` - Update tag
- `DELETE /api/v1/tags/{id}` - Delete tag

### Health

- `GET /api/v1/health` - Health check endpoint

### Documentation

- `GET /api/v1/docs` - Swagger UI API documentation

## Development Environment Setup

1. Clone the repository
2. Create a `.env` file based on `.env.example`
3. Build and start the containers:

   ```bash
   docker-compose up -d
   ```

4. Run database migrations:

   ```bash
   docker-compose exec api alembic upgrade head
   ```

## Git Workflow

Following GitFlow:

- `main` - Production code
- `develop` - Development code
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `release/*` - Release preparation
- `hotfix/*` - Production hotfixes

## Deployment Environments

1. **Development** - For active development

   - Runs on local machines via Docker Compose
   - Uses development settings with debug enabled

2. **Staging** - For testing

   - Runs in a containerized environment similar to production
   - Uses production settings with testing data

3. **Production** - Live environment
   - Runs in production containers
   - Uses production settings with no debug

## Security Considerations

1. All passwords will be hashed using bcrypt
2. JWT tokens will expire after 12 hours
3. Input validation using Pydantic
4. SQL injection protection via SQLAlchemy ORM
5. CORS configuration for API access
6. Rate limiting for API endpoints
7. Environment variables for sensitive information

## Performance Optimizations

1. Database indexing on frequently queried fields
2. Query optimization with SQLAlchemy
3. Connection pooling for database access
4. Response caching where appropriate
5. Pagination for list endpoints
6. Asynchronous processing for non-critical operations

## Testing Strategy

1. Unit tests for individual components
2. Integration tests for API endpoints
3. Database tests with test database
4. Authentication and authorization tests
5. Performance tests for critical paths

## Next Steps

- [x] 1. Set up project repository and initial structure
- [x] 2. Create Docker and Docker Compose configurations
- [x] 3. Implement database models and migrations
- [x] 4. Develop authentication system
- [x] 5. Implement core task management features
- [x] 6. Add categories and tags functionality
- [x] 7. Implement search and filtering
- [ ] 8. Write comprehensive tests
- [ ] 9. Optimize for performance
- [ ] 10. Prepare deployment configuration
