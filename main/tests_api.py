import uuid

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Experience, Project


class ExperienceAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="experience-owner",
            password="test-password",
            email="experience-owner@example.com",
        )
        self.visitor = User.objects.create_user(
            username="experience-visitor",
            password="test-password",
            email="experience-visitor@example.com",
        )
        self.editor = User.objects.create_user(
            username="experience-editor",
            password="test-password",
        )
        self.editor.groups.add(Group.objects.create(name="Editor"))
        self.experience = Experience.objects.create(
            title="API Experience",
            description="A description",
            category="research",
        )
        self.initial_experience_count = Experience.objects.count()
        self.list_url = reverse("api:experience-list")
        self.detail_url = reverse(
            "api:experience-detail",
            args=[self.experience.pk],
        )
        self.star_url = reverse(
            "api:experience-star",
            args=[self.experience.pk],
        )
        self.payload = {
            "title": "New experience",
            "description": "Built a useful application",
            "category": "internship",
            "thumbnail": "https://example.com/image.png",
            "ended_at": None,
        }

    def test_public_list_detail_and_search(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item = next(
            data
            for data in response.data
            if data["id"] == str(self.experience.pk)
        )
        self.assertEqual(item["title"], "API Experience")
        self.assertEqual(item["category_display"], "Research")
        self.assertFalse(item["is_starred"])
        self.assertEqual(item["star_count"], 0)
        self.assertNotIn("starred_by", item)
        self.assertNotIn("email", item)
        self.assertEqual(
            self.client.get(self.detail_url).status_code,
            status.HTTP_200_OK,
        )

        filtered = self.client.get(self.list_url, {"title": "api experience"})
        self.assertEqual(
            [item["id"] for item in filtered.data],
            [str(self.experience.pk)],
        )
        empty = self.client.get(self.list_url, {"title": "not-found"})
        self.assertEqual(empty.data, [])

    def test_missing_experience_returns_404(self):
        missing_url = reverse("api:experience-detail", args=[uuid.uuid4()])
        self.assertEqual(
            self.client.get(missing_url).status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_anonymous_and_regular_users_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(
                self.client.post(self.list_url, self.payload, format="json").status_code,
                status.HTTP_403_FORBIDDEN,
            )
            self.assertEqual(
                self.client.patch(
                    self.detail_url,
                    {"title": "Changed"},
                    format="json",
                ).status_code,
                status.HTTP_403_FORBIDDEN,
            )
            self.assertEqual(
                self.client.delete(self.detail_url).status_code,
                status.HTTP_403_FORBIDDEN,
            )

        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "API Experience")
        self.assertEqual(
            Experience.objects.count(),
            self.initial_experience_count,
        )

    def test_editor_can_patch_but_cannot_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)
        response = self.client.patch(
            self.detail_url,
            {"title": "Editor updated this"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Editor updated this")
        self.assertEqual(
            self.client.post(self.list_url, self.payload, format="json").status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            self.client.delete(self.detail_url).status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertTrue(Experience.objects.filter(pk=self.experience.pk).exists())
        self.assertEqual(
            Experience.objects.count(),
            self.initial_experience_count,
        )

    def test_owner_can_create_update_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_id = response.data["id"]
        created_url = reverse("api:experience-detail", args=[created_id])
        self.assertTrue(Experience.objects.filter(pk=created_id).exists())

        response = self.client.put(created_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(
            created_url,
            {"title": "Owner updated this"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Owner updated this")

        response = self.client.delete(created_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(Experience.objects.filter(pk=created_id).exists())

    def test_serializer_validates_and_cleans_text(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            self.list_url,
            {**self.payload, "title": "<script></script>"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)

        response = self.client.post(
            self.list_url,
            {
                **self.payload,
                "title": "<b>Clean title</b>",
                "description": "<p>Clean description</p>",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Clean title")
        self.assertEqual(response.data["description"], "Clean description")

    def test_star_requires_login_and_toggles_for_authenticated_users(self):
        response = self.client.post(self.star_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)

        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(
            client.login(
                username="experience-owner",
                password="test-password",
            )
        )
        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            Experience.objects.count(),
            self.initial_experience_count,
        )

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(
            client.login(
                username="experience-owner",
                password="test-password",
            )
        )
        page = client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value
        response = client.post(
            self.list_url,
            self.payload,
            format="json",
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class ProjectAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner",
            password="test-password",
            email="owner@example.com",
        )
        self.visitor = User.objects.create_user(
            username="visitor",
            password="test-password",
            email="visitor@example.com",
        )
        self.editor = User.objects.create_user(
            username="editor",
            password="test-password",
        )
        self.editor.groups.add(Group.objects.create(name="Editor"))
        self.project = Project.objects.create(
            title="Portfolio",
            description="My website",
            status="finished",
            image_path="img/portfolio.png",
            external_url="https://example.com/",
        )
        self.initial_project_count = Project.objects.count()
        self.list_url = reverse("api:project-list")
        self.detail_url = reverse("api:project-detail", args=[self.project.pk])
        self.star_url = reverse("api:project-star", args=[self.project.pk])
        self.payload = {
            "title": "New project",
            "description": "A useful app",
            "status": "ongoing",
            "image_path": "img/new-project.png",
            "external_url": "https://example.com/new-project",
        }

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project_data = next(
            item for item in response.data if item["id"] == self.project.pk
        )
        self.assertFalse(project_data["is_starred"])
        self.assertNotIn("fields", project_data)
        self.assertNotIn("starred_by", project_data)
        self.assertEqual(project_data["starred_by_names"], "")
        self.assertEqual(
            self.client.get(self.detail_url).status_code,
            status.HTTP_200_OK,
        )

    def test_search_and_empty_results(self):
        response = self.client.get(self.list_url, {"title": "PORT"})
        self.assertEqual(len(response.data), 1)

        response = self.client.get(self.list_url, {"title": "not-found"})
        self.assertEqual(response.data, [])

    def test_missing_project(self):
        url = reverse("api:project-detail", args=[self.project.pk + 1000])
        self.assertEqual(
            self.client.get(url).status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_guest_and_regular_user_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(
                self.client.post(self.list_url, self.payload, format="json").status_code,
                status.HTTP_403_FORBIDDEN,
            )
            self.assertEqual(
                self.client.patch(
                    self.detail_url,
                    {"title": "Changed"},
                    format="json",
                ).status_code,
                status.HTTP_403_FORBIDDEN,
            )
            self.assertEqual(
                self.client.delete(self.detail_url).status_code,
                status.HTTP_403_FORBIDDEN,
            )

        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Portfolio")
        self.assertEqual(Project.objects.count(), self.initial_project_count)

    def test_owner_can_create(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(self.list_url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Project.objects.filter(pk=response.data["id"]).exists())

    def test_validation_rejects_empty_titles_markup_and_invalid_urls(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in (
            ({"title": "   "}, "title"),
            ({"title": "<img src=x onerror=alert(1)>"}, "title"),
            ({"external_url": "javascript:alert(1)"}, "external_url"),
        ):
            response = self.client.post(
                self.list_url,
                {**self.payload, **changes},
                format="json",
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)

        self.assertEqual(Project.objects.count(), self.initial_project_count)

    def test_patch_put_and_delete(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(
            self.detail_url,
            {"title": "Changed"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.description, "My website")

        response = self.client.put(
            self.detail_url,
            {"title": "Incomplete"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(
            self.client.post(self.star_url).status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.client.force_authenticate(user=self.visitor)

        response = self.client.post(self.star_url)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)

        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

    def test_computed_star_fields_are_read_only_and_names_are_limited_to_usernames(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(
            self.list_url,
            {
                **self.payload,
                "star_count": 99,
                "is_starred": True,
                "starred_by": [self.visitor.pk],
                "starred_by_names": self.visitor.username,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["starred_by_names"], "")
        self.assertNotIn(self.visitor.email, str(response.data))

        self.project.starred_by.add(self.visitor)
        detail_response = self.client.get(self.detail_url)
        self.assertEqual(detail_response.data["starred_by_names"], "visitor")

    def test_editor_can_update_but_cannot_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)

        response = self.client.patch(
            self.detail_url,
            {"title": "Editor update"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Editor update")

        self.assertEqual(
            self.client.post(self.list_url, self.payload, format="json").status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            self.client.delete(self.detail_url).status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_star_is_allowed_for_regular_editor_and_owner(self):
        for user in (self.visitor, self.editor, self.owner):
            self.client.force_authenticate(user=user)
            response = self.client.post(self.star_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.data["is_starred"])
            self.client.post(self.star_url)

    def test_wrong_method(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(
            self.client.delete(self.list_url).status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(
            client.login(username="owner", password="test-password")
        )

        response = client.post(self.list_url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Project.objects.count(), self.initial_project_count)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(
            client.login(username="owner", password="test-password")
        )
        page = client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value

        response = client.post(
            self.list_url,
            self.payload,
            format="json",
            HTTP_X_CSRFTOKEN=token,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
