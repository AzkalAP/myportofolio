from django.db import migrations


PROJECTS = [
    {
        "title": "Infographic @Kastratpacil",
        "description": "An infographic project created for Kastratpacil to communicate information about sexual harassment in a clear and engaging visual format.",
        "status": "finished",
        "image_path": "img/infografis-kastratpacil.png",
        "external_url": "https://www.instagram.com/p/DXG__RDky7O/?utm_source=ig_web_copy_link&stkn=MzRlODBiNWFlZA==",
    },
    {
        "title": "Poster @diesnatalis.fasilkomui",
        "description": "A poster design project supporting the Fun Walk of Fasilkom UI's 40th dies natalis celebration.",
        "status": "finished",
        "image_path": "img/poster-diesnatalis-fasilkomui.png",
        "external_url": "https://www.instagram.com/p/DctRt80s5a_/?utm_source=ig_web_copy_link&stkn=MzRlODBiNWFlZA==",
    },
    {
        "title": "WALAS SBF Kastrat 2026",
        "description": "An ongoing Kastrat initiative that I am contributing to as part of the Kastrat team on SBF 2026.",
        "status": "ongoing",
        "image_path": "",
        "external_url": "",
    },
    {
        "title": "Poster Design for 40th Dies Natalis Fasilkom UI",
        "description": "An ongoing poster design project for the 40th Dies Natalis celebration of Fasilkom UI.",
        "status": "ongoing",
        "image_path": "",
        "external_url": "",
    },
]


def seed_projects(apps, schema_editor):
    project_model = apps.get_model("main", "Project")
    project_model.objects.bulk_create(
        project_model(**project_data) for project_data in PROJECTS
    )


def remove_projects(apps, schema_editor):
    project_model = apps.get_model("main", "Project")
    project_model.objects.filter(
        title__in=[project["title"] for project in PROJECTS]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0003_project"),
    ]

    operations = [
        migrations.RunPython(seed_projects, remove_projects),
    ]
