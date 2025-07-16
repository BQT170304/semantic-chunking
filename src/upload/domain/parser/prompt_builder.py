from __future__ import annotations


def build_markdown_prompt(raw_text: str) -> str:
    return f"""
You are a professional technical writer.

Rewrite the following content as a structured Markdown document with:
- Logical headings (#, ##, etc.)
- Bullet points where applicable
- Clean and easy-to-read format

--- RAW CONTENT START ---
{raw_text}
--- RAW CONTENT END ---
"""
