from django.db import migrations


EXPERIENCE_RECORDS = [
    {
        "title": "SBF Kastrat Staff",
        "description": "Contributing to the Kastrat staff team through organizational-related work as SBF staff in Kastrat Fasilkom UI.",
        "category": "organization",
    },
    {
        "title": "2nd Deputy of Kastrat BEM Fasilkom",
        "description": "Supporting the Kastrat division's coordination and helping guide its organizational programs and responsibilities.",
        "category": "organization",
    },
    {
        "title": "Public Relations Staff",
        "description": "Supporting communication and content design as part of the public relations team.",
        "category": "organization",
    },
]


def seed_experience(apps, schema_editor):
    experience_model = apps.get_model("main", "Experience")
    for experience_data in EXPERIENCE_RECORDS:
        experience_model.objects.get_or_create(
            title=experience_data["title"],
            defaults=experience_data,
        )


def remove_experience(apps, schema_editor):
    experience_model = apps.get_model("main", "Experience")
    experience_model.objects.filter(
        title__in=[experience["title"] for experience in EXPERIENCE_RECORDS]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0004_seed_projects"),
    ]

    operations = [
        migrations.RunPython(seed_experience, remove_experience),
    ]
