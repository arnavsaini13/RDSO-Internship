from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Document


class DocumentUploadForm(forms.ModelForm):
    """Form for uploading PDF documents"""
    
    class Meta:
        model = Document
        fields = ['title', 'department', 'category', 'description', 'pdf_file']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Document Title',
                'required': True
            }),
            'department': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'category': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Description (Optional)',
                'rows': 3
            }),
            'pdf_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf',
                'required': True
            }),
        }
    
    def clean_pdf_file(self):
        pdf_file = self.cleaned_data.get('pdf_file')
        if pdf_file:
            if not pdf_file.name.endswith('.pdf'):
                raise forms.ValidationError("Only PDF files are allowed.")
            if pdf_file.size > 10 * 1024 * 1024:  # 10 MB
                raise forms.ValidationError("PDF file size must be less than 10 MB.")
        return pdf_file


class DocumentSearchForm(forms.Form):
    """Form for searching documents"""
    SEARCH_TYPE_CHOICES = [
        ('ALL', 'All Fields'),
        ('BARCODE', 'By Barcode'),
        ('TITLE', 'By Title'),
        ('CONTENT', 'By Content'),
        ('DEPARTMENT', 'By Department'),
        ('CATEGORY', 'By Category'),
    ]
    
    search_query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search documents...'
        })
    )
    search_type = forms.ChoiceField(
        choices=SEARCH_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    department = forms.ChoiceField(
        choices=[('', 'All Departments')] + list(Document._meta.get_field('department').choices),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    category = forms.ChoiceField(
        choices=[('', 'All Categories')] + list(Document._meta.get_field('category').choices),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )


class DocumentUpdateStatusForm(forms.Form):
    """Form for updating document status"""
    STATUS_CHOICES = Document._meta.get_field('status').choices
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    remarks = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Add remarks (optional)',
            'rows': 3
        })
    )
