"""
Prompt Templates for RAG Answer Generation
"""

SYSTEM_PROMPT_KOREAN = """당신은 POSCO International의 CRM 시스템 전문가입니다.
사용자의 질문에 대해 제공된 매뉴얼 내용을 바탕으로 정확하고 친절하게 답변해주세요.

답변 스타일 가이드:
1. **핵심 답변 먼저**: 질문에 대한 직접적인 답변을 첫 줄에 제시하세요
2. **이모지 활용**: 적절한 이모지로 가독성을 높이세요 (✅, 📋, 💡, ⚠️, 1️⃣, 2️⃣ 등)
3. **단계별 구조화**: 프로세스는 1️⃣, 2️⃣, 3️⃣ 형식으로 명확하게 구분하세요
4. **표 형식**: 비교나 요약이 필요한 경우 마크다운 표를 활용하세요
5. **강조 포인트**: 💡 팁, ⚠️ 주의사항, 📌 요약 등으로 중요 정보를 강조하세요
6. **친근한 어조**: "~입니다", "~해주세요" 보다는 "~이에요", "~하면 됩니다" 같은 친근한 표현 사용
7. **근거 기반**: 제공된 문서 내용만을 기반으로 답변하며, 추측하지 마세요

답변 구조 예시:
[질문에 대한 핵심 답변을 1-2줄로 먼저 제시] ✅

🔍 상세 절차

1️⃣ 첫 번째 단계
- 세부 설명
- 추가 정보

2️⃣ 두 번째 단계
- 세부 설명
- 추가 정보

💡 Tip
- 유용한 팁이나 추가 정보

⚠️ 주의사항
- 중요하게 알아야 할 포인트
- 실수하기 쉬운 부분

📌 요약
| 항목 | 설명 |
|------|------|
| ... | ... |
"""

SYSTEM_PROMPT_ENGLISH = """You are a CRM system expert for POSCO International.
Please provide accurate and helpful answers to user questions based on the provided manual content.

Answer Style Guide:
1. **Core Answer First**: Present the direct answer in the first 1-2 lines
2. **Use Emojis**: Enhance readability with appropriate emojis (✅, 📋, 💡, ⚠️, 1️⃣, 2️⃣, etc.)
3. **Step-by-Step Structure**: Use 1️⃣, 2️⃣, 3️⃣ format for clear process steps
4. **Table Format**: Use markdown tables for comparisons or summaries
5. **Highlight Points**: Emphasize with 💡 Tips, ⚠️ Cautions, 📌 Summary
6. **Friendly Tone**: Use conversational language that's easy to understand
7. **Evidence-Based**: Base answers only on provided documents; don't speculate

Answer Structure Example:
[Present core answer in 1-2 lines first] ✅

🔍 Detailed Steps

1️⃣ First Step
- Details
- Additional info

2️⃣ Second Step
- Details
- Additional info

💡 Tip
- Useful tips or additional information

⚠️ Important Notes
- Key points to remember
- Common mistakes to avoid

📌 Summary
| Item | Description |
|------|-------------|
| ... | ... |
"""

USER_PROMPT_TEMPLATE_KOREAN = """사용자 질문: {query}

관련 문서 내용:
{context}

위 문서 내용을 바탕으로 사용자의 질문에 답변해주세요.
답변은 명확하고 구체적으로 작성하며, 필요한 경우 예시를 포함해주세요.
"""

USER_PROMPT_TEMPLATE_ENGLISH = """User Question: {query}

Relevant Document Content:
{context}

Based on the above document content, please answer the user's question.
Provide a clear and specific answer, including examples if necessary.
"""

CONTEXT_TEMPLATE_KOREAN = """
[문서 {idx}]
출처: {source}
내용:
{text}
---
"""

CONTEXT_TEMPLATE_ENGLISH = """
[Document {idx}]
Source: {source}
Content:
{text}
---
"""


def get_system_prompt(language: str) -> str:
    """
    Get system prompt for given language

    Args:
        language: "korean" or "english"

    Returns:
        System prompt
    """
    return SYSTEM_PROMPT_KOREAN if language == "korean" else SYSTEM_PROMPT_ENGLISH


def get_user_prompt_template(language: str) -> str:
    """
    Get user prompt template for given language

    Args:
        language: "korean" or "english"

    Returns:
        User prompt template
    """
    return USER_PROMPT_TEMPLATE_KOREAN if language == "korean" else USER_PROMPT_TEMPLATE_ENGLISH


def get_context_template(language: str) -> str:
    """
    Get context template for given language

    Args:
        language: "korean" or "english"

    Returns:
        Context template
    """
    return CONTEXT_TEMPLATE_KOREAN if language == "korean" else CONTEXT_TEMPLATE_ENGLISH


def format_context(search_results: list, language: str) -> str:
    """
    Format search results into context string

    Args:
        search_results: List of SearchResult objects
        language: "korean" or "english"

    Returns:
        Formatted context string
    """
    template = get_context_template(language)
    context_parts = []

    for idx, result in enumerate(search_results, 1):
        # Extract source information
        doc_id = result.metadata.get("document_id", "Unknown")
        doc_type = result.metadata.get("type", "Unknown")

        context = template.format(
            idx=idx,
            score=result.score,
            source=f"{doc_type} - {doc_id}",
            text=result.text
        )
        context_parts.append(context)

    return "\n".join(context_parts)


def build_prompt(query: str, search_results: list, language: str) -> dict:
    """
    Build complete prompt for LLM

    Args:
        query: User query
        search_results: List of SearchResult objects
        language: "korean" or "english"

    Returns:
        Dictionary with system and user prompts
    """
    system_prompt = get_system_prompt(language)
    user_template = get_user_prompt_template(language)

    # Format context from search results
    context = format_context(search_results, language)

    # Build user prompt
    user_prompt = user_template.format(query=query, context=context)

    return {
        "system": system_prompt,
        "user": user_prompt
    }
