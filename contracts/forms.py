from django import forms
from .models import Contract

class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        # Include all fields from the updated models.py, including vendor_email
        fields = ['category', 'resource', 'vendor', 'vendor_email', 'start_date', 'end_date', 'cost', 'currency', 'pdf_contract']
        
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            # Now these are normal text inputs so you can type freely instead of using dropdowns
            'resource': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Taylor & Francis Online'}),
            'vendor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Taylor & Francis'}),
            'vendor_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'vendor@example.com'}),
            
            # Dates and Numbers
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}), # Allows decimals
            
            # Select dropdowns for choices
            'currency': forms.Select(attrs={'class': 'form-select'}),
            
            
            # File upload
            'pdf_contract': forms.FileInput(attrs={'class': 'form-control'}),
        }