class SourceCodeParser:
    @staticmethod
    def parse(file_content: str) -> dict:
        """
        Receives raw file content, sanitizes it (removes excess blank lines and spaces),
        and returns the sanitized text and payload size.
        """
        # Remove excess empty lines to save LLM tokens
        lines = file_content.splitlines()
        sanitized_lines = [line.rstrip() for line in lines if line.strip()]
        sanitized_text = "\n".join(sanitized_lines)
        
        payload_size = len(sanitized_text.encode("utf-8"))
        original_size = len(file_content.encode("utf-8"))
        
        return {
            "sanitized_content": sanitized_text,
            "payload_size_bytes": payload_size,
            "original_size_bytes": original_size
        }
