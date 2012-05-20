from django import forms
from GenericTest.models.main import TestCaseItem

class TestCaseItemForm(forms.ModelForm):
    class Meta:
        model = TestCaseItem