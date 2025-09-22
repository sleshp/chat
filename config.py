from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    SECRET_KEY: str
    ALGORITHM: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()


def get_auth_data():
    return {"secret_key": settings.SECRET_KEY, "algorithm": settings.ALGORITHM}