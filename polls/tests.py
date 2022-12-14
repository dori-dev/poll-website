import datetime
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import Question, Choice


def create_question(question_text: str, days: int) -> Question:
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


def create_choice(question: Question, choice_text: str) -> Choice:
    """
    Create a choice with the given `question` and `choice_test` and
    default of votes number is 0 vote.
    """
    return Choice.objects.create(
        question=question,
        choice_text=choice_text
    )


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
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_questions'], [])

    def test_past_question_with_zero_choice(self):
        create_question(
            question_text="Past question.",
            days=-30
        )
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(
            response.context['latest_questions'],
            [],
        )

    def test_past_question_with_one_choice(self):
        question = create_question(
            question_text="Past question",
            days=-30
        )
        create_choice(question, "choice1")
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(
            response.context['latest_questions'],
            [],
        )

    def test_future_question_with_zero_choice(self):
        create_question(
            question_text="Future question.",
            days=30
        )
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_questions'], [])

    def test_future_question_with_one_choice(self):
        question = create_question(
            question_text="Future question.",
            days=30
        )
        create_choice(question, "choice1")
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_questions'], [])

    def test_past_question(self):
        """
        Questions with a published_date in the past are
        displayed on the index page.
        """
        question = create_question(
            question_text="Past question.",
            days=-30
        )
        create_choice(question, "choice1")
        create_choice(question, "choice2")
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
        question = create_question(
            question_text="Future question.",
            days=30
        )
        create_choice(question, "choice1")
        create_choice(question, "choice2")
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_questions'], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only
        past questions are displayed.
        """
        past_question = create_question(
            question_text="Past question.",
            days=-30
        )
        create_choice(past_question, "choice1")
        create_choice(past_question, "choice2")
        future_question = create_question(
            question_text="Future question.",
            days=30
        )
        create_choice(future_question, "choice1")
        create_choice(future_question, "choice2")
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_questions'],
            [past_question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(
            question_text="Past question 1.",
            days=-30
        )
        create_choice(question1, "choice1")
        create_choice(question1, "choice2")
        question2 = create_question(
            question_text="Past question 2.",
            days=-5
        )
        create_choice(question2, "choice1")
        create_choice(question2, "choice2")
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_questions'],
            [question2, question1],
        )


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a published_date
        in the future returns a 404 not found.
        """
        future_question = create_question(
            question_text='Future question.',
            days=5
        )
        create_choice(future_question, "choice1")
        create_choice(future_question, "choice2")
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a published_date
        in the past displays the question's text.
        """
        past_question = create_question(
            question_text='Past Question.',
            days=-5
        )
        create_choice(past_question, "choice1")
        create_choice(past_question, "choice2")
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_past_question_with_zero_choice(self):
        past_question = create_question(
            question_text='Past Question.',
            days=-5
        )
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question_with_one_choice(self):
        past_question = create_question(
            question_text='Past Question.',
            days=-5
        )
        create_choice(past_question, "choice1")
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_future_question_with_zero_choice(self):
        future_question = create_question(
            question_text='Future question.',
            days=5
        )
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_future_question_with_one_choice(self):
        future_question = create_question(
            question_text='Future question.',
            days=5
        )
        create_choice(future_question, "choice1")
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class QuestionResultViewTests(TestCase):
    def _vote(self, question, choice, return_response=False):
        url = reverse('polls:detail', args=(question.id,))
        response = self.client.post(
            url,
            {
                "choice": str(choice.id)
            },
            follow=True
        )
        if return_response:
            return response
        return response.redirect_chain[0][0]

    def test_result_with_one_vote(self):
        question = create_question(
            question_text="The sample question",
            days=-5
        )
        choice1 = create_choice(question, "choice1")
        choice2 = create_choice(question, "choice2")
        response = self.client.get(self._vote(question, choice2))
        self.assertEqual(question.votes_count(), 1)
        self.assertContains(response, question.question_text)
        self.assertContains(response, choice1.choice_text)
        self.assertContains(response, choice2.choice_text)
        self.assertContains(response, "1 vote")
        self.assertContains(response, "0 vote")
        self.assertNotContains(response, "1 votes")
        self.assertNotContains(response, "0 votes")

    def test_result_with_two_vote(self):
        question = create_question(
            question_text="The sample question",
            days=-5
        )
        choice1 = create_choice(question, "choice1")
        choice2 = create_choice(question, "choice2")
        self._vote(question, choice2)
        response = self.client.get(self._vote(question, choice2))
        self.assertEqual(question.votes_count(), 2)
        self.assertContains(response, question.question_text)
        self.assertContains(response, choice1.choice_text)
        self.assertContains(response, choice2.choice_text)
        self.assertContains(response, "2 votes")
        self.assertContains(response, "0 vote")
        self.assertNotContains(response, "0 votes")

    def test_result_with_three_vote(self):
        question = create_question(
            question_text="The sample question",
            days=-5
        )
        choice1 = create_choice(question, "choice1")
        choice2 = create_choice(question, "choice2")
        self._vote(question, choice1)
        response = self.client.get(self._vote(question, choice2))
        self.assertEqual(question.votes_count(), 2)
        self.assertContains(response, question.question_text)
        self.assertContains(response, choice1.choice_text)
        self.assertContains(response, choice2.choice_text)
        self.assertContains(response, "1 vote")
        self.assertNotContains(response, "1 votes")

    def test_result_for_future_question(self):
        question = create_question(
            question_text="The sample question",
            days=5
        )
        choice1 = create_choice(question, "choice1")
        choice2 = create_choice(question, "choice2")
        response = self._vote(question, choice1, return_response=True)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(question.votes_count(), 0)
        response = self._vote(question, choice2, return_response=True)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(question.votes_count(), 0)

    def test_result_for_zero_choice(self):
        question = create_question(
            question_text="The sample question",
            days=-5
        )
        url = reverse('polls:results', args=(question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(question.votes_count(), 0)

    def test_result_for_one_choice(self):
        question = create_question(
            question_text="The sample question",
            days=-5
        )
        choice1 = create_choice(question, "choice1")
        response = self._vote(question, choice1, return_response=True)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(question.votes_count(), 0)
        url = reverse('polls:results', args=(question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(question.votes_count(), 0)
