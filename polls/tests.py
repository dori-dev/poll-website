import datetime
from django.test import TestCase
from django.urls import reverse
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


class QuestionIndexViewTests(TestCase):
    @staticmethod
    def create_question(question_text: str, days: int) -> None:
        """
        Create a question with the given `question_text` and published the
        given number of `days` offset to now(negative for questions published
        in the past, positive for question that have yet to be published)
        """
        time = timezone.now() + datetime.timedelta(days=days)
        return Question.objects.create(
            question_text=question_text,
            published_date=time
        )

    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_questions'], [])

    def test_past_question(self):
        """
        Questions with a published_date in the past are
        displayed on the index page.
        """
        question = self.create_question(
            question_text="Past question.",
            days=-30
        )
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_questions'],
            [question],
        )

    def test_future_question(self):
        """
        Questions with a published_date in the future aren't
        displayed on the index page.
        """
        self.create_question(
            question_text="Future question.",
            days=30
        )
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_questions'], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only
        past questions are displayed.
        """
        question = self.create_question(
            question_text="Past question.",
            days=-30
        )
        self.create_question(
            question_text="Future question.",
            days=30
        )
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_questions'],
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = self.create_question(
            question_text="Past question 1.",
            days=-30
        )
        question2 = self.create_question(
            question_text="Past question 2.",
            days=-5
        )
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_questions'],
            [question2, question1],
        )
