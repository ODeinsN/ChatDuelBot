from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from . models import Question, Choice
from django.urls import reverse
from django.views import generic


class IndexView(generic.ListView):
    template_name = 'GUI/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        return Question.objects.order_by('-pub_date')[:5]
#
# def index(request):
#     latest_question_list = Question.objects.order_by('-pub_date')[:5]
#     context = {'latest_question_list': latest_question_list}
#     return render(request, 'GUI/index.html', context)


class DetailView(generic.DetailView):
    model = Question
    template_name = 'GUI/detail.html'

# def detail(request, question_id: int):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, 'GUI/detail.html', {'question': question})


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'GUI/results.html'

# def results(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, 'GUI/results.html', {'question': question})


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'GUI/detail.html', {'question': question, 'error_message': "You didn't select a choice.",})
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('GUI:results', args=(question.id,)))
