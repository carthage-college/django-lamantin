# -*- coding: utf-8 -*-

"""URLs for all views."""
import logging

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from djauth.decorators import portal_auth_required
from lamantin.geoc.forms import CourseForm
from lamantin.geoc.forms import CourseOutcomeForm
from lamantin.geoc.forms import DocumentForm
from lamantin.geoc.models import Course


logger = logging.getLogger('debug_logfile')


@portal_auth_required(
    session_var='LAMANTIN_AUTH',
    redirect_url=reverse_lazy('access_denied'),
)
def course_form(request, step='course', cid=None):
    """GEOC workflow form. """
    course = None
    template = 'geoc/form_{0}.html'.format(step)
    forms_dict = {}
    errors = False
    user = request.user
    form_syllabus = None
    phile = None
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
        if course.syllabus():
            phile = course.syllabus()

    if request.method == 'POST':
        post = request.POST
        if step=='outcome':
            for outcome in course.outcome.all():
                if outcome.active:
                    forms = []
                    for element in outcome.elements.all():
                        slo = element.slo.get(course=course)
                        form = CourseOutcomeForm(
                            request.POST,
                            request=request,
                            prefix='slo{0}'.format(slo.id),
                            instance=slo,
                        )
                        if form.is_valid():
                            form.save()
                        else:
                            errors = True
                            logger.debug(form['description'])
                            logger.debug(form.errors)
                        forms.append(form)
                    forms_dict[outcome.get_form()] = forms
            if not errors and post.get('save_submit') and not course.save_submit:
                # set the save submit flag so user cannot update
                course.save_submit = True
                course.save()
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
                request.FILES,
                instance=course,
                use_required_attribute=settings.REQUIRED_ATTRIBUTE,
            )
            form_syllabus = DocumentForm(
                request.POST,
                request.FILES,
                instance = phile,
                use_required_attribute=settings.REQUIRED_ATTRIBUTE,
                prefix='syllabus',
            )
            if form.is_valid() and form_syllabus.is_valid():
                course = form.save(commit=False)
                course.user = user
                course.updated_by = user
                course.save()
                form.save_m2m()
                # document syllabus
                doc = form_syllabus.save(commit=False)
                doc.course = course
                if not doc.name:
                    doc.name = 'Syllabus: {0} ({1})'.format(course.title, course.number)
                doc.created_by = user
                doc.updated_by = user
                doc.save()
                doc.tags.add('Syllabus')
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
            form_syllabus = DocumentForm(
                instance = phile,
                use_required_attribute=settings.REQUIRED_ATTRIBUTE,
                prefix='syllabus',
            )
        else:
            for outcome in course.outcome.all():
                if outcome.active:
                    forms = []
                    for element in outcome.elements.all():
                        slo = element.slo.get(course=course)
                        form = CourseOutcomeForm(
                            prefix='slo{0}'.format(slo.id),
                            request=request,
                            instance=slo,
                        )
                        forms.append(form)
                    forms_dict[outcome.get_form()] = forms

    return render(
        request,
        template,
        {
            'form': form,
            'errors': errors,
            'form_syllabus': form_syllabus,
            'step': step,
            'course': course,
        },
    )
