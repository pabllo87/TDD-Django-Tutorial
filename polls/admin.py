# -*- coding: utf-8 *-*
from polls.models import Choice, Poll
from django.contrib import admin


class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 3


class PollAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]

admin.site.register(Poll, PollAdmin)
