from django import forms
from .models import Book, Genre
from library.authors.models import Author

class GenreForm(forms.ModelForm):
    class Meta:
        model = Genre
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write a brief description of the genre...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control bg-dark text-white border-secondary'
            if field_name == 'name':
                field.widget.attrs['placeholder'] = 'e.g. Fantasy, Biography'

    def clean_name(self) -> str:
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("Genre name is required.")
        return name.strip()

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title', 'authors', 'genres', 'isbn', 'description', 
            'publication_date', 'publisher', 'cover_image', 'total_copies'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write a synopsis or summary...'}),
            'publication_date': forms.DateInput(attrs={'type': 'date'}),
            'authors': forms.SelectMultiple(),
            'genres': forms.SelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ['authors', 'genres']:
                field.widget.attrs['class'] = 'form-control bg-dark text-white border-secondary'
            else:
                field.widget.attrs['class'] = 'form-select bg-dark text-white border-secondary'
            
            # Placeholders
            if field_name == 'title':
                field.widget.attrs['placeholder'] = 'e.g. Harry Potter and the Philosopher\'s Stone'
            elif field_name == 'isbn':
                field.widget.attrs['placeholder'] = 'e.g. 978-0747532699'
            elif field_name == 'publisher':
                field.widget.attrs['placeholder'] = 'e.g. Bloomsbury Publishing'
            elif field_name == 'total_copies':
                field.widget.attrs['placeholder'] = 'Number of copies'
                
        # Populate choices dynamically
        self.fields['authors'].queryset = Author.objects.all()
        self.fields['genres'].queryset = Genre.objects.all()

    def clean_total_copies(self) -> int:
        total_copies = self.cleaned_data.get('total_copies')
        if total_copies is not None and total_copies < 0:
            raise forms.ValidationError("Total copies cannot be negative.")
        return total_copies
