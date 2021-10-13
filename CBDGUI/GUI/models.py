from typing import Any


class WebData:
    comment_rate_history: list[float] = [0, 14.5, 2.3, 0.7, 1.9]
    comment_counter_history: list[int] = [0, 10, 24, 30, 60]
    top_comments: list[dict[str, Any]] = []
    current_question: str = ''
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
