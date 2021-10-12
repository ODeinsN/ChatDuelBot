import time

import numpy
import pandas as pandas
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
# from . models import Question, Choice
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .models import WebData
from plotly.offline import plot
import plotly.graph_objects as go
import plotly.express as px
from typing import Any
from .utils import WebDataUpdater as wdu


# class IndexView(generic.ListView):
#     template_name = 'GUI/index.html'
#     context_object_name = 'latest_question_list'
#
#     def get_queryset(self):
#         return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]
#
# # def index(request):
# #     latest_question_list = Question.objects.order_by('-pub_date')[:5]
# #     context = {'latest_question_list': latest_question_list}
# #     return render(request, 'GUI/index.html', context)
#
#
# class DetailView(generic.DetailView):
#     model = Question
#     template_name = 'GUI/detail.html'
#
#     def get_queryset(self):
#         return Question.objects.filter(pub_date__lte=timezone.now())
#
# # def detail(request, question_id: int):
# #     question = get_object_or_404(Question, pk=question_id)
# #     return render(request, 'GUI/detail.html', {'question': question})
#
#
# class ResultsView(generic.DetailView):
#     model = Question
#     template_name = 'GUI/results.html'
#
# # def results(request, question_id):
# #     question = get_object_or_404(Question, pk=question_id)
# #     return render(request, 'GUI/results.html', {'question': question})
#
#
# def vote(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     try:
#         selected_choice = question.choice_set.get(pk=request.POST['choice'])
#     except (KeyError, Choice.DoesNotExist):
#     return render(request, 'GUI/detail.html', {'question': question, 'error_message': "You didn't select a choice.",})
#     else:
#         selected_choice.votes += 1
#         selected_choice.save()
#         return HttpResponseRedirect(reverse('GUI:results', args=(question.id,)))


def control(request):
    # time.sleep(1)
    wdu.update_web_data()
    print(f'{WebData.comment_rate_history=}')
    print(f'{WebData.comment_counter_history=}')
    print(f'{WebData.top_comments=}')
    template = 'plotly_dark'
    graph_size = {'x': 750, 'y': 500}
    comment_rate_df = pandas.DataFrame(dict(
        comment_rate=WebData.comment_rate_history
    ))
    comment_counter_df = pandas.DataFrame(dict(
        comment_counter=WebData.comment_counter_history
    ))
    comment_rate_fig = px.line(
        comment_rate_df,
        title=f"current: {WebData.comment_rate_history[-1]}",
        template=template,
        height=graph_size['y'],
        width=graph_size['x']
    )

    comment_counter_fig = px.line(
        comment_counter_df,
        title=f"current: {WebData.comment_counter_history[-1]}",
        template=template,
        height=graph_size['y'],
        width=graph_size['x']
    )

    comment_rate_div = plot(comment_rate_fig, auto_open=False, output_type='div', include_plotlyjs=False, link_text="")
    comment_counter_div = plot(comment_counter_fig, auto_open=False, output_type='div', include_plotlyjs=False, link_text="")

    top_words: list[dict[str, Any]] = WebData.top_comments
    context = \
        {
            'range': [x for x in range(5)],
            'comment_rate_div': comment_rate_div,
            'comment_counter_div': comment_counter_div,
            'top_words': top_words,
            'graph_size': graph_size
        }
    print(f'{top_words=}')
    print(f'{WebData.comment_rate_history=}')
    print(f'{WebData.comment_rate_history=}')

    # return HttpResponseRedirect(reverse('GUI:control'))
    return render(request, 'GUI/control.html', context)
