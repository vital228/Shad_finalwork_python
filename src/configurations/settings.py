from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["settings"]

class Settings(BaseSettings):
    # for PostgreSQL
    db_host: str
    db_name: str
    db_username: str
    db_password: str
    db_test_name: str = "fastapi_project_test_db"
    max_connection_count: int = 10
    ALGORITHM: str = "HS256"
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 100000

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_username}:{self.db_password}@{self.db_host}/{self.db_name}"

    @property
    def database_test_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_username}:{self.db_password}@{self.db_host}/{self.db_test_name}"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
