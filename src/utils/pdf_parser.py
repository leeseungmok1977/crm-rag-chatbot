"""
PDF 파싱 모듈
- PDF 문서에서 텍스트, 이미지, 메타데이터 추출
- 레이아웃 정보 보존
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

import fitz  # PyMuPDF
import pdfplumber
from langdetect import detect
from tqdm import tqdm


@dataclass
class PDFPage:
    """단일 페이지 정보"""
    page_number: int
    text: str
    images: List[Dict] = field(default_factory=list)
    tables: List[List[List[str]]] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


@dataclass
class PDFDocument:
    """PDF 문서 전체 정보"""
    file_path: str
    total_pages: int
    pages: List[PDFPage]
    metadata: Dict
    language: str


class PDFParser:
    """
    PDF 문서 파싱 클래스

    Features:
    - 텍스트 추출 (레이아웃 보존)
    - 표 추출
    - 이미지 추출
    - 메타데이터 추출
    - 언어 감지
    """

    def __init__(self, preserve_layout: bool = True):
        self.preserve_layout = preserve_layout

    def parse(self, pdf_path: str, extract_images: bool = False) -> PDFDocument:
        """
        PDF 문서 파싱

        Args:
            pdf_path: PDF 파일 경로
            extract_images: 이미지 추출 여부

        Returns:
            PDFDocument 객체
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        print(f"📄 Parsing PDF: {pdf_path.name}")

        # PyMuPDF로 기본 정보 및 이미지 추출
        doc_fitz = fitz.open(str(pdf_path))
        total_pages = len(doc_fitz)

        # pdfplumber로 텍스트 및 표 추출
        pages = []
        with pdfplumber.open(str(pdf_path)) as pdf_plumber:
            for page_num in tqdm(range(total_pages), desc="Processing pages"):
                page_fitz = doc_fitz[page_num]
                page_plumber = pdf_plumber.pages[page_num]

                # 텍스트 추출
                text = self._extract_text(page_plumber, page_fitz)

                # 표 추출
                tables = self._extract_tables(page_plumber)

                # 이미지 추출 (옵션)
                images = []
                if extract_images:
                    images = self._extract_images(page_fitz, page_num)

                # 페이지 메타데이터
                page_metadata = {
                    "width": page_plumber.width,
                    "height": page_plumber.height,
                    "has_tables": len(tables) > 0,
                    "has_images": len(images) > 0,
                }

                page_obj = PDFPage(
                    page_number=page_num + 1,
                    text=text,
                    images=images,
                    tables=tables,
                    metadata=page_metadata
                )
                pages.append(page_obj)

        # 문서 메타데이터
        doc_metadata = self._extract_document_metadata(doc_fitz)

        # 언어 감지
        language = self._detect_language(pages)

        doc_fitz.close()

        document = PDFDocument(
            file_path=str(pdf_path),
            total_pages=total_pages,
            pages=pages,
            metadata=doc_metadata,
            language=language
        )

        print(f"✅ Parsed {total_pages} pages, Language: {language}")
        return document

    def _extract_text(self, page_plumber, page_fitz) -> str:
        """
        페이지에서 텍스트 추출

        pdfplumber는 레이아웃 정보가 더 정확하고,
        PyMuPDF는 속도가 빠름. 상황에 따라 선택.
        """
        if self.preserve_layout:
            # pdfplumber: 레이아웃 보존
            text = page_plumber.extract_text(layout=True)
        else:
            # PyMuPDF: 빠른 추출
            text = page_fitz.get_text()

        # 텍스트 정제
        text = self._clean_text(text)
        return text

    def _extract_tables(self, page_plumber) -> List[List[List[str]]]:
        """페이지에서 표 추출"""
        tables = page_plumber.extract_tables()
        return tables if tables else []

    def _extract_images(self, page_fitz, page_num: int) -> List[Dict]:
        """
        페이지에서 이미지 추출

        Returns:
            이미지 정보 리스트 (바이너리는 저장하지 않고 위치 정보만)
        """
        images = []
        image_list = page_fitz.get_images()

        for img_index, img_info in enumerate(image_list):
            xref = img_info[0]

            # 이미지 메타데이터만 저장
            images.append({
                "image_index": img_index,
                "xref": xref,
                "page": page_num + 1,
                # 필요 시 실제 이미지 추출:
                # base_image = page_fitz.extract_image(xref)
                # image_bytes = base_image["image"]
            })

        return images

    def _extract_document_metadata(self, doc_fitz) -> Dict:
        """문서 전체 메타데이터 추출"""
        metadata = doc_fitz.metadata
        return {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "creator": metadata.get("creator", ""),
            "producer": metadata.get("producer", ""),
            "creation_date": metadata.get("creationDate", ""),
            "modification_date": metadata.get("modDate", ""),
        }

    def _detect_language(self, pages: List[PDFPage]) -> str:
        """
        문서 언어 감지

        처음 3페이지의 텍스트를 샘플링하여 언어 감지
        """
        sample_text = ""
        for page in pages[:3]:
            sample_text += page.text[:500]  # 페이지당 500자

        if not sample_text.strip():
            return "unknown"

        try:
            lang_code = detect(sample_text)
            # ISO 639-1 코드를 이름으로 변환
            lang_map = {
                "ko": "korean",
                "en": "english",
                "ja": "japanese",
                "zh-cn": "chinese",
            }
            return lang_map.get(lang_code, lang_code)
        except Exception as e:
            print(f"⚠️  Language detection failed: {e}")
            return "unknown"

    def _clean_text(self, text: str) -> str:
        """
        텍스트 정제

        - 과도한 공백 제거
        - 특수 문자 정리
        - 하이픈으로 끝나는 단어 연결
        """
        if not text:
            return ""

        # 여러 개의 공백을 하나로
        text = re.sub(r' +', ' ', text)

        # 여러 개의 줄바꿈을 최대 2개로
        text = re.sub(r'\n{3,}', '\n\n', text)

        # 하이픈으로 끝나는 단어 연결 (영어)
        text = re.sub(r'-\n(\w)', r'\1', text)

        # 앞뒤 공백 제거
        text = text.strip()

        return text

    def extract_text_by_page_range(
        self,
        pdf_path: str,
        start_page: int,
        end_page: int
    ) -> str:
        """
        특정 페이지 범위의 텍스트만 추출

        Args:
            pdf_path: PDF 파일 경로
            start_page: 시작 페이지 (1부터 시작)
            end_page: 끝 페이지 (포함)

        Returns:
            추출된 텍스트
        """
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page_num in range(start_page - 1, end_page):
                if page_num < len(pdf.pages):
                    page_text = pdf.pages[page_num].extract_text()
                    text += f"\n--- Page {page_num + 1} ---\n"
                    text += self._clean_text(page_text)
            return text

    def get_page_count(self, pdf_path: str) -> int:
        """PDF 페이지 수 반환"""
        doc = fitz.open(pdf_path)
        count = len(doc)
        doc.close()
        return count

    def extract_toc(self, pdf_path: str) -> List[Tuple[int, str, int]]:
        """
        목차(Table of Contents) 추출

        Returns:
            List of (level, title, page_number)
        """
        doc = fitz.open(pdf_path)
        toc = doc.get_toc()
        doc.close()
        return toc


