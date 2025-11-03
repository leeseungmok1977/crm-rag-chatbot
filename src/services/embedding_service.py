"""
임베딩 서비스 모듈
- 텍스트를 벡터로 변환
- 배치 처리 지원
- 캐싱 기능
- 다양한 임베딩 모델 지원
"""

import hashlib
import json
from typing import List, Dict, Optional, Literal
from pathlib import Path
import time

import numpy as np
from openai import OpenAI
from tqdm import tqdm

# Optional: sentence_transformers for local models
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None


class EmbeddingCache:
    """임베딩 캐시 (로컬 파일 기반)"""

    def __init__(self, cache_dir: str = "data/embeddings"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_key(self, text: str, model: str) -> str:
        """캐시 키 생성"""
        content = f"{model}:{text}"
        return hashlib.md5(content.encode()).hexdigest()

    def get(self, text: str, model: str) -> Optional[List[float]]:
        """캐시에서 임베딩 조회"""
        cache_key = self._get_cache_key(text, model)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if cache_file.exists():
            with open(cache_file, 'r') as f:
                data = json.load(f)
                return data["embedding"]
        return None

    def set(self, text: str, model: str, embedding: List[float]):
        """캐시에 임베딩 저장"""
        cache_key = self._get_cache_key(text, model)
        cache_file = self.cache_dir / f"{cache_key}.json"

        with open(cache_file, 'w') as f:
            json.dump({
                "text": text[:100],  # 처음 100자만 저장 (참고용)
                "model": model,
                "embedding": embedding,
                "timestamp": time.time()
            }, f)

    def clear(self):
        """캐시 전체 삭제"""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()


class EmbeddingService:
    """
    임베딩 서비스

    지원 모델:
    - OpenAI: text-embedding-3-large, text-embedding-3-small
    - SentenceTransformers: 다양한 오픈소스 모델
    """

    def __init__(
        self,
        model_name: str = "openai/text-embedding-3-large",
        api_key: Optional[str] = None,
        cache_enabled: bool = True,
        cache_dir: str = "data/embeddings"
    ):
        """
        Args:
            model_name: 모델 이름 (provider/model 형식)
            api_key: OpenAI API 키 (OpenAI 모델 사용 시)
            cache_enabled: 캐싱 활성화 여부
            cache_dir: 캐시 디렉토리
        """
        self.model_name = model_name
        self.provider, self.model = self._parse_model_name(model_name)

        # 캐시 설정
        self.cache_enabled = cache_enabled
        if cache_enabled:
            self.cache = EmbeddingCache(cache_dir)
        else:
            self.cache = None

        # 모델 초기화
        if self.provider == "openai":
            if not api_key:
                raise ValueError("OpenAI API key is required")
            self.client = OpenAI(api_key=api_key)
            self.dimension = self._get_openai_dimension(self.model)
        elif self.provider == "sentence-transformers":
            if not SENTENCE_TRANSFORMERS_AVAILABLE:
                raise ImportError(
                    "sentence-transformers is not installed. "
                    "Install it with: pip install sentence-transformers"
                )
            self.model_st = SentenceTransformer(self.model)
            self.dimension = self.model_st.get_sentence_embedding_dimension()
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

        print(f"✅ Embedding service initialized: {model_name} (dim={self.dimension})")

    def _parse_model_name(self, model_name: str) -> tuple[str, str]:
        """모델 이름 파싱"""
        if "/" in model_name:
            provider, model = model_name.split("/", 1)
        else:
            # 기본 provider
            provider = "sentence-transformers"
            model = model_name
        return provider, model

    def _get_openai_dimension(self, model: str) -> int:
        """OpenAI 모델의 차원 반환"""
        dimensions = {
            "text-embedding-3-large": 3072,
            "text-embedding-3-small": 1536,
            "text-embedding-ada-002": 1536,
        }
        return dimensions.get(model, 1536)

    def embed_text(self, text: str) -> List[float]:
        """
        단일 텍스트 임베딩

        Args:
            text: 임베딩할 텍스트

        Returns:
            임베딩 벡터
        """
        # 캐시 확인
        if self.cache_enabled:
            cached = self.cache.get(text, self.model_name)
            if cached is not None:
                return cached

        # 임베딩 생성
        if self.provider == "openai":
            embedding = self._embed_openai([text])[0]
        elif self.provider == "sentence-transformers":
            embedding = self._embed_sentence_transformer([text])[0]
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

        # 캐시 저장
        if self.cache_enabled:
            self.cache.set(text, self.model_name, embedding)

        return embedding

    def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 100,
        show_progress: bool = True
    ) -> List[List[float]]:
        """
        배치 텍스트 임베딩

        Args:
            texts: 임베딩할 텍스트 리스트
            batch_size: 배치 크기
            show_progress: 진행률 표시

        Returns:
            임베딩 벡터 리스트
        """
        embeddings = []
        uncached_texts = []
        uncached_indices = []

        # 캐시 확인
        if self.cache_enabled:
            for i, text in enumerate(texts):
                cached = self.cache.get(text, self.model_name)
                if cached is not None:
                    embeddings.append(cached)
                else:
                    embeddings.append(None)
                    uncached_texts.append(text)
                    uncached_indices.append(i)
        else:
            uncached_texts = texts
            uncached_indices = list(range(len(texts)))
            embeddings = [None] * len(texts)

        # 캐시되지 않은 텍스트 임베딩
        if uncached_texts:
            print(f"📊 Embedding {len(uncached_texts)} texts (cached: {len(texts) - len(uncached_texts)})")

            batches = [
                uncached_texts[i:i + batch_size]
                for i in range(0, len(uncached_texts), batch_size)
            ]

            batch_embeddings = []
            iterator = tqdm(batches, desc="Embedding") if show_progress else batches

            for batch in iterator:
                if self.provider == "openai":
                    batch_emb = self._embed_openai(batch)
                elif self.provider == "sentence-transformers":
                    batch_emb = self._embed_sentence_transformer(batch)
                else:
                    raise ValueError(f"Unknown provider: {self.provider}")

                batch_embeddings.extend(batch_emb)

                # Rate limiting for OpenAI
                if self.provider == "openai":
                    time.sleep(0.1)

            # 캐시 저장 및 결과 업데이트
            for idx, text, emb in zip(uncached_indices, uncached_texts, batch_embeddings):
                if self.cache_enabled:
                    self.cache.set(text, self.model_name, emb)
                embeddings[idx] = emb

        return embeddings

    def _embed_openai(self, texts: List[str]) -> List[List[float]]:
        """OpenAI API로 임베딩"""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            embeddings = [data.embedding for data in response.data]
            return embeddings
        except Exception as e:
            print(f"❌ OpenAI embedding error: {e}")
            raise

    def _embed_sentence_transformer(self, texts: List[str]) -> List[List[float]]:
        """SentenceTransformer로 임베딩"""
        embeddings = self.model_st.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False
        )
        return embeddings.tolist()

    def compute_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """
        두 임베딩의 코사인 유사도 계산

        Returns:
            유사도 (0~1)
        """
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        similarity = dot_product / (norm1 * norm2)
        return float(similarity)

    def get_model_info(self) -> Dict:
        """모델 정보 반환"""
        return {
            "model_name": self.model_name,
            "provider": self.provider,
            "model": self.model,
            "dimension": self.dimension,
            "cache_enabled": self.cache_enabled
        }


