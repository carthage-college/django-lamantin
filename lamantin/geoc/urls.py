# -*- coding: utf-8 -*-

"""URLs for all views."""

from django.urls import path
from django.urls import reverse_lazy
from django.views.generic import RedirectView
from lamantin.geoc import views


urlpatterns = [
    path(
        'form/<str:step>/<int:cid>/update/',
        views.course_form,
        name='update',
    ),
    path('form/', views.course_form, name='course'),
    # home: redirect to dashboard
    path('', RedirectView.as_view(url=reverse_lazy('course'))),
]
