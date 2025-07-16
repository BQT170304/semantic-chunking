import os
from .markdown_generator import ClaudeMarkdownGenerator, NovaMarkdownGenerator
from shared.logging.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

def read_input_file(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def save_markdown(output_path: str, markdown: str):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown)

def main(input_file: str, output_file: str, use_nova: bool = False):
    raw_text = read_input_file(input_file)
    # Choose between Nova (faster) or Claude (higher quality)
    try:
        if use_nova:
            logger.info("Attempting to use AWS Bedrock Nova Micro (faster)...")
            generator = NovaMarkdownGenerator()
            model_name = "Nova Micro"
        else:
            logger.info("Attempting to use AWS Bedrock Claude 3 Haiku...")
            generator = ClaudeMarkdownGenerator()
            model_name = "Claude 3 Haiku"
            
        markdown = generator.generate(raw_text)
        logger.info(f"Successfully used AWS Bedrock {model_name}", status="success")
    except Exception as e:
        logger.error("Unexpected error occurred", error=str(e), status="failed")
        logger.info("Run 'python quick_bedrock_check.py' to diagnose issues")
        raise
    
    save_markdown(output_file, markdown)
    logger.info("Markdown saved successfully", output_file=output_file, status="success")

if __name__ == "__main__":
    # Set use_nova=True for faster processing with Amazon Nova Micro
    main("E:\\WordSpace\\input\\output.txt", "output1.txt", use_nova=True)
