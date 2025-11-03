"""
인기 질문 통계 업데이트 스크립트
매일 자정에 실행하여 질문 통계를 정리합니다.
"""

import json
from pathlib import Path
from collections import Counter
from datetime import datetime, timedelta


def update_popular_queries():
    """Update popular queries statistics"""
    history_file = Path("data/query_history.json")

    if not history_file.exists():
        print("❌ No query history found")
        return

    try:
        # Load history
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)

        queries = history.get('queries', [])
        timestamps = history.get('timestamps', [])

        if not queries:
            print("📊 No queries to process")
            return

        # Count frequencies
        query_counts = Counter(queries)

        # Get top 10
        top_queries = query_counts.most_common(10)

        # Save statistics
        stats_file = Path("data/query_stats.json")
        stats = {
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_queries': len(queries),
            'unique_queries': len(query_counts),
            'top_queries': [
                {'query': query, 'count': count}
                for query, count in top_queries
            ]
        }

        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)

        print(f"✅ Updated query statistics")
        print(f"📊 Total queries: {len(queries)}")
        print(f"📊 Unique queries: {len(query_counts)}")
        print(f"\n🏆 Top 5 popular queries:")
        for idx, (query, count) in enumerate(top_queries[:5], 1):
            print(f"  {idx}. {query} ({count}회)")

        # Optional: Clean old history (keep last 30 days)
        cutoff_date = datetime.now() - timedelta(days=30)

        filtered_queries = []
        filtered_timestamps = []

        for query, timestamp in zip(queries, timestamps):
            try:
                query_date = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                if query_date >= cutoff_date:
                    filtered_queries.append(query)
                    filtered_timestamps.append(timestamp)
            except:
                # Keep if can't parse
                filtered_queries.append(query)
                filtered_timestamps.append(timestamp)

        # Update history file
        history['queries'] = filtered_queries
        history['timestamps'] = filtered_timestamps

        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

        removed_count = len(queries) - len(filtered_queries)
        if removed_count > 0:
            print(f"\n🧹 Cleaned {removed_count} old queries (>30 days)")

    except Exception as e:
        print(f"❌ Error updating statistics: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("📊 Query Statistics Update")
    print("=" * 60)
    update_popular_queries()
    print("=" * 60)
