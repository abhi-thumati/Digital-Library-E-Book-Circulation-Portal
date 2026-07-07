from django import forms
from .models import Author
import re

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name', 'biography']
        widgets = {
            'biography': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write a brief biography of the author...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control bg-dark text-white border-secondary'
            if field_name == 'name':
                field.widget.attrs['placeholder'] = 'e.g. J.K. Rowling'

    def clean_name(self) -> str:
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("Name field is required.")
        
        # Simple name check - should have letters, dots, spaces, hyphens
        if not re.match(r'^[a-zA-Z\s\.\-\']+$', name):
            raise forms.ValidationError("Author name contains invalid characters. Use letters, spaces, dots, hyphens only.")
        
        return name.strip()
