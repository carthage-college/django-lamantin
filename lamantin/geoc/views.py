# -*- coding: utf-8 -*-

"""URLs for all views."""

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from djauth.decorators import portal_auth_required
from lamantin.geoc.forms import CourseForm
from lamantin.geoc.forms import CourseOutcomeForm
from lamantin.geoc.models import Course


@portal_auth_required(
    session_var='LAMANTIN_AUTH',
    redirect_url=reverse_lazy('access_denied'),
)
def course_form(request, step='course', cid=None):
    """GEOC workflow form. """
    course = None
    template = 'geoc/form_{0}.html'.format(step)
    forms_dict = {}
    user = request.user
    if cid:
        course = Course.objects.get(pk=cid)
        if course.save_submit:
            messages.add_message(
                request,
                messages.WARNING,
                """
                    The course you attempted to edit is complete.
                    The GEOC committe will review your course and report back to you presently.
                """,
                extra_tags='alert-warning',
            )
            return HttpResponseRedirect(reverse_lazy('dashboard_home'))
        elif user != course.user:
            messages.add_message(
                request,
                messages.WARNING,
                "The course you attempted to edit is unavailable.",
                extra_tags='alert-warning',
            )
            return HttpResponseRedirect(reverse_lazy('dashboard_home'))

    if request.method == 'POST':
        post = request.POST
        if step=='outcome':
            if post.get('save_submit') and not course.save_submit:
                # set the save submit flag so user cannot update
                course.save_submit = True
                course.save()
            for outcome in course.outcome.all():
                forms = []
                for element in outcome.elements.all():
                    form = CourseOutcomeForm(
                        request.POST,
                        prefix='slo{0}'.format(element.slo.id),
                        instance=element.slo,
                    )
                    if form.is_valid():
                        form.save()
                    forms.append(form)
                forms_dict[outcome.get_form()] = forms
            messages.add_message(
                request,
                messages.SUCCESS,
                "Step 2 is complete. The GEOC committe will review your course and report back to you presently.",
                extra_tags='alert-success',
            )
            return HttpResponseRedirect(reverse_lazy('dashboard_home'))
        else:
            form = CourseForm(
                request.POST,
                instance=course,
                use_required_attribute=settings.REQUIRED_ATTRIBUTE,
            )
            if form.is_valid():
                course = form.save(commit=False)
                course.user = user
                course.updated_by = user
                course.save()
                form.save_m2m()
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    "Step 1 is complete. Please complete the outcomes below.",
                    extra_tags='alert-success',
                )
                return HttpResponseRedirect(
                    reverse_lazy('course_update', args=['outcome', course.id]),
                )
    else:
        if step == 'course':
            form = CourseForm(
                instance=course,
                use_required_attribute=settings.REQUIRED_ATTRIBUTE,
            )
        else:
            for outcome in course.outcome.all():
                forms = []
                for element in outcome.elements.all():
                    form = CourseOutcomeForm(prefix='slo{0}'.format(element.slo.id), instance=element.slo)
                    forms.append(form)
                forms_dict[outcome.get_form()] = forms

    return render(
        request,
        template,
        {'form': form, 'step': step, 'course': course},
    )
