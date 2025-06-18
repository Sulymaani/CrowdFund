from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Tag


# These views are defined but not yet hooked up in urls.py
# They will be activated when tag-specific pages are needed

class TagListView(ListView):
    """
    Display a list of all tags.
    """
    model = Tag
    context_object_name = 'tags'
    template_name = 'tags/list.html'


class TagDetailView(DetailView):
    """
    Display a single tag and associated content.
    """
    model = Tag
    context_object_name = 'tag'
    template_name = 'tags/detail.html'
    slug_url_kwarg = 'slug'
