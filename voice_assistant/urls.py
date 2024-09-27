from django.urls import path
from . import views

urlpatterns = [
    path('1', views.index1, name='index1'),
    path('2', views.index2, name='index2'),
    path('3', views.index3, name='index3'),
    path('process_transcription/', views.process_transcription, name='process_transcription'),
]