class MultilingualEmbeddingService:
    """
    다국어 임베딩 서비스

    언어별로 최적화된 모델 사용
    """

    def __init__(
        self,
        default_model: str = "openai/text-embedding-3-large",
        language_models: Optional[Dict[str, str]] = None,
        api_key: Optional[str] = None
    ):
        """
        Args:
            default_model: 기본 모델
            language_models: 언어별 모델 매핑 (예: {"korean": "model1", "english": "model2"})
            api_key: OpenAI API 키
        """
        self.default_model = default_model
        self.language_models = language_models or {}
        self.api_key = api_key

        # 언어별 서비스 초기화
        self.services: Dict[str, EmbeddingService] = {}

        # 기본 서비스
        self.services["default"] = EmbeddingService(
            model_name=default_model,
            api_key=api_key
        )

        # 언어별 서비스
        for lang, model in self.language_models.items():
            self.services[lang] = EmbeddingService(
                model_name=model,
                api_key=api_key
            )

    def embed_text(self, text: str, language: str = "auto") -> List[float]:
        """
        텍스트 임베딩 (언어 자동 선택)

        Args:
            text: 임베딩할 텍스트
            language: 언어 ("auto"면 자동 감지)

        Returns:
            임베딩 벡터
        """
        if language == "auto":
            language = self._detect_language(text)

        service = self.services.get(language, self.services["default"])
        return service.embed_text(text)

    def embed_batch(
        self,
        texts: List[str],
        languages: Optional[List[str]] = None,
        batch_size: int = 100
    ) -> List[List[float]]:
        """
        배치 텍스트 임베딩

        Args:
            texts: 임베딩할 텍스트 리스트
            languages: 각 텍스트의 언어 (None이면 자동 감지)
            batch_size: 배치 크기

        Returns:
            임베딩 벡터 리스트
        """
        if languages is None:
            languages = [self._detect_language(text) for text in texts]

        # 언어별로 그룹화
        groups: Dict[str, List[tuple[int, str]]] = {}
        for i, (text, lang) in enumerate(zip(texts, languages)):
            if lang not in groups:
                groups[lang] = []
            groups[lang].append((i, text))

        # 언어별로 임베딩
        embeddings = [None] * len(texts)
        for lang, items in groups.items():
            indices, lang_texts = zip(*items)
            service = self.services.get(lang, self.services["default"])
            lang_embeddings = service.embed_batch(lang_texts, batch_size)

            for idx, emb in zip(indices, lang_embeddings):
                embeddings[idx] = emb

        return embeddings

    def _detect_language(self, text: str) -> str:
        """간단한 언어 감지"""
        from langdetect import detect

        try:
            lang_code = detect(text)
            lang_map = {
                "ko": "korean",
                "en": "english",
                "ja": "japanese",
                "zh-cn": "chinese",
            }
            return lang_map.get(lang_code, "default")
        except:
            return "default"


