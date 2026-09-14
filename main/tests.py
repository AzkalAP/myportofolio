from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

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