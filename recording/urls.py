from django.urls import path
from . import views

app_name = 'recording'

urlpatterns = [
    path('', views.RecordingView.as_view(), name='recording-list'),
]