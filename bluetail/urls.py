from django.urls import include, path
from django.contrib import admin

import bluetail.views as views

urlpatterns = [
    path('test/', views.test_view, name='test-view'),
]