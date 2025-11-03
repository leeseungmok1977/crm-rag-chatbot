"""
메타데이터 추출 모듈
- 파일명에서 문서 정보 추출
- 문서 타입, 언어, 버전 자동 감지
"""

import re
from pathlib import Path
from typing import Dict, Optional, Literal
from dataclasses import dataclass


@dataclass
class DocumentMetadata:
    """문서 메타데이터"""
    document_id: str
    type: str  # account_contact, meeting_memo, order_fulfillment, common_master
    language: str  # korean, english
    version: str
    source_file: str
    file_size: int
    keywords: list[str]


class MetadataExtractor:
    """
    CRM 매뉴얼 파일명에서 메타데이터 추출

    파일명 패턴:
    - P_INTL_CRM 매뉴얼(국문)_거래선&연락처.pdf
    - P_INTL_CRM Guide Book(ENG)_Account&Contact.pdf
    """

    # 문서 타입 매핑
    TYPE_MAPPING = {
        # 한국어
        "거래선": "account_contact",
        "연락처": "account_contact",
        "미팅메모": "meeting_memo",
        "회의": "meeting_memo",
        "order": "order_fulfillment",
        "fulfillment": "order_fulfillment",
        "주문": "order_fulfillment",
        "발주": "order_fulfillment",
        "공통": "common_master",
        "master": "common_master",
        "마스터": "common_master",

        # 영어
        "account": "account_contact",
        "contact": "account_contact",
        "meeting": "meeting_memo",
        "memo": "meeting_memo",
    }

    # 키워드 매핑
    KEYWORDS_MAPPING = {
        "account_contact": [
            "거래선", "고객", "연락처", "담당자", "Account", "Contact", "Customer"
        ],
        "meeting_memo": [
            "미팅", "회의", "메모", "일지", "Meeting", "Memo", "Minutes"
        ],
        "order_fulfillment": [
            "주문", "발주", "계약", "이행", "Order", "Fulfillment", "Contract"
        ],
        "common_master": [
            "공통", "설정", "권한", "마스터", "Common", "Master", "Settings"
        ],
    }

    def extract_from_filename(self, file_path: str) -> DocumentMetadata:
        """
        파일명에서 메타데이터 추출

        Args:
            file_path: PDF 파일 경로

        Returns:
            DocumentMetadata 객체
        """
        path = Path(file_path)
        filename = path.stem  # 확장자 제외
        file_size = path.stat().st_size if path.exists() else 0

        # 언어 감지
        language = self._detect_language_from_filename(filename)

        # 문서 타입 감지
        doc_type = self._detect_type_from_filename(filename)

        # 버전 감지 (파일명 또는 기본값)
        version = self._detect_version(filename)

        # Document ID 생성
        document_id = self._generate_document_id(doc_type, language, version)

        # 키워드 추출
        keywords = self.KEYWORDS_MAPPING.get(doc_type, [])

        metadata = DocumentMetadata(
            document_id=document_id,
            type=doc_type,
            language=language,
            version=version,
            source_file=path.name,
            file_size=file_size,
            keywords=keywords
        )

        return metadata

    def _detect_language_from_filename(self, filename: str) -> str:
        """파일명에서 언어 감지"""
        filename_lower = filename.lower()

        if any(keyword in filename_lower for keyword in ["국문", "(ko)", "korean"]):
            return "korean"
        elif any(keyword in filename_lower for keyword in ["eng", "english", "(en)"]):
            return "english"
        elif any(keyword in filename for keyword in ["일본", "japanese", "(jp)"]):
            return "japanese"
        elif any(keyword in filename for keyword in ["중국", "chinese", "(cn)"]):
            return "chinese"

        # 한글 포함 여부로 판단
        if re.search(r'[가-힣]', filename):
            return "korean"
        else:
            return "english"

    def _detect_type_from_filename(self, filename: str) -> str:
        """파일명에서 문서 타입 감지"""
        filename_lower = filename.lower()

        # 각 키워드로 매칭
        for keyword, doc_type in self.TYPE_MAPPING.items():
            if keyword.lower() in filename_lower:
                return doc_type

        # 기본값
        return "common_master"

    def _detect_version(self, filename: str) -> str:
        """버전 감지 (예: v1.0, v2.1)"""
        # 버전 패턴 찾기
        version_patterns = [
            r'v(\d+\.\d+)',
            r'ver(\d+\.\d+)',
            r'version(\d+\.\d+)',
            r'_(\d+\.\d+)',
        ]

        for pattern in version_patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                return match.group(1)

        # 기본 버전
        return "1.0"

    def _generate_document_id(
        self,
        doc_type: str,
        language: str,
        version: str
    ) -> str:
        """Document ID 생성"""
        # 언어 코드
        lang_code = {
            "korean": "ko",
            "english": "en",
            "japanese": "jp",
            "chinese": "cn"
        }.get(language, "en")

        # 타입 약자
        type_code = {
            "account_contact": "account",
            "meeting_memo": "meeting",
            "order_fulfillment": "order",
            "common_master": "common"
        }.get(doc_type, "doc")

        # 버전 (점 제거)
        version_code = version.replace(".", "_")

        return f"crm_{type_code}_{lang_code}_v{version_code}"

    def extract_from_content(
        self,
        text: str,
        existing_metadata: Optional[DocumentMetadata] = None
    ) -> Dict:
        """
        문서 내용에서 추가 메타데이터 추출

        Args:
            text: 문서 텍스트
            existing_metadata: 기존 메타데이터 (있으면 업데이트)

        Returns:
            추가 메타데이터 딕셔너리
        """
        additional_metadata = {}

        # 섹션 제목 추출
        sections = self._extract_sections(text)
        if sections:
            additional_metadata["sections"] = sections
            additional_metadata["section_count"] = len(sections)

        # 키워드 빈도 분석
        if existing_metadata:
            keyword_freq = self._count_keywords(text, existing_metadata.keywords)
            additional_metadata["keyword_frequency"] = keyword_freq

        # 문서 길이 정보
        additional_metadata["char_count"] = len(text)
        additional_metadata["word_count"] = len(text.split())
        additional_metadata["line_count"] = len(text.split('\n'))

        return additional_metadata

    def _extract_sections(self, text: str) -> list[str]:
        """문서에서 섹션 제목 추출"""
        sections = []

        # 섹션 패턴
        patterns = [
            r'^#{1,6}\s+(.+)$',  # Markdown
            r'^(\d+\.\s+.+)$',   # 1. 제목
            r'^(\d+\.\d+\s+.+)$',  # 1.1 제목
            r'^제(\d+)장\s+(.+)$',  # 제1장
        ]

        for line in text.split('\n'):
            line = line.strip()
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    sections.append(line)
                    break

        return sections[:50]  # 최대 50개

    def _count_keywords(self, text: str, keywords: list[str]) -> Dict[str, int]:
        """키워드 빈도 계산"""
        text_lower = text.lower()
        keyword_freq = {}

        for keyword in keywords:
            count = text_lower.count(keyword.lower())
            if count > 0:
                keyword_freq[keyword] = count

        return keyword_freq


