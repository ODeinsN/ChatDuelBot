from typing import Any


class WebData:
    comment_rate_history: list[float] = [0, 14.5, 2.3, 0.7, 1.9]
    comment_counter_history: list[int] = [0, 10, 24, 30, 60]
    top_comments: list[dict[str, Any]] = []
    current_question: str = ''