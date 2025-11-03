"""
문서 청킹(Chunking) 모듈
- 다양한 청킹 전략 구현
- 의미 단위 기반 청킹
- 메타데이터 보존
"""

import re
from typing import List, Dict, Optional, Literal
from dataclasses import dataclass, field
import hashlib

try:
    from langchain.text_splitter import (
        RecursiveCharacterTextSplitter,
        TokenTextSplitter,
    )
except ImportError:
    from langchain_text_splitters import (
        RecursiveCharacterTextSplitter,
        TokenTextSplitter,
    )


@dataclass
class Chunk:
    """청크 데이터 클래스"""
    chunk_id: str
    text: str
    metadata: Dict = field(default_factory=dict)
    token_count: Optional[int] = None
    char_count: Optional[int] = None

    def __post_init__(self):
        self.char_count = len(self.text)
        # 간단한 토큰 추정 (정확한 계산은 tokenizer 필요)
        if self.token_count is None:
            self.token_count = self._estimate_tokens(self.text)

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """토큰 수 추정 (실제 tokenizer 사용 시 더 정확)"""
        # 영어: ~4 chars/token, 한국어: ~2 chars/token
        # 간단한 휴리스틱
        korean_chars = len(re.findall(r'[가-힣]', text))
        other_chars = len(text) - korean_chars

        estimated = (korean_chars / 2) + (other_chars / 4)
        return int(estimated)