# 유틸리티 함수
def create_embedding_service(
    provider: Literal["openai", "local"] = "openai",
    api_key: Optional[str] = None
) -> EmbeddingService:
    """
    간편한 임베딩 서비스 생성

    Args:
        provider: "openai" 또는 "local"
        api_key: OpenAI API 키

    Returns:
        EmbeddingService 인스턴스
    """
    if provider == "openai":
        if not api_key:
            raise ValueError("OpenAI API key is required")
        return EmbeddingService(
            model_name="openai/text-embedding-3-large",
            api_key=api_key
        )
    elif provider == "local":
        # 로컬 모델 (무료)
        return EmbeddingService(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")


if __name__ == "__main__":
    # 테스트 코드
    import os
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    # OpenAI 임베딩 테스트
    print("=== OpenAI Embedding Test ===")
    service = EmbeddingService(
        model_name="openai/text-embedding-3-large",
        api_key=api_key
    )

    text1 = "거래선 등록 방법을 알려주세요"
    text2 = "How to register a new account"
    text3 = "CRM 시스템 사용법"

    # 단일 임베딩
    emb1 = service.embed_text(text1)
    print(f"Text: {text1}")
    print(f"Embedding dim: {len(emb1)}")
    print(f"First 5 values: {emb1[:5]}")

    # 배치 임베딩
    texts = [text1, text2, text3]
    embeddings = service.embed_batch(texts)
    print(f"\nBatch embedding: {len(embeddings)} texts")

    # 유사도 계산
    similarity = service.compute_similarity(embeddings[0], embeddings[2])
    print(f"\nSimilarity between '{text1}' and '{text3}': {similarity:.4f}")

    # 로컬 모델 테스트
    print("\n=== Local Model Test ===")
    local_service = EmbeddingService(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    emb_local = local_service.embed_text(text1)
    print(f"Local embedding dim: {len(emb_local)}")
