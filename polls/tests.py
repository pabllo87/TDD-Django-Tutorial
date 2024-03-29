from django.test import TestCase
from django.utils import timezone
from polls.models import Choice, Poll
from django.core.urlresolvers import reverse


class PollModelTest(TestCase):
    def test_creating_a_new_poll_and_saving_it_to_the_database(self):
        # start by createing a new Poll object with its "question" set
        poll = Poll()
        poll.question = "What's up?"
        poll.pub_date = timezone.now()

        # check we can save it to the database
        poll.save()

        # now check we can find it in the database again
        all_polls_in_database = Poll.objects.all()
        self.assertEquals(len(all_polls_in_database), 1)
        only_poll_in_database = all_polls_in_database[0]
        self.assertEquals(only_poll_in_database, poll)

        # and check that is's saved its two attributes: question and pub_date
        self.assertEquals(only_poll_in_database.question, "What's up?")
        self.assertEquals(only_poll_in_database.pub_date, poll.pub_date)

    def test_verbose_name_for_pub_date(self):
        for field in Poll._meta.fields:
            if field.name == 'pub_date':
                self.assertEquals(field.verbose_name, 'Date published')

    def test_poll_objects_are_named_after_thier_question(self):
        p = Poll()
        p.question = "How is babby formed?"
        self.assertEquals(unicode(p), 'How is babby formed?')


class ChoiceModelTest(TestCase):
    def test_createing_same_choices_for_a_poll(self):
        #start by creating a new Poll object
        poll = Poll()
        poll.question = "What's up?"
        poll.pub_date = timezone.now()
        poll.save()

        # now create a Choice object
        choice = Choice()

        # link it with our Poll
        choice.poll = poll

        # give it some text
        choice.choice = "doin' fine..."

        # and let's say it's had some votes
        choice.votes = 3

        # save it
        choice.save()

        # try retrivering it from the database, using the poll object's reverse
        # lookup
        poll_choices = poll.choice_set.all()
        self.assertEquals(poll_choices.count(), 1)

        # finally check, its attributes have been saved
        choice_from_db = poll_choices[0]
        self.assertEquals(choice_from_db, choice)
        self.assertEquals(choice_from_db.choice, "doin' fine...")
        self.assertEquals(choice_from_db.votes, 3)

    def test_choice_defaults(self):
        choice = Choice()
        self.assertEquals(choice.votes, 0)


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
