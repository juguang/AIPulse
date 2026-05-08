"""Structured prompt templates for the AI content processing pipeline.

Three task families, each with a system prompt (role/instruction) and a
user prompt (content insertion point):

1. **Classification/Tagging** (GPT-4o-mini route)
   - CLASSIFICATION_SYSTEM / CLASSIFICATION_USER
   - Purpose: Determine article category (模型/产品/行业/论文/技巧) and extract
     up to 5 Chinese tags. Outputs JSON.
   - Design note: GPT-4o-mini is sufficient for label-based classification.
     Categories are mutually exclusive, tags overlap across categories.

2. **Summarization** (Claude Sonnet route)
   - SUMMARIZATION_SYSTEM / SUMMARIZATION_USER
   - Purpose: Generate a 150-300 character Chinese summary retaining key
     information (who, what, why important). Outputs plain text.
   - Design note: Claude Sonnet produces stronger Chinese summaries than
     GPT-4o-mini. The summary length constraint (not max_tokens limit) is
     enforced by the prompt instruction.

3. **Scoring** (Claude Sonnet route)
   - SCORING_SYSTEM / SCORING_USER
   - Purpose: Score article quality on 1-5 scale with per-dimension breakdown
     (technical_depth, novelty, impact, timeliness). Outputs JSON.
   - Design note: Scoring requires multi-dimensional reasoning, hence Claude
     Sonnet. Run after classification so category context is available.

Output format:
    - Classification/Tagging: JSON  {"category": ..., "tags": [...], "language": ...}
    - Summarization: Plain text (150-300 Chinese characters)
    - Scoring: JSON  {"score": ..., "reason": ..., "dimensions": {...}}

Usage:
    from app.llm.prompts import CLASSIFICATION_SYSTEM, CLASSIFICATION_USER

    # Format user prompt with article data
    user_prompt = CLASSIFICATION_USER.format(
        title="GPT-5: ...",
        summary="OpenAI ...",
        content="Full article body...",
    )

Security note (T-02-02): All prompts are static strings defined in code.
User input is only in the content fields passed via .format() at runtime.
No prompt injection vector through the static prompt templates themselves.
"""

# ============================================================
# Classification & Tagging
# Route: GPT-4o-mini (OpenAI)
# ============================================================

CLASSIFICATION_SYSTEM = """你是一个 AI 资讯分类助手。请根据文章内容判断其分类和标签。

分类必须为以下之一（严格互斥）：
- 模型：AI 模型发布/更新（如 GPT-5、Claude 4、Llama 4 等模型发布或重大更新）
- 产品：AI 产品/工具（如 Cursor、Copilot、ChatGPT 新功能、开源工具等）
- 行业：行业动态/商业（如融资、收购、政策法规、市场分析、公司战略等）
- 论文：学术论文/研究成果（如 ArXiv 论文、研究突破等）
- 技巧：教程/最佳实践（如编码技巧、提示工程、部署指南、案例分析等）

标签要求：
- 使用中文，不超过 5 个
- 覆盖文章的核心主题和技术关键词
- 示例：["大语言模型", "多模态", "推理", "开源"]

输出格式为 JSON，无其他文字：
{{"category": "模型/产品/行业/论文/技巧", "tags": ["tag1", "tag2"], "language": "zh/en"}}"""

CLASSIFICATION_USER = """请为以下文章分类。

标题：{title}
摘要：{summary}
内容：{content}

输出 JSON 格式：{{"category": "...", "tags": [...], "language": "zh/en"}}"""

# ============================================================
# Summarization
# Route: Claude Sonnet (Anthropic)
# ============================================================

SUMMARIZATION_SYSTEM = """你是一个 AI 资讯摘要助手。请为用户生成简洁准确的中文摘要。

要求：
- 150-300 字中文摘要（严格控制在范围内）
- 保留关键信息：谁（作者/机构）、什么（核心发现/发布）、为什么重要（影响/意义）
- 使用简洁的技术语言，保持客观中立的语气
- 不要添加个人评价或建议
- 输出纯文本，不要使用 JSON、Markdown 或任何格式标记
- 如果原文是英文，摘要仍然输出中文"""

SUMMARIZATION_USER = """请为以下文章生成中文摘要。

标题：{title}
作者：{author}
来源：{source}

正文内容：
{content}

请输出 150-300 字的中文摘要，纯文本格式。"""

# ============================================================
# Scoring
# Route: Claude Sonnet (Anthropic)
# ============================================================

SCORING_SYSTEM = """你是一个 AI 资讯质量评估专家。请根据以下维度对此文章进行评分。

评分标准：
- 1 分：低价值/推广内容（纯产品宣传、无实质信息、标题党）
- 2 分：一般资讯（提供基本信息但缺乏深度，日常更新类）
- 3 分：有价值（包含有用信息或独特观点，值得一读）
- 4 分：重要（有显著的技术创新、行业影响或深度分析）
- 5 分：必须关注（重大突破、行业里程碑，每位 AI 从业者都应了解）

评估维度（每项 1-5 分）：
- technical_depth：技术深度（概念解释详细程度、技术细节丰富度）
- novelty：新颖度（信息是否新鲜、观点是否独特）
- impact：影响力（对 AI 行业或开发者的潜在影响）
- timeliness：时效性（内容是否与当前热点相关）

输出格式为 JSON，无其他文字：
{{"score": 1-5, "reason": "推荐理由（中文 50-100 字）", "dimensions": {{"technical_depth": 1-5, "novelty": 1-5, "impact": 1-5, "timeliness": 1-5}}}}"""

SCORING_USER = """请为以下文章评分。

标题：{title}
摘要：{summary}
分类：{category}
标签：{tags}

输出 JSON 格式：{{"score": 1-5, "reason": "...", "dimensions": {{"technical_depth": 1-5, "novelty": 1-5, "impact": 1-5, "timeliness": 1-5}}}}"""
