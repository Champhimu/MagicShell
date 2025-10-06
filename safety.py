import re

DANGEROUS_CMD_PATTERN = re.compile(r'\brm\s+(-rf\s+)?|rmdir\b')

def is_dangerous_command(cmd: str) -> bool:
    return bool(DANGEROUS_CMD_PATTERN.search(cmd))

def strip_code_fences(text: str) -> str:
    # Remove triple backticks (```bash ... ```), optional language hints
    text = re.sub(r"```(?:cmd|bash)?\s*([\s\S]*?)\s*```", r"\1", text)
    
    # Remove inline backticks (`command`)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    return text.strip()