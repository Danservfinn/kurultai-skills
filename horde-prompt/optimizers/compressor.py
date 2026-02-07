"""
Token compression utilities for horde-prompt.

Provides functions to estimate token count and compress prompts
while preserving semantic meaning.
"""

import re
from typing import List, Tuple


def estimate_tokens(text: str) -> int:
    """
    Estimate token count for text.

    Rough approximation: ~4 characters per token for English text.
    This is conservative; actual tokenization may vary.

    Args:
        text: Text to estimate

    Returns:
        Estimated token count
    """
    if not text:
        return 0
    return len(text) // 4


def compress_prompt(prompt: str, target_tokens: int) -> Tuple[str, float]:
    """
    Compress prompt to target token count while preserving semantics.

    Compression strategies (applied in order):
    1. Remove redundant whitespace
    2. Convert prose lists to bracket notation
    3. Replace verbose phrases with compact syntax
    4. Remove non-essential examples
    5. Truncate with ellipsis if still over target

    Args:
        prompt: Original prompt
        target_tokens: Target token count

    Returns:
        (compressed_prompt, compression_ratio)
    """
    original_tokens = estimate_tokens(prompt)

    if original_tokens <= target_tokens:
        return prompt, 0.0

    compressed = prompt
    current_tokens = original_tokens

    # Strategy 1: Remove redundant whitespace
    compressed = re.sub(r'\n{3,}', '\n\n', compressed)
    compressed = re.sub(r' +', ' ', compressed)
    current_tokens = estimate_tokens(compressed)

    if current_tokens <= target_tokens:
        return compressed, 1.0 - (current_tokens / original_tokens)

    # Strategy 2: Convert prose lists to bracket notation
    # "- item one\n- item two\n- item three" → "[item one, item two, item three]"
    compressed = re.sub(
        r'(?m)^- (.+)(?:\n- (.+))*(?:\n- (.+))*',
        lambda m: '[' + ', '.join(m.groups()) + ']',
        compressed
    )
    current_tokens = estimate_tokens(compressed)

    if current_tokens <= target_tokens:
        return compressed, 1.0 - (current_tokens / original_tokens)

    # Strategy 3: Replace verbose phrases with compact syntax
    replacements = {
        r'You are a ([^.]+)\.': r'ROLE: \1',
        r'Your expertise (?:includes|is|includes the following):': 'EXPERTISE:',
        r'Please (?:provide|generate|create)': 'OUTPUT:',
        r'For each (?:item|entry|aspect)': 'PER:',
        r'Consider (?:the|all)': 'CHECK:',
    }

    for pattern, replacement in replacements.items():
        compressed = re.sub(pattern, replacement, compressed, flags=re.IGNORECASE)
        current_tokens = estimate_tokens(compressed)
        if current_tokens <= target_tokens:
            break

    if current_tokens <= target_tokens:
        return compressed, 1.0 - (current_tokens / original_tokens)

    # Strategy 4: Remove examples (between "Example:" and next section)
    compressed = re.sub(
        r'Example[:\s]*\n.*?(?=\n\n[A-Z]|$)',
        '',
        compressed,
        flags=re.DOTALL
    )
    current_tokens = estimate_tokens(compressed)

    if current_tokens <= target_tokens:
        return compressed, 1.0 - (current_tokens / original_tokens)

    # Strategy 5: Truncate if still over target
    # Try to truncate at a sentence boundary
    sentences = re.split(r'(?<=[.!?])\s+', compressed)
    truncated = []
    tokens_so_far = 0

    for sentence in sentences:
        sentence_tokens = estimate_tokens(sentence)
        if tokens_so_far + sentence_tokens > target_tokens:
            break
        truncated.append(sentence)
        tokens_so_far += sentence_tokens

    if truncated:
        compressed = ' '.join(truncated) + '...'
    else:
        # Even one sentence is too long, truncate character-wise
        compressed = compressed[:target_tokens * 4] + '...'

    final_tokens = estimate_tokens(compressed)
    return compressed, 1.0 - (final_tokens / original_tokens)


def compress_to_budget(prompt: str, budget: str) -> str:
    """
    Compress prompt to specified budget level.

    Args:
        prompt: Original prompt
        budget: "minimal" | "standard" | "verbose"

    Returns:
        Compressed prompt at specified budget level
    """
    # Budget levels as token targets (relative to original)
    budget_ratios = {
        "minimal": 0.3,   # 30% of original
        "standard": 0.6,  # 60% of original
        "verbose": 1.0,   # 100% of original
    }

    target_ratio = budget_ratios.get(budget, 0.6)
    target_tokens = estimate_tokens(prompt) * target_ratio

    compressed, _ = compress_prompt(prompt, target_tokens)
    return compressed
