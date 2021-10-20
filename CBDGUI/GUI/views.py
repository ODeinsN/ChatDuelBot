from typing import Any

import pandas as pandas
import plotly.express as px
from django.shortcuts import render
from plotly.offline import plot

from .models import WebData
from .utils import WebDataUpdater as wdu


def control(request):
    # time.sleep(1)
    wdu.update_web_data()
    # print(f'{WebData.comment_rate_history=}')
    # print(f'{WebData.comment_counter_history=}')
    # print(f'{WebData.top_comments=}')
    template = 'plotly_dark'
    graph_size = {'x': 680, 'y': 430}
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

    comment_rate_div = plot(comment_rate_fig, auto_open=False,
                            output_type='div', include_plotlyjs=False, link_text="")
    comment_counter_div = plot(comment_counter_fig, auto_open=False, output_type='div', include_plotlyjs=False,
                               link_text="")

    top_words: list[dict[str, Any]] = WebData.top_comments
    context = \
        {
            'range': [x for x in range(5)],
            'comment_rate_div': comment_rate_div,
            'comment_counter_div': comment_counter_div,
            'top_words': top_words,
            'graph_size': graph_size
        }
    # print(f'{top_words=}')
    # print(f'{WebData.comment_rate_history=}')
    # print(f'{WebData.comment_rate_history=}')

    # return HttpResponseRedirect(reverse('GUI:control'))
    return render(request, 'GUI/control.html', context)


def display(request):
    wdu.update_web_data()
    context = \
        {'range': [x for x in range(3)],
         'top_words': WebData.top_comments,
         'current_question': WebData.current_question
         }
    return render(request, 'GUI/display.html', context)