class DocumentChunker:
    """
    문서 청킹 클래스

    지원하는 청킹 전략:
    1. Fixed Size: 고정 크기 청킹
    2. Recursive: 재귀적 문자 기반 청킹
    3. Semantic: 의미 단위 기반 청킹 (섹션, 단락)
    4. Token-based: 토큰 수 기반 청킹
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        min_chunk_size: int = 100,
        max_chunk_size: int = 2000,
    ):
        """
        Args:
            chunk_size: 기본 청크 크기 (문자 수)
            chunk_overlap: 청크 간 중복 영역 크기
            min_chunk_size: 최소 청크 크기
            max_chunk_size: 최대 청크 크기
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size

    def chunk_document(
        self,
        text: str,
        metadata: Dict,
        strategy: Literal["fixed", "recursive", "semantic", "token"] = "recursive"
    ) -> List[Chunk]:
        """
        문서를 청킹

        Args:
            text: 청킹할 텍스트
            metadata: 문서 메타데이터
            strategy: 청킹 전략

        Returns:
            청크 리스트
        """
        if strategy == "fixed":
            chunks = self._chunk_fixed_size(text, metadata)
        elif strategy == "recursive":
            chunks = self._chunk_recursive(text, metadata)
        elif strategy == "semantic":
            chunks = self._chunk_semantic(text, metadata)
        elif strategy == "token":
            chunks = self._chunk_by_tokens(text, metadata)
        else:
            raise ValueError(f"Unknown chunking strategy: {strategy}")

        # 너무 작은 청크 필터링
        chunks = [c for c in chunks if c.char_count >= self.min_chunk_size]

        return chunks

    def _chunk_fixed_size(self, text: str, metadata: Dict) -> List[Chunk]:
        """고정 크기로 청킹"""
        chunks = []
        start = 0
        chunk_index = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]

            chunk_id = self._generate_chunk_id(
                metadata.get("document_id", "doc"),
                chunk_index
            )

            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                "chunk_index": chunk_index,
                "chunk_start": start,
                "chunk_end": end,
            })

            chunk = Chunk(
                chunk_id=chunk_id,
                text=chunk_text,
                metadata=chunk_metadata
            )
            chunks.append(chunk)

            start = end - self.chunk_overlap
            chunk_index += 1

        return chunks

    def _chunk_recursive(self, text: str, metadata: Dict) -> List[Chunk]:
        """
        재귀적 청킹 (LangChain)

        우선순위:
        1. 빈 줄 2개 (\n\n) - 단락 구분
        2. 빈 줄 1개 (\n)
        3. 마침표 (.)
        4. 쉼표 (,)
        5. 공백 ( )
        """
        # 구분자 정의 (한/영 모두 고려)
        separators = [
            "\n\n\n",  # 섹션 구분
            "\n\n",    # 단락 구분
            "\n",      # 줄바꿈
            "。",      # 한국어/일본어 마침표
            ". ",      # 영어 마침표
            "! ",
            "? ",
            ", ",
            " ",
        ]

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=separators,
            length_function=len,
        )

        text_chunks = splitter.split_text(text)
        chunks = []

        for idx, chunk_text in enumerate(text_chunks):
            chunk_id = self._generate_chunk_id(
                metadata.get("document_id", "doc"),
                idx
            )

            chunk_metadata = metadata.copy()
            chunk_metadata["chunk_index"] = idx

            chunk = Chunk(
                chunk_id=chunk_id,
                text=chunk_text,
                metadata=chunk_metadata
            )
            chunks.append(chunk)

        return chunks

    def _chunk_semantic(self, text: str, metadata: Dict) -> List[Chunk]:
        """
        의미 단위 기반 청킹

        섹션/소제목을 기준으로 청킹하고,
        너무 크면 추가로 분할
        """
        # 섹션 헤더 패턴 (다양한 형식 지원)
        section_patterns = [
            r'^#{1,6}\s+.+$',           # Markdown 헤더
            r'^\d+\.\s+.+$',            # 1. 제목
            r'^\d+\.\d+\s+.+$',         # 1.1 제목
            r'^\d+\.\d+\.\d+\s+.+$',    # 1.1.1 제목
            r'^[A-Z][^a-z]*$',          # 대문자만 (TITLE)
            r'^제\d+장.+$',              # 제1장 ...
            r'^제\d+절.+$',              # 제1절 ...
        ]

        # 섹션으로 분할
        sections = self._split_by_sections(text, section_patterns)

        chunks = []
        chunk_index = 0

        for section_title, section_text in sections:
            # 섹션이 너무 크면 추가 분할
            if len(section_text) > self.max_chunk_size:
                # 재귀적 청킹 사용
                sub_chunks = self._chunk_recursive(section_text, metadata)
                for sub_chunk in sub_chunks:
                    sub_chunk.metadata["section_title"] = section_title
                    sub_chunk.chunk_id = self._generate_chunk_id(
                        metadata.get("document_id", "doc"),
                        chunk_index
                    )
                    chunks.append(sub_chunk)
                    chunk_index += 1
            else:
                # 섹션 전체를 하나의 청크로
                chunk_id = self._generate_chunk_id(
                    metadata.get("document_id", "doc"),
                    chunk_index
                )

                chunk_metadata = metadata.copy()
                chunk_metadata.update({
                    "chunk_index": chunk_index,
                    "section_title": section_title,
                })

                chunk = Chunk(
                    chunk_id=chunk_id,
                    text=section_text,
                    metadata=chunk_metadata
                )
                chunks.append(chunk)
                chunk_index += 1

        return chunks

    def _chunk_by_tokens(self, text: str, metadata: Dict) -> List[Chunk]:
        """토큰 수 기반 청킹"""
        # TokenTextSplitter 사용 (OpenAI tokenizer)
        splitter = TokenTextSplitter(
            chunk_size=self.chunk_size // 4,  # chars to tokens 근사
            chunk_overlap=self.chunk_overlap // 4,
        )

        text_chunks = splitter.split_text(text)
        chunks = []

        for idx, chunk_text in enumerate(text_chunks):
            chunk_id = self._generate_chunk_id(
                metadata.get("document_id", "doc"),
                idx
            )

            chunk_metadata = metadata.copy()
            chunk_metadata["chunk_index"] = idx

            chunk = Chunk(
                chunk_id=chunk_id,
                text=chunk_text,
                metadata=chunk_metadata
            )
            chunks.append(chunk)

        return chunks

    def _split_by_sections(
        self,
        text: str,
        patterns: List[str]
    ) -> List[tuple[str, str]]:
        """
        텍스트를 섹션으로 분할

        Returns:
            List of (section_title, section_content)
        """
        lines = text.split('\n')
        sections = []
        current_section = None
        current_content = []

        for line in lines:
            is_header = False

            # 헤더 패턴 매칭
            for pattern in patterns:
                if re.match(pattern, line.strip(), re.MULTILINE):
                    is_header = True
                    break

            if is_header:
                # 이전 섹션 저장
                if current_section is not None:
                    sections.append((
                        current_section,
                        '\n'.join(current_content)
                    ))

                # 새 섹션 시작
                current_section = line.strip()
                current_content = []
            else:
                current_content.append(line)

        # 마지막 섹션 저장
        if current_section is not None:
            sections.append((
                current_section,
                '\n'.join(current_content)
            ))

        # 섹션이 없으면 전체를 하나의 섹션으로
        if not sections:
            sections = [("Document", text)]

        return sections

    def _generate_chunk_id(self, document_id: str, chunk_index: int) -> str:
        """청크 ID 생성"""
        return f"{document_id}_chunk_{chunk_index:04d}"

    def chunk_with_context(
        self,
        text: str,
        metadata: Dict,
        strategy: str = "recursive",
        add_parent_context: bool = True
    ) -> List[Chunk]:
        """
        컨텍스트를 포함한 청킹

        각 청크에 이전/다음 청크의 일부를 컨텍스트로 추가
        """
        chunks = self.chunk_document(text, metadata, strategy)

        if not add_parent_context or len(chunks) <= 1:
            return chunks

        # 각 청크에 컨텍스트 추가
        for i, chunk in enumerate(chunks):
            context_parts = []

            # 이전 청크 컨텍스트
            if i > 0:
                prev_text = chunks[i - 1].text[-100:]  # 마지막 100자
                context_parts.append(f"[이전 내용: ...{prev_text}]")

            # 다음 청크 컨텍스트
            if i < len(chunks) - 1:
                next_text = chunks[i + 1].text[:100]  # 처음 100자
                context_parts.append(f"[다음 내용: {next_text}...]")

            # 메타데이터에 컨텍스트 추가
            if context_parts:
                chunk.metadata["context"] = "\n".join(context_parts)

        return chunks


