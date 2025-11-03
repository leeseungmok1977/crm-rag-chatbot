"""
문서 처리 실행 스크립트
- CLI를 통한 문서 처리
- PDF 폴더 전체 처리
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from src.core.config import get_settings
from src.core.pipeline import create_pipeline


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="CRM Manual Document Processing Pipeline"
    )

    parser.add_argument(
        "input_path",
        type=str,
        help="PDF file or folder path"
    )

    parser.add_argument(
        "--strategy",
        type=str,
        default="recursive",
        choices=["fixed", "recursive", "semantic", "token"],
        help="Chunking strategy (default: recursive)"
    )

    parser.add_argument(
        "--recreate-collections",
        action="store_true",
        help="Recreate vector collections (delete existing data)"
    )

    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable embedding cache"
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Batch size for embedding (default: 100)"
    )

    args = parser.parse_args()

    # Load environment variables
    load_dotenv()
    settings = get_settings()

    print("=" * 60)
    print("🚀 CRM Document Processing Pipeline")
    print("=" * 60)
    print(f"Input: {args.input_path}")
    print(f"Strategy: {args.strategy}")
    print(f"Recreate Collections: {args.recreate_collections}")
    print(f"Cache: {'Disabled' if args.no_cache else 'Enabled'}")
    print(f"Batch Size: {args.batch_size}")
    print("=" * 60)

    # Check input path
    input_path = Path(args.input_path)
    if not input_path.exists():
        print(f"❌ Error: Path not found: {args.input_path}")
        sys.exit(1)

    try:
        # Create pipeline (use_memory=True to skip Qdrant connection attempt)
        pipeline = create_pipeline(
            openai_api_key=settings.openai_api_key,
            qdrant_host=settings.qdrant_host,
            qdrant_port=settings.qdrant_port,
            vector_size=settings.embedding_dimension,
            use_memory=True  # Use in-memory mode when Docker is not available
        )

        # Override cache setting
        if args.no_cache:
            pipeline.embedding_service.cache_enabled = False

        # Recreate collections if requested
        if args.recreate_collections:
            print("\n⚠️  Recreating collections (existing data will be deleted)...")
            pipeline.vector_store.initialize_crm_collections(
                vector_size=settings.embedding_dimension,
                recreate=True
            )

        # Process
        if input_path.is_file():
            # Single file
            stats = pipeline.process_document(
                pdf_path=str(input_path),
                chunking_strategy=args.strategy,
                save_intermediate=True
            )
            print("\n✅ Processing completed!")
            print(f"   - Document ID: {stats['document_id']}")
            print(f"   - Chunks: {stats['total_chunks']}")
            print(f"   - Time: {stats['processing_time_seconds']}s")

        elif input_path.is_dir():
            # Folder
            stats_list = pipeline.process_folder(
                folder_path=str(input_path),
                chunking_strategy=args.strategy,
                file_pattern="*.pdf"
            )
            print("\n✅ All processing completed!")

        else:
            print(f"❌ Error: Invalid path type: {args.input_path}")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
