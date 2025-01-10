from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Project settings
    postgres_user: str
    postgres_password: str = ""
    postgres_host: str
    postgres_port: int = 5432
    postgres_db: str = ""

    environment: str = "feature"

    class Config:
        env_file = ".env"

    @property
    def get_postgres_uri(self) -> str:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            path=self.postgres_db,
        ).unicode_string()


setting = Settings()  # type: ignore

if __name__ == "__main__":
    print(setting)
    print(setting.get_postgres_uri)
