# -*- coding: utf-8 -*-

"""Admin classes for data models."""

from django.contrib import admin
from django.db import models
from lamantin.geoc.models import Annotation
from lamantin.geoc.models import Course
from lamantin.geoc.models import CourseOutcome
from lamantin.geoc.models import Document
from lamantin.geoc.models import Outcome
from lamantin.geoc.models import OutcomeCourse
from lamantin.geoc.models import OutcomeElement


class AnnotationAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'course', 'creator_name', 'created_at', 'status')
    raw_id_fields = ('created_by', 'updated_by', 'course')
    list_editable = ['status']

    def creator_name(self, obj):
        return '{0}, {1}'.format(
            obj.created_by.last_name,obj.created_by.first_name,
        )
    creator_name.admin_order_field  = 'created_by'
    creator_name.short_description = "Submitted by"


class CourseAdmin(admin.ModelAdmin):
    """Course admin class."""

    list_display = (
        'title',
        'number',
        'user',
        'created_at',
        'updated_at',
        'save_submit',
        'archive',
        'furbish',
        'approved',
        'approved_date',
    )
    list_editable = ('approved', 'archive', 'furbish', 'save_submit')
    list_per_page = 500
    save_on_top = True


class DocumentAdmin(admin.ModelAdmin):
    raw_id_fields = ('course', 'created_by', 'updated_by')
    list_display = (
        '__str__',
        'name',
        'course',
        'creator_name',
        'created_at',
    )

    def creator_name(self, obj):
        return "{0}, {1}".format(obj.created_by.last_name, obj.created_by.first_name)
    creator_name.admin_order_field  = 'created_by'
    creator_name.short_description = "Submitted by"


class OutcomeAdmin(admin.ModelAdmin):
    """Outcome admin class."""

    list_display = ('name', 'group', 'tag_list', 'active')
    list_per_page = 500
    list_editable = ['active']


class OutcomeCourseAdmin(admin.ModelAdmin):
    """Outcome course admin class."""

    list_display = ('course', 'outcome', 'approved', 'furbish')
    list_per_page = 500
    list_editable = ('approved', 'furbish')


class OutcomeElementAdmin(admin.ModelAdmin):
    """Outcome element admin class."""

    list_display = ('outcome', 'description', 'active')
    list_per_page = 500
    list_editable = ['active']


admin.site.register(OutcomeCourse)
admin.site.register(Annotation, AnnotationAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(CourseOutcome)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Outcome, OutcomeAdmin)
admin.site.register(OutcomeElement, OutcomeElementAdmin)
