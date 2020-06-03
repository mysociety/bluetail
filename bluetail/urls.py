from django.urls import include, path, reverse_lazy
from django.contrib import admin
from django.views.generic import RedirectView

import bluetail.views as views

urlpatterns = [
    path('test/', views.test_view, name='test-view'),
    path('tenderer/', views.tenderer_view, name='example-tenderer'),
    path('tender/', views.tender_view, name='example-tender'),
    # path('', views.tenders_view, name='example-tenders'),
    path('', RedirectView.as_view(url=reverse_lazy('ocds-list')), name='example-tenders'),

    path('ocds/', views.OCDSList.as_view(), name='ocds-list'),
    path('ocds/<str:pk>/', views.OCDSTenderDetailView.as_view(), name='ocds-detail'),
    # path('ocds/<str:ocid>/<path:tenderer_id>/', views.OCDSTendererDetailView.as_view(), name='ocds-tenderer'),
    path('ocds/<str:ocid>/tenderer/<path:tenderer_id>/', views.OCDSTendererDetailView.as_view(), name='ocds-tenderer'),
    path('bods/statement/person/<str:pk>/', views.BODSPersonStatementView.as_view(), name='bods-person-statement'),
    path('bods/statement/entity/<str:pk>/', views.BODSEntityStatementView.as_view(), name='bods-entity-statement'),
    path('bods/statement/ownership/<str:pk>/', views.BODSOwnershipStatementView.as_view(), name='bods-ownership-statement'),
]
