from __future__ import annotations


def build_markdown_prompt(raw_text: str) -> str:
    # Detect language first
    has_vietnamese = any(ord(char) > 127 for char in raw_text if char.isalpha())

    if has_vietnamese:
        return f"""
NHIỆM VỤ: Bạn là một người viết kỹ thuật chuyên nghiệp. Định dạng nội dung sau thành Markdown.

QUY TẮC TUYỆT ĐỐI:
- GIỮ NGUYÊN 100% nội dung tiếng Việt
- KHÔNG dịch sang tiếng Anh
- KHÔNG thay đổi từ ngữ
- CHỈ thêm ký hiệu Markdown (#, -, *, etc.)

YÊU CẦU ĐỊNH DẠNG:
- Dùng heading (#, ##, ###) để tạo cấu trúc
- Dùng bullet points cho danh sách
- Giữ nguyên tất cả thuật ngữ kỹ thuật
- Sử dụng cú pháp Markdown chuẩn

CẢNH BÁO: Tuyệt đối KHÔNG được dịch hoặc thay đổi nội dung!

--- NỘI DUNG GỐC ---
{raw_text}
--- KẾT THÚC NỘI DUNG ---

HÃY XUẤT RA NỘI DUNG TIẾNG VIỆT VỚI ĐỊNH DẠNG MARKDOWN.
"""
    else:
        return f"""
You are a professional technical writer and document formatter.

Your task is to rewrite the following content as a structured Markdown document with the following requirements:

FORMATTING REQUIREMENTS:
- Use logical headings (#, ##, ###, etc.) to create hierarchy
- Add bullet points where applicable for lists
- Create clean and easy-to-read format
- Use proper Markdown syntax

CRITICAL CONTENT PRESERVATION RULES:
- **ABSOLUTELY MANDATORY**: KEEP THE EXACT SAME LANGUAGE as the input content
- **ZERO TRANSLATION ALLOWED**: Do not translate any word or phrase
- **ZERO PARAPHRASING ALLOWED**: Use the exact same words and phrases
- **ZERO CONTENT MODIFICATION**: Do not change, add, or remove any information
- **PRESERVE ALL**: Technical terms, names, numbers, dates, and specific details exactly as written
- **FORMATTING ONLY**: Your job is ONLY to add Markdown structure, nothing else

--- RAW CONTENT START ---
{raw_text}
--- RAW CONTENT END ---

REMINDER: Output the content in the EXACT SAME LANGUAGE as the input with ONLY Markdown formatting added.
"""