# 유틸리티 함수
def extract_metadata_from_pdf_folder(folder_path: str) -> list[DocumentMetadata]:
    """
    폴더 내 모든 PDF의 메타데이터 추출

    Args:
        folder_path: PDF 폴더 경로

    Returns:
        메타데이터 리스트
    """
    extractor = MetadataExtractor()
    folder = Path(folder_path)

    pdf_files = list(folder.glob("**/*.pdf"))
    metadata_list = []

    print(f"📁 Extracting metadata from {len(pdf_files)} PDF files...")

    for pdf_file in pdf_files:
        try:
            metadata = extractor.extract_from_filename(str(pdf_file))
            metadata_list.append(metadata)
            print(f"  ✅ {pdf_file.name}")
            print(f"     - Type: {metadata.type}")
            print(f"     - Language: {metadata.language}")
            print(f"     - ID: {metadata.document_id}")
        except Exception as e:
            print(f"  ❌ {pdf_file.name}: {e}")

    return metadata_list


def get_document_type_display_name(doc_type: str, language: str = "korean") -> str:
    """
    문서 타입의 표시 이름 반환

    Args:
        doc_type: 문서 타입 (account_contact 등)
        language: 언어

    Returns:
        표시 이름
    """
    names = {
        "account_contact": {
            "korean": "거래선 & 연락처",
            "english": "Account & Contact"
        },
        "meeting_memo": {
            "korean": "미팅메모",
            "english": "Meeting Memo"
        },
        "order_fulfillment": {
            "korean": "주문 & 이행",
            "english": "Order & Fulfillment"
        },
        "common_master": {
            "korean": "공통 & Master",
            "english": "Common & Master"
        }
    }

    return names.get(doc_type, {}).get(language, doc_type)


if __name__ == "__main__":
    # 테스트 코드
    import sys

    extractor = MetadataExtractor()

    # 테스트 파일명들
    test_filenames = [
        "P_INTL_CRM 매뉴얼(국문)_거래선&연락처.pdf",
        "P_INTL_CRM Guide Book(ENG)_Account&Contact.pdf",
        "P_INTL_CRM 매뉴얼(국문)_미팅메모.pdf",
        "P_INTL_CRM Guide Book(ENG)_Meeting Memo.pdf",
        "P_INTL_CRM 매뉴얼(국문)_Order&Fulfillment.pdf",
        "P_INTL_CRM Guide Book(ENG)_Order&Fulfillment.pdf",
        "P_INTL_CRM 매뉴얼(국문)_공통&Master.pdf",
        "P_INTL_CRM Guide Book(ENG)_Common&Master.pdf",
    ]

    print("=== Metadata Extraction Test ===\n")

    for filename in test_filenames:
        print(f"📄 {filename}")
        metadata = extractor.extract_from_filename(filename)
        print(f"   Document ID: {metadata.document_id}")
        print(f"   Type: {metadata.type}")
        print(f"   Language: {metadata.language}")
        print(f"   Version: {metadata.version}")
        print(f"   Keywords: {', '.join(metadata.keywords[:3])}...")
        print()

    # 폴더 테스트 (인자가 있으면)
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
        print(f"\n=== Extracting from folder: {folder_path} ===\n")
        metadata_list = extract_metadata_from_pdf_folder(folder_path)
        print(f"\n✅ Total: {len(metadata_list)} documents")
