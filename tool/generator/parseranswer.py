import re
from typing import Optional

def parse_java_code_from_answer(answer: str) -> Optional[str]:
    idx = answer.find("```java")
    if idx == -1:
        return None
    else:
        end_idx = answer.find("}\n```")
        java_code = answer[idx + 7: end_idx+1]
        return java_code
