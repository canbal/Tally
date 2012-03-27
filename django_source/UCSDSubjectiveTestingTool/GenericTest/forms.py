from django import forms
from GenericTest.models import TestCaseItem

class TestCaseItemForm(forms.ModelForm):
    class Meta:
        model = TestCaseItem