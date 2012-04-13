from django.test import TestCase
from django.utils import timezone
from polls.models import Choice, Poll
from django.core.urlresolvers import reverse
from polls.forms import PollVoteForm

class HomePageViewTest(TestCase):
    def test_root_url_shows_all_polls(self):
        # set up some pools
        poll1 = Poll(question='6 times 7', pub_date=timezone.now())
        poll1.save()
        poll2 = Poll(question='life, the universer and everything',
                    pub_date=timezone.now())
        poll2.save()

        response = self.client.get('/')

        # check we've user the right template
        self.assertTemplateUsed(response, 'home.html')

        # check we've passed the polls to the template
        polls_in_context = response.context['polls']
        self.assertEquals(list(polls_in_context), [poll1, poll2])

        # check the poll names appear on the page
        self.assertIn(poll1.question, response.content)
        self.assertIn(poll2.question, response.content)

        # check the page also contains the url to individual polls pages
        poll1_url = reverse('poll_views_poll', args=[poll1.id, ])
        self.assertIn(poll1_url, response.content)
        poll2_url = reverse('poll_views_poll', args=[poll2.id, ])
        self.assertIn(poll2_url, response.content)


class SinglePollViewTest(TestCase):
    def test_page_shows_poll_title_and_no_votes_message(self):
        # set up two polls, to check the right one is displayed
        poll1 = Poll(question='6 times 7', pub_date=timezone.now())
        poll1.save()
        poll2 = Poll(question='life, the universer and everything',
                    pub_date=timezone.now())
        poll2.save()

        response = self.client.get('/poll/%d/' % (poll2.id, ))

        # check we've user the poll template
        self.assertTemplateUsed(response, 'poll.html')

        # check we've passed the right poll into the context
        self.assertEquals(response.context['poll'], poll2)

        # check the poll's question appears on the page
        self.assertIn(poll2.question, response.content)

        # check out 'no votes yes' message appears
        self.assertIn('No-one has voted on this poll yet', response.content)

    def test_page_shows_poll_choices_using_form(self):
        # set up a poll with choices
        poll1 = Poll(question='time', pub_date=timezone.now())
        poll1.save()
        choice1 = Choice(poll=poll1, choice="PM", votes=0)
        choice1.save()
        choice2 = Choice(poll=poll1, choice="Gardener's", votes=0)
        choice2.save()

        response = self.client.get('/poll/%d/' % (poll1.id, ))

        # check we've passed in a form of the right type
        self.assertTrue(isinstance(response.context['form'], PollVoteForm))

        # and check the check the form is begin used in the template,
        # by checking for the choice text
        self.assertIn(choice1.choice, response.content.replace('&#39;',"'"))
        self.assertIn(choice2.choice, response.content.replace('&#39;',"'"))

    def test_view_shows_procentage_of_votes(self):
        # set up a poll with choices
        poll1 = Poll(question='6 times 7', pub_date=timezone.now())
        poll1.save()
        choice1 = Choice(poll=poll1, choice='42', votes=1)
        choice1.save()
        choice2 = Choice(poll=poll1, choice='The Ultimate Answer', votes=2)
        choice2.save()

        response = self.client.get('/poll/%d/' % (poll1.id, ))

        # check the procentages of votes are shown, sensibly rounded
        self.assertIn('33 %: 42', response.content)
        self.assertIn('67 %: The Ultimate Answer', response.content)

        # add that the 'no-one has voted' message is gone
        self.assertNotIn('No-one has voted', response.content)

    def test_view_can_handle_votes_vis_POST(self):
        # set up a poll with choices
        poll1 = Poll(question='6 times 7', pub_date=timezone.now())
        poll1.save()
        choice1 = Choice(poll=poll1, choice='42', votes=1)
        choice1.save()
        choice2 = Choice(poll=poll1, choice='The Ultimate Answer', votes=3)
        choice2.save()

        # set up our POST data - keys and values are strings
        post_data = {'vote': str(choice2.id)}

        # make our request to the view
        poll_url = '/poll/%d/' % (poll1.id, )
        response = self.client.post(poll_url, data=post_data)

        # retrive the updated choice from the database
        choice_in_db = Choice.objects.get(pk=choice2.id)

        # check it's votes have gone up by 1
        self.assertEquals(choice_in_db.votes, 4)

        # always redirect after a POST - even if, in this case, we go back
        # to the same page.
        self.assertRedirects(response, poll_url)

    def test_view_shows_total_votes(self):
        # set up a poll with choices
        poll1 = Poll(question='6 times 7', pub_date=timezone.now())
        poll1.save()
        choice1 = Choice(poll=poll1, choice='42', votes=1)
        choice1.save()
        choice2 = Choice(poll=poll1, choice='The Ultimate Answer', votes=2)
        choice2.save()

        response = self.client.get('/poll/%d/' % (poll1.id, ))
        self.assertIn('3 votes', response.content)

        # also check we only pluralise "votes" if necessary. details!
        choice2.votes = 0
        choice2.save()
        response = self.client.get('/poll/%d/' % (poll1.id, ))
        self.assertIn('1 vote', response.content)
        self.assertNotIn('1 votes', response.content)
