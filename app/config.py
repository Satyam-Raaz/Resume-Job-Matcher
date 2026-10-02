from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    anthropic_api_key: str = ""
    w_semantic: float = 0.6
    w_skills: float = 0.3
    w_experience: float = 0.1

    class Config:
        env_file = ".env"


settings = Settings()
