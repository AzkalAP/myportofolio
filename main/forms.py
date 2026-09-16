from django.forms import ModelForm, TextInput, Textarea, URLInput

from main.models import Project

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "status",
            "image_path",
            "external_url",
]

        labels = {
            "title": "Nama Proyek",
            "description": "Deskripsi Proyek",
            "status": "Status Proyek",
            "image_path": "Path Gambar",
            "external_url": "URL Proyek",
        }
        
        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Portfolio Website",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Tell us about your project",
                    "rows": 3,
                }
            ),
            "image_path": TextInput(
                attrs={
                    "placeholder": "img/project.png",
                }
            ),
            "external_url": URLInput(
                attrs={
                    "placeholder": "https://github.com/username/project",
                }
            ),
        }