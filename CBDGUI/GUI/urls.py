from django.urls import path

from . import views

app_name = 'GUI'
urlpatterns = [
    path('', views.control, name='control'),
    path('display', views.display, name='display')
]
