from django import forms
from GenericTest.main.models import TestCaseItem

class TestCaseItemForm(forms.ModelForm):
    class Meta:
        model = TestCaseItem