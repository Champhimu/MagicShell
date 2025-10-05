import re

DANGEROUS_CMD_PATTERN = re.compile(r'\brm\s+(-rf\s+)?|rmdir\b')

def is_dangerous_command(cmd: str) -> bool:
    return bool(DANGEROUS_CMD_PATTERN.search(cmd))
