from django import forms
from .models import Property, PropertyImage

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        exclude = ['agent']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'is_featured':
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

class PropertyImageForm(forms.Form):
    image1 = forms.ImageField(label='Image 1', required=False, 
               widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
    image2 = forms.ImageField(label='Image 2', required=False,
               widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
    image3 = forms.ImageField(label='Image 3', required=False,
               widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))