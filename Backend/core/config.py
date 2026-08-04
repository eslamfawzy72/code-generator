from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    OLLAMA_MODEL: str = "qwen2.5:3b"
    OLLAMA_EMBEDDING_MODEL: str = "qllama/bge-small-en-v1.5"

    CHROMA_PATH: str = "./chroma_db"
    CHROMA_COLLECTION: str = "code_generator"


settings = Settings()
