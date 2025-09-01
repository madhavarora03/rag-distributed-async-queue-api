from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # R2 Bucket Config
    r2_account_id: str
    r2_access_key_id: str
    r2_secret_access_key: str
    r2_bucket_name: str

    # OpenAI API
    openai_api_key: str

    # Mongo DB
    mongo_user: str
    mongo_pass: str
    mongo_host: str
    mongo_port: int
    db_name: str

    # vector_db config
    qdrant_uri: str

    # auth related stuff
    secret_key: str

    class Config:
        env_file = ".env"


settings = Settings()  # type: ignore
