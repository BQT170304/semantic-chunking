from __future__ import annotations


def build_markdown_prompt(raw_text: str) -> str:
    has_vietnamese = any(ord(char) > 127 for char in raw_text if char.isalpha())
    if has_vietnamese:
        return f"""
        <ROLE>
        Bạn là chuyên gia phân tích cấu trúc tài liệu. Bạn có khả năng xác định tiêu đề các mục (header) dựa trên cách diễn đạt, kiểu đánh số, hoặc các dấu hiệu định dạng.
        </ROLE>

        <TASK>
        Từ nội dung tài liệu được cung cấp (có thể là văn bản thuần được trích xuất từ một tài liệu có cấu trúc), hãy trích xuất **chỉ các tiêu đề** và tổ chức chúng theo cấu trúc phân cấp. Xác định cấp độ tiêu đề phù hợp (h1, h2, h3, h4, ...) dựa vào cấu trúc logic và phân cấp của tài liệu.

        Công việc của bạn gồm:
        1. Phân tích toàn bộ nội dung tài liệu
        2. Nhận diện tất cả các tiêu đề dựa trên định dạng, đánh số hoặc ngữ nghĩa
        3. Xác định cấp độ phân cấp tương ứng cho từng tiêu đề
        4. Nhóm các tiêu đề theo từng cấp
        5. Trả về kết quả dưới dạng JSON có cấu trúc như hướng dẫn bên dưới
        </TASK>

        <GUIDELINES>
        - **h1**: Tiêu đề chính của tài liệu hoặc các phần cấp cao nhất
        - **h2**: Các mục lớn nằm dưới h1
        - **h3**: Các mục con nằm dưới h2
        - **h4**: Các mục chi tiết hơn nằm dưới h3
        - Giữ nguyên thứ tự logic của các tiêu đề như trong tài liệu gốc
        - Bỏ qua mọi đoạn văn hay câu không phải là tiêu đề
        - Nếu trong tài liệu không có cấp độ nào đó thì bỏ qua khóa (key) đó trong JSON
        - Không bỏ qua bất kỳ cấp độ tiêu đề nào
        - **LƯU Ý QUAN TRỌNG**: Phân tích phân cấp tiêu đề cẩn thận. Các tiêu đề đánh số như “A.”, “B.”, “C.” thường là cấp h2; còn “A.1.”, “A.2.” là h3; và “A.1.1.” sẽ là h4

        <EXAMPLE_OF_HIERARCHY_PROCESSING>
        Nếu bạn thấy cấu trúc sau trong một tài liệu:

        THÔNG TIN KHÁCH HÀNG (MÃ KHÁCH HÀNG: CUST-0012345)
        A. Thông tin Khách hàng Cá nhân (Cập nhật: 05/07/2025)
        A.1. Thông tin định danh cơ bản
        A.2. Giấy tờ tùy thân hợp lệ
        B. Thông tin Địa chỉ & Môi trường sinh sống
        B.1. Địa chỉ cư trú hiện tại
        B.2. Địa chỉ thường trú
        C. Cam kết và Chữ ký

        Thì kết quả phân cấp đúng sẽ là:
        ```json
        {{
        "h1": ["THÔNG TIN KHÁCH HÀNG (MÃ KHÁCH HÀNG: CUST-0012345)"],
        "h2": ["A. Thông tin Khách hàng Cá nhân (Cập nhật: 05/07/2025)", "B. Thông tin Địa chỉ & Môi trường sinh sống", "C. Cam kết và Chữ ký"],
        "h3": ["A.1. Thông tin định danh cơ bản", "A.2. Giấy tờ tùy thân hợp lệ", "B.1. Địa chỉ cư trú hiện tại", "B.2. Địa chỉ thường trú"]
        }}
        ```

        </EXAMPLE_OF_HIERARCHY_PROCESSING>


        <EXAMPLE_OF_WHAT_NOT_TO_DO>
        Không bao gồm:
        - Nội dung văn bản hoặc đoạn văn
        - Chú thích, ghi chú, trích dẫn
        - Tiêu đề bảng hoặc tên cột
        - Số trang hoặc metadata của tài liệu
        - Gạch đầu dòng hoặc mục liệt kê không phải tiêu đề

        Ví dụ về kết quả không đúng:
        ```json
        {{
        "h1": ["THÔNG TIN KHÁCH HÀNG", "A. Thông tin Khách hàng Cá nhân"],
        "h2": ["A.1. Thông tin định danh cơ bản", "B. Thông tin Địa chỉ"]
        }}
        ```

        Ví dụ trên sai vì “A.1.” đáng lẽ phải là h3, vì nó nằm trong “A.” (là h2), chứ không phải là h2.
        </EXAMPLE_OF_WHAT_NOT_TO_DO>

        </GUIDELINES>

        <OUTPUT FORMAT>
        Trả về kết quả dưới dạng đối tượng JSON với các cặp key-value như sau: - Các khóa (key) là: "h1", "h2", "h3", "h4" - Giá trị (value) là các mảng chứa nội dung văn bản của các tiêu đề tương ứng - Sử dụng cú pháp JSON chuẩn và sạch
        Ví dụ:
                {{
                "h1": ["Giới thiệu", "Phương pháp", "Kết quả", "Kết luận"],
                "h2": ["Bối cảnh", "Phát biểu vấn đề", "Thu thập dữ liệu", "Phương pháp phân tích", "Những phát hiện chính", "Thảo luận"],
                "h3": ["Tổng quan tài liệu", "Khoảng trống nghiên cứu", "Thiết kế khảo sát", "Phân tích thống kê", "Chỉ số hiệu suất"],
                "h4": ["Tính toán kích thước mẫu", "Kỹ thuật xác thực"]
                }}
        </OUTPUT_FORMAT>

        <CONTENTS>
        {raw_text}
        </CONTENTS>
                """

    return f"""
        <ROLE>
        You are an expert in document structure analysis. You are highly capable of identifying section titles based on their wording, numbering style.
        </ROLE>

        <TASK>
        From the given document content (which may be plain text extracted from a structured document), extract only the headers and organize them in a hierarchical structure. Determine the appropriate header levels (h1, h2, h3, h4, ...) based on the document's logical structure and hierarchy.

        Your job is to:
        1. Analyze the entire document content
        2. Identify all headers based on formatting, numbering, or content cues
        3. Determine the appropriate hierarchy level for each header
        4. Group headers by their levels
        5. Return the structured JSON output as specified below
        </TASK>

        <GUIDELINES>
        - **h1**: Main document title or primary sections (top level)
        - **h2**: Major subsections under h1
        - **h3**: Sub-subsections under h2
        - **h4**: Detailed subsections under h3
        - Preserve the logical order of headers as they appear in the document
        - Skip any paragraph or sentence that is not a header
        - If a header level doesn't exist in the document, omit that key from the JSON
        - Do not skip any header level
        - **IMPORTANT**: If the content includes numbered headers like "A.", "B.", "C.", "D.", "E.", "F.", "G.", "H." ensure that all such headers are correctly mapped to their corresponding header levels.
        - **IMPORTANT**: Analyze header hierarchy carefully. Headers with numbering like "A.", "B.", "C." are typically h2 level, while "A.1.", "A.2." are h3 level, and "A.1.1." would be h4 level.

        <EXAMPLE_OF_HIERARCHY_PROCESSING>
        If you see this structure in a document:

        CUSTOMER INFORMATION (CUSTOMER ID: CUST-0012345)
        A. Personal Customer Information (Updated: 07/05/2025)
        A.1. Basic Identification Information
        A.2. Valid Personal Identification Documents
        B. Address & Living Environment Information
        B.1. Current Residential Address
        B.2. Permanent Address
        C. Commitment & Signature

        The correct hierarchical output should be:
        ```json
        {{
        "h1": [
            "CUSTOMER INFORMATION (CUSTOMER ID: CUST-0012345)",
            "Customer Analysis & Evaluation (For Internal Bank Use Only)"
        ],
        "h2": [
            "A. Personal Customer Information (Updated: 07/05/2025)",
            "B. Address & Living Environment Information",
            "C. Commitment & Signature"
        ],
        "h3": [
            "A.1. Basic Identification Information",
            "A.2. Valid Personal Identification Documents",
            "B.1. Current Residential Address",
            "B.2. Permanent Address"
        ]
        }}
        ```

        </EXAMPLE_OF_HIERARCHY_PROCESSING>

        <EXAMPLE_OF_WHAT_NOT_TO_DO>
        Do not include:
        - Body text or paragraph content
        - Captions, footnotes, or references
        - Table headers or column names
        - Page numbers or document metadata
        - Bullet points or list items that are not section headers

        Example of incorrect output:
        ```json
        {{
        "h1": [
            "CUSTOMER INFORMATION",
            "A. Personal Customer Information"
        ],
        "h2": [
            "A.1. Basic Identification Information",
            "B. Address Information"
        ]
        }}
        ```

        This is wrong because "A.1." should be h3 (under "A." which is h2), not h2.
        </EXAMPLE_OF_WHAT_NOT_TO_DO>
        </GUIDELINES>

        <OUTPUT FORMAT>
        Output as a JSON object with key-value pairs:
        - Keys should be the header level tags: "h1", "h2", "h3", "h4"
        - Values should be arrays containing the text content of headers at that level
        - Use clean, properly formatted JSON syntax

        Example:
        {{
        "h1": ["Introduction", "Methodology", "Results", "Conclusion"],
        "h2": ["Background", "Problem Statement", "Data Collection", "Analysis Methods", "Key Findings", "Discussion"],
        "h3": ["Literature Review", "Research Gap", "Survey Design", "Statistical Analysis", "Performance Metrics"],
        "h4": ["Sample Size Calculation", "Validation Techniques"]
        }}
        </OUTPUT FORMAT>

        <CONTENTS>
        {raw_text}
        </CONTENTS>
            """
