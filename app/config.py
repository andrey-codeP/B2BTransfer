from pydantic_settings import SettingsConfigDict, BaseSettings


class Settings(BaseSettings):
    """синглтон для настроек"""

    POSTGRES_URL: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int
    SECRET_KEY: str
    ALGORITHM: str

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
