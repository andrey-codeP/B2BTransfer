from pydantic_settings import SettingsConfigDict, BaseSettings


class Settings(BaseSettings):
    """синглтон для настроек"""

    DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
