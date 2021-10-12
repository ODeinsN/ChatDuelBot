import random
from dataclasses import dataclass
from typing import Set

"""
Tracks how many comments used this word and saves the related comment
"""


@dataclass
class CommentContainer:
    _comment_set: Set
    _comment_counter: int = 0

    def __init__(self, comment):
        self._comment_counter += 1
        self._comment_set = set()
        self._comment_set.add(comment)

    def __lt__(self, other):
        return self._comment_counter < other.comment_counter

    def add_comment(self, comment):
        self._comment_set.add(comment)
        self._comment_counter += 1

    def get_random_comment(self):
        return list(self._comment_set)[random.randint(0, len(self._comment_set) - 1)].message

    @property
    def comment_counter(self):
        return self._comment_counter

    def get_comment_counter(self) -> int:
        return self._comment_counter

    def get_comment(self, index: int):
        l = list(self._comment_set)
        if 0 <= index < len(l):
            return l[index].message
        return None
