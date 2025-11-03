"""
설치 및 설정 테스트 스크립트
"""

import sys
from pathlib import Path

print("=" * 60)
print("🧪 CRM RAG Chatbot - Setup Test")
print("=" * 60)

# 1. Python 버전 확인
print(f"\n✓ Python Version: {sys.version}")

# 2. 필수 패키지 확인
print("\n📦 Checking packages...")
packages = {
    "python-dotenv": "dotenv",
    "pydantic": "pydantic",
    "pypdf": "pypdf",
    "pdfplumber": "pdfplumber",
    "langdetect": "langdetect",
    "openai": "openai",
    "langchain": "langchain",
    "langchain-openai": "langchain_openai",
    "qdrant-client": "qdrant_client",
    "tqdm": "tqdm",
}

missing = []
for name, module in packages.items():
    try:
        __import__(module)
        print(f"  ✓ {name}")
    except ImportError:
        print(f"  ✗ {name} - NOT FOUND")
        missing.append(name)

if missing:
    print(f"\n❌ Missing packages: {', '.join(missing)}")
    print("Run: pip install " + " ".join(missing))
    sys.exit(1)

# 3. 환경 변수 확인
print("\n🔑 Checking environment variables...")
try:
    from dotenv import load_dotenv
    import os

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    if api_key:
        print(f"  ✓ OPENAI_API_KEY: {api_key[:10]}...{api_key[-4:]}")
    else:
        print("  ⚠️  OPENAI_API_KEY not found in .env")
        print("     Please create .env file and add your API key")
except Exception as e:
    print(f"  ✗ Error: {e}")

# 4. 프로젝트 구조 확인
print("\n📁 Checking project structure...")
required_paths = [
    "src/utils/pdf_parser.py",
    "src/utils/chunker.py",
    "src/utils/metadata_extractor.py",
    "src/services/embedding_service.py",
    "src/services/vector_store.py",
    "src/core/pipeline.py",
    "src/core/config.py",
    "scripts/process_documents.py",
]

for path in required_paths:
    if Path(path).exists():
        print(f"  ✓ {path}")
    else:
        print(f"  ✗ {path} - NOT FOUND")

# 5. 디렉토리 확인
print("\n📂 Checking directories...")
required_dirs = ["data/processed", "data/embeddings", "logs", "PDF"]
for dir_path in required_dirs:
    dir_obj = Path(dir_path)
    if dir_obj.exists():
        print(f"  ✓ {dir_path}/")
    else:
        print(f"  ⚠️  {dir_path}/ - Creating...")
        dir_obj.mkdir(parents=True, exist_ok=True)

# 6. PDF 파일 확인
print("\n📄 Checking PDF files...")
pdf_dir = Path("PDF")
if pdf_dir.exists():
    pdf_files = list(pdf_dir.glob("*.pdf"))
    if pdf_files:
        print(f"  ✓ Found {len(pdf_files)} PDF files:")
        for pdf in pdf_files[:3]:  # 처음 3개만 표시
            size_mb = pdf.stat().st_size / (1024 * 1024)
            print(f"    - {pdf.name} ({size_mb:.1f} MB)")
        if len(pdf_files) > 3:
            print(f"    ... and {len(pdf_files) - 3} more")
    else:
        print("  ⚠️  No PDF files found in PDF/ directory")
        print("     Please place CRM manual PDFs in the PDF/ folder")
else:
    print("  ✗ PDF/ directory not found")

# 7. 간단한 기능 테스트
print("\n🧪 Testing basic functionality...")

# PDF 파서 테스트
try:
    from src.utils.pdf_parser import PDFParser
    parser = PDFParser()
    print("  ✓ PDF Parser imported")
except Exception as e:
    print(f"  ✗ PDF Parser error: {e}")

# 청커 테스트
try:
    from src.utils.chunker import DocumentChunker
    chunker = DocumentChunker()
    test_text = "테스트 텍스트입니다. " * 100
    chunks = chunker.chunk_document(
        test_text,
        {"document_id": "test"},
        strategy="recursive"
    )
    print(f"  ✓ Chunker works ({len(chunks)} chunks created)")
except Exception as e:
    print(f"  ✗ Chunker error: {e}")

# 메타데이터 추출기 테스트
try:
    from src.utils.metadata_extractor import MetadataExtractor
    extractor = MetadataExtractor()
    metadata = extractor.extract_from_filename(
        "P_INTL_CRM 매뉴얼(국문)_거래선&연락처.pdf"
    )
    print(f"  ✓ Metadata Extractor works (type: {metadata.type})")
except Exception as e:
    print(f"  ✗ Metadata Extractor error: {e}")

print("\n" + "=" * 60)
print("✅ Setup test completed!")
print("=" * 60)

# 다음 단계 안내
print("\n📖 Next Steps:")
print("1. Ensure .env file has your OPENAI_API_KEY")
print("2. Place PDF files in PDF/ directory")
print("3. Start Qdrant: docker run -p 6333:6333 qdrant/qdrant")
print("4. Process documents: python scripts/process_documents.py PDF/")
print("\nFor more info, see: README.md or QUICKSTART.md")
