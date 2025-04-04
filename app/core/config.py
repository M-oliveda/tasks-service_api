"""Configuration settings for the TasksService API using pydantic-settings."""
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings using pydantic-settings."""

    # Flask
    SECRET_KEY: str = Field(
        default="my-secret-key",
        description="App secret key",
        examples=["my-secret-key"],
    )
    FLASK_ENV: str = Field(
        default="development", description="Flask environment", examples=["development"]
    )
    DEBUG: bool = Field(default=True, description="Debug mode", examples=[True])

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI: str = Field(
        default="postgresql://postgres:postgres@db:5432/tasksservice",
        description="Database URL",
        examples=["postgresql://postgres:postgres@db:5432/tasksservice"],
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = Field(
        default=False, description="SQLAlchemy track modifications", examples=[False]
    )

    # JWT
    JWT_SECRET_KEY: str = Field(
        default="your-jwt-secret-key",
        description="JWT secret key",
        examples=["your-jwt-secret-key"],
    )
    JWT_ACCESS_TOKEN_EXPIRES: int = Field(
        # 12 hours
        default=43200,
        description="JWT access token expiration time in seconds",
        examples=[43200],
    )

    # Logging
    LOG_LEVEL: str = Field(
        default="INFO", description="Logging level", examples=["INFO"]
    )

    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="CORS origins",
        examples=["http://localhost:3000", "http://localhost:8080"],
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v) -> List[str]:
        """Assemble CORS origins."""
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    # Rate limiting
    RATELIMIT_DEFAULT: str = Field(
        default="100/hour", description="Default rate limit", examples=["100/hour"]
    )
    RATELIMIT_STORAGE_URI: str = Field(
        default="memory://",
        description="Rate limit storage URI",
        examples=["memory://"],
    )
    RATELIMIT_ENABLED: bool = Field(
        default=False, description="Enable rate limiting", examples=[False]
    )

    # Swagger
    SWAGGER: dict = Field(
        default={"title": "Tasks Service API", "uiversion": 3, "version": "0.1.0"},
        description="Swagger configuration",
        examples=[{"title": "Tasks Service API", "uiversion": 3, "version": "0.1.0"}],
    )

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )


class TestingSettings(Settings):
    """Testing configuration."""

    TESTING: bool = Field(default=True, description="Testing mode", examples=[True])
    DEBUG: bool = Field(default=True, description="Debug mode", examples=[True])
    SQLALCHEMY_DATABASE_URI: str = Field(
        default="postgresql://postgres:postgres@db:5432/tasksservice_test",
        description="Database URL",
        examples=["postgresql://postgres:postgres@db:5432/tasksservice_test"],
    )
    JWT_ACCESS_TOKEN_EXPIRES: int = Field(
        # 1 hour for testing
        default=3600,
        description="JWT access token expiration time in seconds",
        examples=[3600],
    )
    PRESERVE_CONTEXT_ON_EXCEPTION: bool = Field(
        default=False, description="Preserve context on exception", examples=[False]
    )
    RATELIMIT_ENABLED: bool = Field(
        default=False, description="Enable rate limiting", examples=[False]
    )


class DevelopmentSettings(Settings):
    """Development configuration."""

    DEBUG: bool = Field(default=True, description="Debug mode", examples=[True])


class ProductionSettings(Settings):
    """Production configuration."""

    DEBUG: bool = Field(default=False, description="Debug mode", examples=[False])
    TESTING: bool = Field(default=False, description="Testing mode", examples=[False])
    RATELIMIT_ENABLED: bool = Field(
        default=True, description="Enable rate limiting", examples=[True]
    )

    # Security
    SESSION_COOKIE_SECURE: bool = Field(
        default=True, description="Session cookie secure", examples=[True]
    )
    REMEMBER_COOKIE_SECURE: bool = Field(
        default=True, description="Remember cookie secure", examples=[True]
    )


# Map environment to configurations
config_by_name = {
    "development": DevelopmentSettings,
    "testing": TestingSettings,
    "production": ProductionSettings,
}


def get_settings(env: str = "development") -> Settings:
    """Get settings for the current environment."""
    return config_by_name.get(env, DevelopmentSettings)()
