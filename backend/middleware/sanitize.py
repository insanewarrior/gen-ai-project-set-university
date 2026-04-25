import logging
import re

logger = logging.getLogger(__name__)

MAX_LENGTH = 2000

_INJECTION_PATTERNS = re.compile(
    r"ignore previous( instructions)?|system:|<\|im_start\|>|</s>|\[INST\]|\[/INST\]|<\|endoftext\|>|<\|im_end\|>",
    re.IGNORECASE,
)


def sanitize_llm_input(text: str) -> str:
    if len(text) > MAX_LENGTH:
        logger.warning("Input truncated from %d to %d chars", len(text), MAX_LENGTH)
        text = text[:MAX_LENGTH]

    text = _INJECTION_PATTERNS.sub("", text)

    text = (
        text.replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("{", "&#123;")
            .replace("}", "&#125;")
    )

    return text
