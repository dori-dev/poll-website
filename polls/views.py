from django.shortcuts import render, get_object_or_404
from .models import Question


def index(request):
    latest_questions = Question.objects.order_by(
        '-published_date')[:5]
    context = {
        'latest_questions': latest_questions
    }
    return render(request, "polls/index.html", context)


def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    context = {
        'question': question
    }
    return render(request, 'polls/detail.html', context)
