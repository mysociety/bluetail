from django.urls import include, path
from django.contrib import admin

import bluetail.views as views

urlpatterns = [
    path('test/', views.test_view, name='test-view'),
    path('tenderer/', views.tenderer_view, name='example-tenderer'),
    path('tender/', views.tender_view, name='example-tender'),
    path('', views.tenders_view, name='example-tenders'),
]
