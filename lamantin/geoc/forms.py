# -*- coding: utf-8 -*-

from django import forms
from lamantin.geoc.models import Course
from lamantin.geoc.models import CourseOutcome
from lamantin.geoc.models import Document
from lamantin.geoc.models import Outcome


class Dupes:
    """Data model for managing form validation for outcomes."""

    def __init__(self):
        """Initialize the object with defauls."""
        self.tags = {
            'Abilities': {'outcomes': [], 'check': False},
            'Explorations': {'outcomes': [], 'check': False},
            'Perspectives': {'outcomes': [], 'check': False},
        }
        self.error = []

    def get_outcomes(self):
        """Fetch the outcome objects for each tag."""
        for tag, outcomes in self.tags.items():
            self.tags[tag]['outcomes'] = Outcome.objects.filter(tags__name__in=[tag])

    def check(self, outcomes):
        """Check for dupes."""
        for outcome in outcomes:
            for tag, slo in self.tags.items():
                if outcome in slo['outcomes']:
                    if not slo['check']:
                        slo['check'] = True
                    else:
                        if tag not in self.error:
                            self.error.append(tag)


class CourseForm(forms.ModelForm):
    """GEOC course form."""

    outcome = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(),
        queryset=Outcome.objects.all(),
        required=True,
    )

    class Meta:
        model = Course
        fields = ('title', 'number', 'outcome')

    def clean(self):
        """Form validation."""
        cd = self.cleaned_data
        dupes = Dupes()
        dupes.get_outcomes()
        dupes.check(cd['outcome'])
        if dupes.error:
             self.add_error('outcome', dupes.error)
        return cd


class CourseOutcomeForm(forms.ModelForm):
    """GEOC specific outcome form."""

    class Meta:
        model = CourseOutcome
        fields = ('description',)


class DocumentForm(forms.ModelForm):
    """GEOC documents."""

    class Meta:
        model = Document
        fields = ['phile']
