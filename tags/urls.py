from django.urls import path
from . import views

app_name = 'tags'

urlpatterns = [
    # For future tag-specific views
    # path('', views.TagListView.as_view(), name='list'),
    # path('<slug:slug>/', views.TagDetailView.as_view(), name='detail'),
]
