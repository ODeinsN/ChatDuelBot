from ..models import WebData
from threading import Lock
from typing import Any
from array import array
import pickle
from pathlib import Path


def write_data_into_file(comment_rate: list[float], comment_counter: list[int], top_words: list[dict[str, Any]], current_question: str):
    lock = Lock()
    with lock:
        src_dir_path = 'CBDGUI/GUI/utils/src'

        p = Path(src_dir_path)
        p.mkdir(exist_ok=True)
        (p / 'comment_counter.data').open('w').write('')
        (p / 'comment_rate.data').open('w').write('')
        (p / 'top_comments.data').open('w').write('')
        (p / 'current_question.data').open('w').write('')

        with open(f'{src_dir_path}/comment_counter.data', 'wb') as file:
            pickle.dump(comment_counter, file, protocol=pickle.HIGHEST_PROTOCOL)

        with open(f'{src_dir_path}/comment_rate.data', 'wb') as file:
            pickle.dump(comment_rate, file, protocol=pickle.HIGHEST_PROTOCOL)

        with open(f'{src_dir_path}/top_comments.data', 'wb') as file:
            pickle.dump(top_words, file, protocol=pickle.HIGHEST_PROTOCOL)

        with open(f'{src_dir_path}/current_question.data', 'wb') as file:
            pickle.dump(current_question, file, protocol=pickle.HIGHEST_PROTOCOL)


def update_web_data():
    lock = Lock()
    src_dir_path = 'GUI/utils/src'
    with lock:
        with open(f'{src_dir_path}/comment_counter.data', 'rb') as file:
            WebData.comment_counter_history = pickle.load(file)

        with open(f'{src_dir_path}/comment_rate.data', 'rb') as file:
            WebData.comment_rate_history = pickle.load(file)

        with open(f'{src_dir_path}/top_comments.data', 'rb') as file:
            WebData.top_comments = pickle.load(file)

        with open(f'{src_dir_path}/current_question.data', 'rb') as file:
            WebData.current_question = pickle.load(file)
