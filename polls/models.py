# standard libraries
import datetime
# third party libraries
from django.db import models
from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Question(models.Model):
    question_text = models.CharField(max_length=256)
    published_date = models.DateTimeField(
        _('date published')
    )

    @admin.display(
        boolean=True,
        ordering='-published_date',
        description='Published recently?'
    )
    def was_published_recently(self):
        one_day_ago = timezone.now() - datetime.timedelta(days=1)
        return one_day_ago <= self.published_date <= timezone.now()

    @admin.display(
        description='Choices'
    )
    def choice_numbers(self):
        return self.choice_set.count()

    def votes_count(self):
        votes = 0
        for choice in self.choice_set.all():
            votes += choice.votes
        return votes

    def sorted_choice(self):
        return self.choice_set.order_by('-votes')

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )
    choice_text = models.CharField(max_length=256)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text
