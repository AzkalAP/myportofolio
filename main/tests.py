from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.forms import ExperienceForm
from main.models import Experience, Project


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="SBF Kastrat Staff - BEM Fasilkom UI",
            description="Contributing to the Kastrat staff team through organizational-related work as SBF staff in Kastrat Fasilkom UI.",
            category="organization",
        )
        self.finished_project = Project.objects.create(
            title="Infographic @Kastratpacil",
            description="A finished infographic project.",
            status="finished",
            image_path="img/infografis-kastratpacil.png",
            external_url="https://www.instagram.com/p/DXG__RDky7O/",
        )
        self.ongoing_project = Project.objects.create(
            title="WALAS SBF Kastrat 2026",
            description="An ongoing Kastrat initiative.",
            status="ongoing",
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/a-page-that-does-not-exist/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        # Menyesuaikan dengan title dan category yang baru
        self.assertEqual(str(self.experience), "SBF Kastrat Staff - BEM Fasilkom UI")
        self.assertEqual(self.experience.category, "organization")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        
        self.assertContains(response, "Organization")
        self.assertContains(response, "Ongoing")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "No experience has been added yet.")

    def test_experience_json_endpoint(self):
        response = self.client.get(reverse("main:get_experience_json"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertContains(response, self.experience.title)

    def test_experience_page_uses_json_data(self):
        response = self.client.get(reverse("main:show_experience"))

        experience_ids = [experience.pk for experience in response.context["experience_list"]]
        self.assertIn(self.experience.pk, experience_ids)
        self.assertContains(response, self.experience.title)

    def test_experience_page_has_management_controls(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, reverse("main:create_experience"))
        self.assertContains(
            response,
            reverse("main:update_experience", args=[self.experience.pk]),
        )
        self.assertContains(
            response,
            reverse("main:delete_experience", args=[self.experience.pk]),
        )

    def test_experience_create_form_page(self):
        response = self.client.get(reverse("main:create_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience_form.html")
        self.assertContains(response, "Add New Experience")

    def test_experience_update_form_page(self):
        response = self.client.get(
            reverse("main:update_experience", args=[self.experience.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience_form.html")
        self.assertContains(response, "Edit Experience")
        self.assertContains(response, self.experience.title)

    def test_create_experience(self):
        response = self.client.post(
            reverse("main:create_experience"),
            {
                "title": "Teaching Assistant",
                "description": "Helped students learn programming.",
                "category": "research",
                "thumbnail": "",
                "ended_at": "",
            },
        )

        self.assertRedirects(response, reverse("main:show_experience"))
        self.assertTrue(Experience.objects.filter(title="Teaching Assistant").exists())

    def test_create_experience_requires_valid_data(self):
        form = ExperienceForm(
            {
                "title": "",
                "description": "Missing title.",
                "category": "research",
                "thumbnail": "",
                "ended_at": "",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)
        self.assertFalse(Experience.objects.filter(title="").exists())

    def test_update_experience(self):
        response = self.client.post(
            reverse("main:update_experience", args=[self.experience.pk]),
            {
                "title": "Updated Experience",
                "description": "Updated description.",
                "category": "volunteer",
                "thumbnail": "",
                "ended_at": "",
            },
        )

        self.assertRedirects(response, reverse("main:show_experience"))
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Updated Experience")
        self.assertEqual(self.experience.category, "volunteer")

    def test_delete_experience(self):
        response = self.client.post(
            reverse("main:delete_experience", args=[self.experience.pk])
        )

        self.assertRedirects(response, reverse("main:show_experience"))
        self.assertFalse(Experience.objects.filter(pk=self.experience.pk).exists())

    def test_delete_experience_requires_post(self):
        response = self.client.get(
            reverse("main:delete_experience", args=[self.experience.pk])
        )

        self.assertEqual(response.status_code, 405)

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Completed")
        self.assertNotContains(response, "Ongoing")

    def test_projects_url_is_accessible(self):
        response = self.client.get(reverse("main:show_projects"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects.html")

    def test_update_project_form_page(self):
        response = self.client.get(
            reverse("main:update_project", args=[self.finished_project.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects_form.html")
        self.assertTrue(response.context["is_edit"])
        self.assertContains(response, self.finished_project.title)

    def test_update_project(self):
        response = self.client.post(
            reverse("main:update_project", args=[self.finished_project.pk]),
            {
                "title": "Updated Project",
                "description": "Updated project description.",
                "status": "ongoing",
                "image_path": "img/updated-project.png",
                "external_url": "https://example.com/updated-project",
            },
        )

        self.assertRedirects(response, reverse("main:show_projects"))
        self.finished_project.refresh_from_db()
        self.assertEqual(self.finished_project.title, "Updated Project")
        self.assertEqual(self.finished_project.status, "ongoing")

    def test_update_project_requires_valid_data(self):
        response = self.client.post(
            reverse("main:update_project", args=[self.finished_project.pk]),
            {
                "title": "",
                "description": "Missing title.",
                "status": "finished",
                "image_path": "",
                "external_url": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.finished_project.refresh_from_db()
        self.assertEqual(self.finished_project.title, "Infographic @Kastratpacil")

    def test_update_nonexistent_project_returns_404(self):
        response = self.client.get(reverse("main:update_project", args=[999999]))

        self.assertEqual(response.status_code, 404)

    def test_project_model(self):
        self.assertEqual(str(self.finished_project), "Infographic @Kastratpacil")
        self.assertTrue(self.finished_project.is_finished)
        self.assertFalse(self.ongoing_project.is_finished)

    def test_projects_page_renders_database_projects(self):
        response = self.client.get(reverse("main:show_projects"))

        self.assertContains(response, self.finished_project.title)
        self.assertContains(response, self.finished_project.description)
        self.assertContains(response, self.ongoing_project.title)
        self.assertContains(response, "Finished")
        self.assertContains(response, "In progress")

    def test_finished_project_has_image_and_external_link(self):
        response = self.client.get(reverse("main:show_projects"))

        self.assertContains(response, '/static/img/infografis-kastratpacil.png')
        self.assertContains(response, "instagram.com/p/DXG__RDky7O/")
        self.assertContains(response, 'alt="Image for Infographic @Kastratpacil"')

    def test_ongoing_project_has_no_image(self):
        response = self.client.get(reverse("main:show_projects"))

        self.assertNotContains(
            response,
            'alt="Image for WALAS SBF Kastrat 2026"',
        )

    def test_empty_projects_page(self):
        Project.objects.all().delete()
        response = self.client.get(reverse("main:show_projects"))

        self.assertContains(response, "No projects have been added yet.")