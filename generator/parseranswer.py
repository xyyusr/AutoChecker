import re
from typing import Optional

def parse_java_code_from_answer(answer: str) -> Optional[str]:
    idx = answer.find("```java")
    if idx == -1:
        return None
    else:
        end_idx = answer.find("```\n")
        java_code = answer[idx + 7: end_idx]
        return java_code


# print(parser_node_from_answer(
# """
# The nodes that need attention are:
# 1. string1
# 2. string2
# 3. string3
# """
# ))