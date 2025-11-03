"""
설정 관리 모듈
"""

import os
from pathlib import Path
from typing import Optional, Literal
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # OpenAI
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")

    # Qdrant
    qdrant_host: str = Field(default="localhost", env="QDRANT_HOST")
    qdrant_port: int = Field(default=6333, env="QDRANT_PORT")
    qdrant_api_key: Optional[str] = Field(default=None, env="QDRANT_API_KEY")

    # Embedding
    embedding_model: str = Field(
        default="openai/text-embedding-3-large",
        env="EMBEDDING_MODEL"
    )
    embedding_dimension: int = Field(default=3072, env="EMBEDDING_DIMENSION")

    # Chunking
    chunk_size: int = Field(default=1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, env="CHUNK_OVERLAP")
    min_chunk_size: int = Field(default=100, env="MIN_CHUNK_SIZE")
    max_chunk_size: int = Field(default=2000, env="MAX_CHUNK_SIZE")
    chunking_strategy: Literal["fixed", "recursive", "semantic", "token"] = Field(
        default="recursive",
        env="CHUNKING_STRATEGY"
    )

    # Cache
    cache_enabled: bool = Field(default=True, env="CACHE_ENABLED")
    cache_dir: str = Field(default="data/embeddings", env="CACHE_DIR")

    # Processing
    batch_size: int = Field(default=100, env="BATCH_SIZE")
    save_intermediate: bool = Field(default=True, env="SAVE_INTERMEDIATE")

    # Paths
    pdf_input_dir: str = Field(default="PDF", env="PDF_INPUT_DIR")
    processed_output_dir: str = Field(default="data/processed", env="PROCESSED_OUTPUT_DIR")
    log_dir: str = Field(default="logs", env="LOG_DIR")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_settings() -> Settings:
    """설정 객체 반환"""
    return Settings()


if __name__ == "__main__":
    # 설정 테스트
    settings = get_settings()
    print("=== Configuration ===")
    print(f"OpenAI API Key: {'*' * 20}{settings.openai_api_key[-4:]}")
    print(f"Qdrant: {settings.qdrant_host}:{settings.qdrant_port}")
    print(f"Embedding Model: {settings.embedding_model}")
    print(f"Chunk Size: {settings.chunk_size}")
