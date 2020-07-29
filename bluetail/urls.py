from django.urls import include, path, reverse_lazy
from django.contrib import admin
from django.views.generic import RedirectView

import bluetail.views as views

urlpatterns = [
    path('', RedirectView.as_view(url=reverse_lazy('ocds-list')), name='home'),
    path('tenders/', views.OCDSTenderList.as_view(), name='ocds-list'),
    path('tenders/<str:pk>/', views.OCDSTenderDetailView.as_view(), name='ocds-detail'),
    path('tenders/<str:dataset>/<str:pk>/', views.OCDSTenderDetailView.as_view(), name='ocds-detail'),
    path('tenders/<str:ocid>/tenderer/<path:tenderer_id>/', views.OCDSTendererDetailView.as_view(), name='ocds-tenderer'),
    path('bods/statement/person/<str:pk>/', views.BODSPersonStatementView.as_view(), name='bods-person-statement'),
    path('bods/statement/entity/<str:pk>/', views.BODSEntityStatementView.as_view(), name='bods-entity-statement'),
    path('bods/statement/ownership/<str:pk>/', views.BODSOwnershipStatementView.as_view(), name='bods-ownership-statement'),
]
