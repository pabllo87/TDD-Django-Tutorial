from django.views.generic import TemplateView, DetailView, ListView
from polls.models import Poll


class HomeView(ListView):
    template_name = 'home.html'

    model = Poll
    context_object_name = "polls"
    #queryset = Poll.objests.all()


class PollView(DetailView):
    template_name = 'poll.html'

    context_object_name = 'poll'
    model = Poll
