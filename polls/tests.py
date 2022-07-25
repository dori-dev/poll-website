import datetime

from django.test import TestCase
from django.utils import timezone

from .models import Question


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions
        whose published_date is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(published_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_now_question(self):
        """
        was_published_recently() returns True for questions
        whose published_date is just now.
        """
        now_question = Question(published_date=timezone.now())
        self.assertIs(now_question.was_published_recently(), True)
