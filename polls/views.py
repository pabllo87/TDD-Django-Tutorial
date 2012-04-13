from django.views.generic import DetailView, ListView
from polls.models import Poll, Choice
from polls.forms import PollVoteForm
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect


class HomeView(ListView):
    template_name = 'home.html'

    model = Poll
    context_object_name = "polls"
    #queryset = Poll.objests.all()


class PollView(DetailView):
    template_name = 'poll.html'

    context_object_name = 'poll'
    model = Poll

    def __init__(self, **kwargs):
        super(PollView, self).__init__(**kwargs)
        #self.post = self.request.POST.copy()

    def post(self, request, *args, **kwargs):
        choice = Choice.objects.get(id=self.request.POST['vote'])
        choice.votes += 1
        choice.save()
        return HttpResponseRedirect(reverse('poll_views_poll', args=[self.kwargs['pk'], ]))

    def get_object(self):
        self.poll = super(PollView, self).get_object()
        return self.poll

    def get_context_data(self, **kwargs):
        context = super(PollView, self).get_context_data(**kwargs)
        context['form'] = PollVoteForm(poll=self.poll)
        return context
