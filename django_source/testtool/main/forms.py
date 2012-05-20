from django import forms
from testtool.models import TestCaseItem

class TestCaseItemForm(forms.ModelForm):
    class Meta:
        model = TestCaseItem