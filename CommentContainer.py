from dataclasses import dataclass
from typing import Set
import random

"""
Tracks how many comments used this word and saves the related comment
"""


@dataclass
class CommentContainer:
    comment_set: Set
    comment_counter: int = 0

    def __init__(self, comment):
        self.comment_counter += 1
        self.comment_set = set()
        self.comment_set.add(comment)

    def __lt__(self, other):
        return self.comment_counter < other.comment_counter

    def add_comment(self, comment):
        self.comment_set.add(comment)
        self.comment_counter += 1

    def get_random_comment(self):
        return list(self.comment_set)[random.randint(0, len(self.comment_set) - 1)].message

    def get_comment_counter(self) -> int:
        return self.comment_counter