class TableChunker:
    """
    표(Table)를 위한 특별한 청킹 전략

    표는 구조를 유지하면서 청킹
    """

    def chunk_table(
        self,
        table: List[List[str]],
        table_caption: str,
        metadata: Dict
    ) -> Chunk:
        """
        표를 하나의 청크로 변환

        Args:
            table: 2D 리스트 형태의 표
            table_caption: 표 제목/캡션
            metadata: 메타데이터

        Returns:
            표를 텍스트로 변환한 청크
        """
        # 표를 마크다운 형식으로 변환
        table_text = self._table_to_markdown(table, table_caption)

        chunk_id = self._generate_table_chunk_id(metadata)

        chunk_metadata = metadata.copy()
        chunk_metadata.update({
            "content_type": "table",
            "table_caption": table_caption,
            "table_rows": len(table),
            "table_cols": len(table[0]) if table else 0,
        })

        return Chunk(
            chunk_id=chunk_id,
            text=table_text,
            metadata=chunk_metadata
        )

    def _table_to_markdown(
        self,
        table: List[List[str]],
        caption: str
    ) -> str:
        """표를 마크다운 형식으로 변환"""
        if not table:
            return f"**{caption}**\n(빈 표)"

        markdown = f"**{caption}**\n\n"

        # 헤더
        header = table[0]
        markdown += "| " + " | ".join(header) + " |\n"
        markdown += "|" + "|".join(["---"] * len(header)) + "|\n"

        # 데이터 행
        for row in table[1:]:
            markdown += "| " + " | ".join(row) + " |\n"

        return markdown

    def _generate_table_chunk_id(self, metadata: Dict) -> str:
        """표 청크 ID 생성"""
        doc_id = metadata.get("document_id", "doc")
        page = metadata.get("page", 0)
        table_index = metadata.get("table_index", 0)
        return f"{doc_id}_p{page}_table{table_index}"


# 유틸리티 함수
def chunk_text_simple(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200
) -> List[str]:
    """
    간단한 텍스트 청킹 (Chunk 객체 없이)

    테스트용
    """
    chunker = DocumentChunker(chunk_size=chunk_size, chunk_overlap=overlap)
    chunks = chunker.chunk_document(
        text,
        metadata={"document_id": "temp"},
        strategy="recursive"
    )
    return [c.text for c in chunks]


def get_optimal_chunk_size(text_length: int, language: str = "korean") -> int:
    """
    텍스트 길이와 언어에 따른 최적 청크 크기 추천

    Args:
        text_length: 전체 텍스트 길이
        language: 언어 (korean/english)

    Returns:
        추천 청크 크기
    """
    # 언어별 기본 청크 크기
    base_size = {
        "korean": 1000,
        "english": 1500,
    }.get(language, 1000)

    # 문서 길이에 따라 조정
    if text_length < 5000:
        return base_size // 2
    elif text_length > 100000:
        return base_size * 1.5
    else:
        return base_size


if __name__ == "__main__":
    # 테스트 코드
    sample_text = """
    # CRM 사용 가이드

    ## 1. 거래선 관리

    거래선을 등록하려면 다음 절차를 따르세요.

    ### 1.1 신규 거래선 등록

    1. CRM 메뉴에서 '거래선 관리' 클릭
    2. '신규 등록' 버튼 클릭
    3. 필수 정보 입력
    4. 저장

    ### 1.2 거래선 수정

    기존 거래선 정보를 수정할 수 있습니다.
    """

    # 청킹 테스트
    chunker = DocumentChunker(chunk_size=200, chunk_overlap=50)

    print("=== Recursive Chunking ===")
    chunks = chunker.chunk_document(
        sample_text,
        metadata={"document_id": "test_doc"},
        strategy="recursive"
    )
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i + 1}:")
        print(f"  ID: {chunk.chunk_id}")
        print(f"  Length: {chunk.char_count} chars, ~{chunk.token_count} tokens")
        print(f"  Text: {chunk.text[:100]}...")

    print("\n=== Semantic Chunking ===")
    chunks = chunker.chunk_document(
        sample_text,
        metadata={"document_id": "test_doc"},
        strategy="semantic"
    )
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i + 1}:")
        print(f"  Section: {chunk.metadata.get('section_title', 'N/A')}")
        print(f"  Length: {chunk.char_count} chars")
