from django import forms
from .models import Property, PropertyImage

class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

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
    images = MultipleFileField(
        label='Property Images',
        required=False,
        widget=MultipleFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'id': 'propertyImages'
        }),
        help_text='Select up to 7 images for the property'
    )
    
    def clean_images(self):
        files = self.cleaned_data.get('images')
        if not files:
            return files
            
        if not isinstance(files, list):
            files = [files]
        
        if len(files) > 7:
            raise forms.ValidationError('You can upload a maximum of 7 images.')
        
        for file in files:
            if hasattr(file, 'content_type') and not file.content_type.startswith('image/'):
                raise forms.ValidationError(f'{file.name} is not a valid image file.')
            
            if hasattr(file, 'size') and file.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError(f'{file.name} is too large. Maximum size is 5MB.')
        
        return files