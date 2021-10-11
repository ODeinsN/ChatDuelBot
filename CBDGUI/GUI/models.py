from django.db import models
import datetime
from django.utils import timezone


class WebData:
    comment_rate_history: list[float] = [1, 2, 3, 4, 5, 6]
    comment_counter_history: list[int] = [0]
    _top_comments: list[dict[str, object]] = []

    # @property
    # def comment_rate_history(self):
    #     return self._comment_rate_history
    #
    # @comment_rate_history.setter
    # def comment_rate_history(self, val):
    #     self._comment_rate_history = val
    #
    # @property
    # def comment_counter_history(self):
    #     return self._comment_counter_history
    #
    # @comment_counter_history.setter
    # def comment_counter_history(self, val):
    #     self._comment_counter_history = val

# class Question(models.Model):
#     question_text = models.CharField(max_length=200)
#     pub_date: datetime.time = models.DateTimeField('data published')
#
#     def __str__(self):
#         return self.question_text
#
#     def was_published_recently(self):
#         now = timezone.now()
#         return now - datetime.timedelta(days=1) <= self.pub_date <= now
#
#
# class Choice(models.Model):
#     question = models.ForeignKey(Question, on_delete=models.CASCADE)
#     choice_text = models.CharField(max_length=200)
#     votes = models.IntegerField(default=0)
#
#     def __str__(self):
#         return self.choice_text
