from django.db.models import F, Count
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from .models import Choice, Question


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_questions'

    def get_queryset(self):
        """Return the last ten published questions
        not including those set to be published in the future and
        not including those have lower than 2 question.
        """
        recent_questions = Question.objects.filter(
            published_date__lte=timezone.now()
        ).order_by('-published_date')
        have_choice_questions = filter(
            lambda question: question.choice_set.count() >= 2,
            recent_questions
        )
        return list(have_choice_questions)[:10]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        and have greaten than or equal 2 choice.
        """
        if self.request.user.is_staff:
            return Question.objects.all()
        return Question.objects.annotate(
            n_choice=Count("choice")
        ).filter(
            n_choice__gte=2,
            published_date__lte=timezone.now()
        )

    def post(self, request, *args, **kwargs):
        question_id = kwargs.get('pk')
        if not request.user.is_staff:
            filtered_question = Question.objects.annotate(
                n_choice=Count("choice")
            ).filter(
                n_choice__gte=2,
                published_date__lte=timezone.now()
            )
        else:
            filtered_question = Question
        if question_id is None:
            return redirect('polls:index')
        question = get_object_or_404(filtered_question, pk=question_id)
        try:
            selected_choice: Choice = question.choice_set.get(
                pk=request.POST['choice']
            )
        except (KeyError, Choice.DoesNotExist):
            # Redisplay the question voting form.
            context = {
                'question': question,
                'error_message': "You didn't select a choice.",
            }
            return render(request, 'polls/detail.html', context)
        else:
            # Using F() to avoiding race conditions
            selected_choice.votes = F('votes') + 1
            selected_choice.save()
            return redirect(reverse('polls:results', args=(question.id,)))


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        and have greaten than or equal 2 choice.
        """
        if self.request.user.is_staff:
            return Question.objects.all()
        return Question.objects.annotate(
            n_choice=Count("choice")
        ).filter(
            n_choice__gte=2,
            published_date__lte=timezone.now()
        )