# 유틸리티 함수
def parse_pdf_quick(pdf_path: str) -> str:
    """
    빠른 텍스트 추출 (메타데이터 없이)

    테스트나 간단한 용도로 사용
    """
    parser = PDFParser(preserve_layout=False)
    doc = parser.parse(pdf_path, extract_images=False)

    full_text = ""
    for page in doc.pages:
        full_text += f"\n--- Page {page.page_number} ---\n"
        full_text += page.text

    return full_text


def extract_tables_from_pdf(pdf_path: str) -> Dict[int, List]:
    """
    PDF에서 모든 표 추출

    Returns:
        {page_number: [table1, table2, ...]}
    """
    parser = PDFParser()
    doc = parser.parse(pdf_path, extract_images=False)

    tables_by_page = {}
    for page in doc.pages:
        if page.tables:
            tables_by_page[page.page_number] = page.tables

    return tables_by_page


if __name__ == "__main__":
    # 테스트 코드
    import sys

    if len(sys.argv) < 2:
        print("Usage: python pdf_parser.py <pdf_file>")
        sys.exit(1)

    pdf_file = sys.argv[1]

    # 파싱 테스트
    parser = PDFParser(preserve_layout=True)
    document = parser.parse(pdf_file, extract_images=True)

    print(f"\n📊 Document Info:")
    print(f"  - File: {document.file_path}")
    print(f"  - Pages: {document.total_pages}")
    print(f"  - Language: {document.language}")
    print(f"  - Title: {document.metadata.get('title', 'N/A')}")

    print(f"\n📄 First Page Preview:")
    print(document.pages[0].text[:500])

    # 표 통계
    table_count = sum(len(page.tables) for page in document.pages)
    print(f"\n📊 Tables found: {table_count}")

    # 이미지 통계
    image_count = sum(len(page.images) for page in document.pages)
    print(f"🖼️  Images found: {image_count}")
