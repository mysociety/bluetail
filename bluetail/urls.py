from django.urls import include, path
from django.contrib import admin

import bluetail.views as views

urlpatterns = [
    path('test/', views.test_view, name='test-view'),
    path('tenderer/', views.tenderer_view, name='example-tenderer'),
    path('tender/', views.tender_view, name='example-tender'),
    path('', views.tenders_view, name='example-tenders'),
    path('ocds/<str:pk>/', views.OCDSDetailView.as_view(), name='detail'),
    path('bods/statement/person/<str:pk>/', views.BODSPersonStatementView.as_view(), name='bods-person-statement'),
    path('bods/statement/entity/<str:pk>/', views.BODSEntityStatementView.as_view(), name='bods-entity-statement'),
    path('bods/statement/ownership/<str:pk>/', views.BODSOwnershipStatementView.as_view(), name='bods-ownership-statement'),
]
