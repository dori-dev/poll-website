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

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions
        whose published_date older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(published_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions
        whose published_date is within the last day.
        """
        time = timezone.now() - datetime.timedelta(
            hours=23, minutes=59, seconds=59
        )
        recent_question = Question(published_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_was_published_recently_with_now_question(self):
        """
        was_published_recently() returns True for questions
        whose published_date is just now.
        """
        time = timezone.now()
        now_question = Question(published_date=time)
        self.assertIs(now_question.was_published_recently(), True)
