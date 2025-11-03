"""
Answer Generator - LLM-based answer generation using RAG
"""

from typing import List, Dict, Optional
import openai
from .prompts import build_prompt


class SearchResult:
    """Search result data structure (reused from vector_store)"""

    def __init__(self, chunk_id: str, text: str, score: float, metadata: Dict):
        self.chunk_id = chunk_id
        self.text = text
        self.score = score
        self.metadata = metadata


class AnswerGenerator:
    """Generate answers using LLM based on search results"""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4",
        temperature: float = 0.3,
        max_tokens: int = 1000
    ):
        """
        Initialize answer generator

        Args:
            api_key: OpenAI API key
            model: Model name (gpt-4, gpt-3.5-turbo, etc.)
            temperature: Temperature for generation (0.0-1.0)
            max_tokens: Maximum tokens for response
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Initialize OpenAI client
        openai.api_key = api_key

    def generate_answer(
        self,
        query: str,
        search_results: List[SearchResult],
        language: str = "korean"
    ) -> Dict[str, any]:
        """
        Generate answer based on query and search results

        Args:
            query: User query
            search_results: List of SearchResult objects
            language: "korean" or "english"

        Returns:
            Dictionary containing:
                - answer: Generated answer text
                - sources: List of source information
                - model: Model used
                - tokens: Token usage info
        """
        if not search_results:
            no_result_msg = (
                "죄송합니다. 질문과 관련된 내용을 매뉴얼에서 찾을 수 없습니다."
                if language == "korean"
                else "I'm sorry, I couldn't find relevant information in the manuals."
            )
            return {
                "answer": no_result_msg,
                "sources": [],
                "model": self.model,
                "tokens": {"prompt": 0, "completion": 0, "total": 0}
            }

        # Build prompt
        prompt = build_prompt(query, search_results, language)

        try:
            # Call OpenAI API
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt["system"]},
                    {"role": "user", "content": prompt["user"]}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            # Extract answer
            answer = response.choices[0].message.content

            # Extract source information
            sources = self._extract_sources(search_results)

            # Token usage
            tokens = {
                "prompt": response.usage.prompt_tokens,
                "completion": response.usage.completion_tokens,
                "total": response.usage.total_tokens
            }

            return {
                "answer": answer,
                "sources": sources,
                "model": self.model,
                "tokens": tokens
            }

        except Exception as e:
            error_msg = (
                f"답변 생성 중 오류가 발생했습니다: {str(e)}"
                if language == "korean"
                else f"Error generating answer: {str(e)}"
            )
            return {
                "answer": error_msg,
                "sources": [],
                "model": self.model,
                "tokens": {"prompt": 0, "completion": 0, "total": 0}
            }

    def _extract_sources(self, search_results: List[SearchResult]) -> List[Dict]:
        """
        Extract source information from search results

        Args:
            search_results: List of SearchResult objects

        Returns:
            List of source dictionaries
        """
        sources = []
        for idx, result in enumerate(search_results, 1):
            source = {
                "index": idx,
                "document_id": result.metadata.get("document_id", "Unknown"),
                "type": result.metadata.get("type", "Unknown"),
                "language": result.metadata.get("language", "Unknown"),
                "chunk_id": result.chunk_id,
                "score": result.score,
                "text_preview": result.text[:200] + "..." if len(result.text) > 200 else result.text
            }
            sources.append(source)
        return sources

    def generate_streaming_answer(
        self,
        query: str,
        search_results: List[SearchResult],
        language: str = "korean"
    ):
        """
        Generate answer with streaming (for real-time UI updates)

        Args:
            query: User query
            search_results: List of SearchResult objects
            language: "korean" or "english"

        Yields:
            Chunks of generated text
        """
        if not search_results:
            no_result_msg = (
                "죄송합니다. 질문과 관련된 내용을 매뉴얼에서 찾을 수 없습니다."
                if language == "korean"
                else "I'm sorry, I couldn't find relevant information in the manuals."
            )
            yield no_result_msg
            return

        # Build prompt
        prompt = build_prompt(query, search_results, language)

        try:
            # Call OpenAI API with streaming
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt["system"]},
                    {"role": "user", "content": prompt["user"]}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True
            )

            # Yield chunks
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            error_msg = (
                f"답변 생성 중 오류가 발생했습니다: {str(e)}"
                if language == "korean"
                else f"Error generating answer: {str(e)}"
            )
            yield error_msg
