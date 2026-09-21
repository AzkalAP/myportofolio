from django.forms import DateTimeInput, ModelForm, TextInput, Textarea, URLInput

from main.models import Experience, Project


class ExperienceForm(ModelForm):
    class Meta:
        model = Experience
        fields = [
            "title",
            "description",
            "category",
            "thumbnail",
            "ended_at",
        ]

        labels = {
            "title": "Experience Title",
            "description": "Description",
            "category": "Category",
            "thumbnail": "Thumbnail URL",
            "ended_at": "End Date",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Organization Staff",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Describe your experience",
                    "rows": 3,
                }
            ),
            "thumbnail": URLInput(
                attrs={
                    "placeholder": "https://example.com/image.png",
                }
            ),
            "ended_at": DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={
                    "type": "datetime-local",
                },
            ),
        }

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