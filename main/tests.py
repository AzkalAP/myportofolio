from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.forms import ExperienceForm, ProjectForm
from main.models import Experience, Project


class MainTest(TestCase):
    def setUp(self):
        self.member = User.objects.create_user(
            username="member",
            password="StrongPass123!",
        )
        self.owner = User.objects.create_superuser(
            username="owner",
            email="owner@example.com",
            password="StrongPass123!",
        )
        self.editor = User.objects.create_user(
            username="editor",
            password="StrongPass123!",
        )
        editor_group = Group.objects.create(name="Editor")
        self.editor.groups.add(editor_group)
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
        self.assertContains(response, "No active login session / Cookie not found")

    def test_auth_navigation_changes_with_login_state(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertContains(response, reverse("main:login"))
        self.assertContains(response, reverse("main:register"))
        self.assertNotContains(response, reverse("main:logout"))

        self.client.force_login(self.member)
        response = self.client.get(reverse("main:show_main"))

        self.assertContains(response, "member")
        self.assertContains(response, reverse("main:logout"))
        self.assertNotContains(response, reverse("main:register"))

    def test_register_creates_user_and_shows_message(self):
        response = self.client.post(
            reverse("main:register"),
            {
                "username": "new-member",
                "password1": "SecureExamplePass123!",
                "password2": "SecureExamplePass123!",
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("main:login"))
        self.assertContains(response, "Account created successfully")
        created_user = User.objects.get(username="new-member")
        self.assertTrue(created_user.check_password("SecureExamplePass123!"))

    def test_register_displays_validation_errors(self):
        response = self.client.post(
            reverse("main:register"),
            {
                "username": "new-member",
                "password1": "SecureExamplePass123!",
                "password2": "DifferentExamplePass123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("password2", response.context["form"].errors)
        self.assertFalse(User.objects.filter(username="new-member").exists())

    def test_login_sets_cookie_and_session(self):
        response = self.client.post(
            reverse("main:login"),
            {"username": "member", "password": "StrongPass123!"},
        )

        self.assertRedirects(response, reverse("main:show_main"))
        self.assertIn("last_login", response.cookies)
        self.assertIn("sessionid", response.cookies)
        profile_response = self.client.get(reverse("main:show_main"))
        self.assertContains(
            profile_response,
            response.cookies["last_login"].value,
        )

    def test_login_rejects_invalid_credentials(self):
        response = self.client.post(
            reverse("main:login"),
            {"username": "member", "password": "wrong-password"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a correct username and password")

    def test_logout_clears_login_cookie_and_session(self):
        self.client.force_login(self.member)
        self.client.cookies["last_login"] = "2026-09-28 12:00:00"

        response = self.client.get(reverse("main:logout"))

        self.assertRedirects(response, reverse("main:show_main"))
        self.assertEqual(response.cookies["last_login"]["max-age"], 0)
        self.assertEqual(response.cookies["sessionid"]["max-age"], 0)
        profile_response = self.client.get(reverse("main:show_main"))
        self.assertContains(profile_response, "No active login session / Cookie not found")
        self.assertNotContains(profile_response, "member</span>")

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/a-page-that-does-not-exist/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        # Menyesuaikan dengan title dan category yang baru
        self.assertEqual(str(self.experience), "SBF Kastrat Staff - BEM Fasilkom UI")
        self.assertEqual(self.experience.category, "organization")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_can_be_starred_by_users(self):
        self.experience.starred_by.add(self.member)

        self.assertEqual(self.experience.starred_by.count(), 1)
        self.assertTrue(
            self.member.starred_experiences.filter(pk=self.experience.pk).exists()
        )

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

    def test_experience_json_contains_star_state_without_user_identities(self):
        self.experience.starred_by.add(self.member)

        anonymous_response = self.client.get(reverse("main:get_experience_json"))
        anonymous_item = next(
            item
            for item in anonymous_response.json()
            if item["pk"] == str(self.experience.pk)
        )
        self.assertEqual(anonymous_item["fields"]["star_count"], 1)
        self.assertFalse(anonymous_item["fields"]["is_starred"])
        self.assertNotIn("starred_by", anonymous_item["fields"])
        self.assertNotContains(anonymous_response, self.member.username)

        self.client.force_login(self.member)
        member_response = self.client.get(reverse("main:get_experience_json"))
        member_item = next(
            item
            for item in member_response.json()
            if item["pk"] == str(self.experience.pk)
        )
        self.assertEqual(member_item["fields"]["star_count"], 1)
        self.assertTrue(member_item["fields"]["is_starred"])

    def test_experience_json_filters_by_title(self):
        response = self.client.get(
            reverse("main:get_experience_json"),
            {"title": "Kastrat"},
        )

        titles = [item["fields"]["title"] for item in response.json()]
        self.assertTrue(titles)
        self.assertTrue(all("Kastrat" in title for title in titles))

    def test_ajax_create_experience_returns_created_record(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("main:create_experience_ajax"),
            {
                "title": "Teaching Assistant",
                "description": "Helped students learn programming.",
                "category": "research",
                "thumbnail": "",
                "ended_at": "",
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Experience.objects.filter(title="Teaching Assistant").exists()
        )

    def test_ajax_create_experience_returns_validation_errors(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("main:create_experience_ajax"),
            {
                "title": "<b></b>",
                "description": "Missing a usable title.",
                "category": "research",
                "thumbnail": "",
                "ended_at": "",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("title", response.json()["errors"])

    def test_ajax_create_experience_requires_owner_permission(self):
        create_url = reverse("main:create_experience_ajax")
        data = {
            "title": "Unauthorized experience",
            "description": "Must not be saved.",
            "category": "research",
            "thumbnail": "",
            "ended_at": "",
        }

        for user in (None, self.member, self.editor):
            if user is None:
                self.client.logout()
            else:
                self.client.force_login(user)
            response = self.client.post(create_url, data)
            self.assertEqual(response.status_code, 403)

        self.assertFalse(
            Experience.objects.filter(title="Unauthorized experience").exists()
        )

    def test_ajax_create_experience_requires_csrf(self):
        from django.test import Client

        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.owner)
        create_url = reverse("main:create_experience_ajax")
        data = {
            "title": "CSRF protected experience",
            "description": "Requires a valid CSRF token.",
            "category": "research",
            "thumbnail": "",
            "ended_at": "",
        }

        self.assertEqual(csrf_client.post(create_url, data).status_code, 403)
        login_response = csrf_client.get(reverse("main:login"))
        csrf_token = str(login_response.context["csrf_token"])
        response = csrf_client.post(
            create_url,
            data,
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(response.status_code, 201)

    def test_ajax_toggle_experience_star(self):
        toggle_url = reverse(
            "main:toggle_experience_star",
            args=[self.experience.pk],
        )
        anonymous_response = self.client.post(toggle_url)
        self.assertEqual(anonymous_response.status_code, 403)

        self.client.force_login(self.member)
        starred_response = self.client.post(toggle_url)
        self.assertEqual(starred_response.status_code, 200)
        self.assertEqual(starred_response.json(), {"star_count": 1, "is_starred": True})

        unstarred_response = self.client.post(toggle_url)
        self.assertEqual(unstarred_response.status_code, 200)
        self.assertEqual(unstarred_response.json(), {"star_count": 0, "is_starred": False})

    def test_experience_page_uses_json_data(self):
        response = self.client.get(reverse("main:show_experience"))

        experience_ids = [experience.pk for experience in response.context["experience_list"]]
        self.assertIn(self.experience.pk, experience_ids)
        self.assertContains(response, self.experience.title)

    def test_experience_page_has_management_controls(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertNotContains(response, reverse("main:create_experience"))
        self.assertNotContains(
            response,
            reverse("main:update_experience", args=[self.experience.pk]),
        )
        self.assertNotContains(
            response,
            reverse("main:delete_experience", args=[self.experience.pk]),
        )

        self.client.force_login(self.editor)
        response = self.client.get(reverse("main:show_experience"))
        self.assertNotContains(response, reverse("main:create_experience"))
        self.assertContains(
            response,
            reverse("main:update_experience", args=[self.experience.pk]),
        )
        self.assertNotContains(
            response,
            reverse("main:delete_experience", args=[self.experience.pk]),
        )

        self.client.force_login(self.owner)
        response = self.client.get(reverse("main:show_experience"))
        self.assertContains(response, reverse("main:create_experience"))
        self.assertContains(
            response,
            reverse("main:update_experience", args=[self.experience.pk]),
        )
        self.assertContains(
            response,
            reverse("main:update_experience", args=[self.experience.pk]),
        )
        self.assertContains(
            response,
            reverse("main:delete_experience", args=[self.experience.pk]),
        )

    def test_experience_create_form_page(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("main:create_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience_form.html")
        self.assertContains(response, "Add New Experience")

    def test_experience_update_form_page(self):
        self.client.force_login(self.editor)
        response = self.client.get(
            reverse("main:update_experience", args=[self.experience.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience_form.html")
        self.assertContains(response, "Edit Experience")
        self.assertContains(response, self.experience.title)

    def test_create_experience(self):
        self.client.force_login(self.owner)
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

    def test_experience_form_strips_html_from_text_fields(self):
        form = ExperienceForm(
            {
                "title": "<b>Teaching Assistant</b>",
                "description": "<p>Helped students learn programming.</p>",
                "category": "research",
                "thumbnail": "",
                "ended_at": "",
            }
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["title"], "Teaching Assistant")
        self.assertEqual(
            form.cleaned_data["description"],
            "Helped students learn programming.",
        )

    def test_experience_form_rejects_title_containing_only_html(self):
        form = ExperienceForm(
            {
                "title": "<script></script>",
                "description": "A description.",
                "category": "research",
                "thumbnail": "",
                "ended_at": "",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_update_experience(self):
        self.client.force_login(self.editor)
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
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("main:delete_experience", args=[self.experience.pk])
        )

        self.assertRedirects(response, reverse("main:show_experience"))
        self.assertFalse(Experience.objects.filter(pk=self.experience.pk).exists())

    def test_delete_experience_requires_post(self):
        self.client.force_login(self.owner)
        response = self.client.get(
            reverse("main:delete_experience", args=[self.experience.pk])
        )

        self.assertEqual(response.status_code, 405)

    def test_experience_mutations_follow_role_matrix(self):
        create_url = reverse("main:create_experience")
        update_url = reverse("main:update_experience", args=[self.experience.pk])
        delete_url = reverse("main:delete_experience", args=[self.experience.pk])
        create_data = {
            "title": "New Experience",
            "description": "Created by owner.",
            "category": "research",
            "thumbnail": "",
            "ended_at": "",
        }
        update_data = {
            **create_data,
            "title": "Updated Experience",
        }

        for url, data in ((create_url, create_data), (update_url, update_data), (delete_url, {})):
            response = self.client.post(url, data)
            self.assertRedirects(response, f"{reverse('main:login')}?next={url}")

        self.client.force_login(self.member)
        self.assertEqual(self.client.post(create_url, create_data).status_code, 403)
        self.assertEqual(self.client.post(update_url, update_data).status_code, 403)
        self.assertEqual(self.client.post(delete_url).status_code, 403)

        self.client.force_login(self.editor)
        self.assertEqual(self.client.post(create_url, create_data).status_code, 403)
        self.assertRedirects(
            self.client.post(update_url, update_data),
            reverse("main:show_experience"),
        )
        self.assertEqual(self.client.post(delete_url).status_code, 403)

        self.client.force_login(self.owner)
        self.assertRedirects(
            self.client.post(create_url, create_data),
            reverse("main:show_experience"),
        )
        self.assertRedirects(
            self.client.post(delete_url),
            reverse("main:show_experience"),
        )

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Completed")
        self.assertContains(
            response,
            '<p class="experience-status">Completed</p>',
        )

    def test_projects_url_is_accessible(self):
        response = self.client.get(reverse("main:show_projects"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects.html")

    def test_update_project_form_page(self):
        self.client.force_login(self.editor)
        response = self.client.get(
            reverse("main:update_project", args=[self.finished_project.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects_form.html")
        self.assertTrue(response.context["is_edit"])
        self.assertContains(response, self.finished_project.title)

    def test_projects_page_has_edit_controls(self):
        response = self.client.get(reverse("main:show_projects"))
        self.assertContains(response, 'data-is-editor="false"')
        self.client.force_login(self.editor)
        response = self.client.get(reverse("main:show_projects"))
        self.assertContains(response, 'data-is-editor="true"')

    def test_project_create_form_uses_create_mode(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("main:create_project"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add New Project")
        self.assertContains(response, reverse("main:create_project"))
        self.assertNotContains(response, "Edit Project")

    def test_project_update_form_uses_edit_mode(self):
        self.client.force_login(self.editor)
        response = self.client.get(
            reverse("main:update_project", args=[self.finished_project.pk])
        )

        self.assertContains(response, "Edit Project")
        self.assertContains(
            response,
            reverse("main:update_project", args=[self.finished_project.pk]),
        )

    def test_update_project(self):
        self.client.force_login(self.editor)
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
        self.client.force_login(self.editor)
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
        self.client.force_login(self.editor)
        response = self.client.get(reverse("main:update_project", args=[999999]))

        self.assertEqual(response.status_code, 404)

    def test_project_model(self):
        self.assertEqual(str(self.finished_project), "Infographic @Kastratpacil")
        self.assertTrue(self.finished_project.is_finished)
        self.assertFalse(self.ongoing_project.is_finished)

    def test_projects_page_renders_database_projects(self):
        response = self.client.get(reverse("main:show_projects"))

        self.assertContains(response, 'id="project-search-form"')
        self.assertContains(response, 'id="loading"')
        self.assertContains(response, 'id="error"')
        self.assertContains(response, 'id="empty"')
        self.assertContains(response, 'id="grid"')
        self.assertNotContains(response, self.finished_project.title)

        projects_response = self.client.get(reverse("main:get_projects_json"))
        project_titles = [
            item["fields"]["title"] for item in projects_response.json()
        ]
        self.assertIn(self.finished_project.title, project_titles)
        self.assertIn(self.ongoing_project.title, project_titles)

    def test_projects_json_filters_titles_case_insensitively(self):
        response = self.client.get(
            reverse("main:get_projects_json"),
            {"title": "infographic"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(
            response.json()[0]["fields"]["title"],
            self.finished_project.title,
        )

    def test_project_controls_are_visible_only_to_superuser(self):
        response = self.client.get(reverse("main:show_projects"))
        self.assertNotContains(response, reverse("main:create_project"))
        self.assertContains(response, 'data-is-owner="false"')
        self.assertContains(response, 'data-is-editor="false"')
        self.assertNotContains(response, 'id="add-project-modal"')

        self.client.force_login(self.member)
        response = self.client.get(reverse("main:show_projects"))
        self.assertNotContains(response, reverse("main:create_project"))
        self.assertContains(response, 'data-is-owner="false"')
        self.assertContains(response, 'data-is-editor="false"')
        self.assertNotContains(response, 'id="add-project-modal"')

        self.client.force_login(self.editor)
        response = self.client.get(reverse("main:show_projects"))
        self.assertNotContains(response, reverse("main:create_project"))
        self.assertContains(response, 'data-is-owner="false"')
        self.assertContains(response, 'data-is-editor="true"')
        self.assertNotContains(response, 'id="add-project-modal"')

        self.client.force_login(self.owner)
        response = self.client.get(reverse("main:show_projects"))
        self.assertContains(response, reverse("main:create_project"))
        self.assertContains(response, 'data-is-owner="true"')
        self.assertContains(response, 'id="add-project-modal"')

    def test_create_project_requires_login_and_superuser(self):
        create_url = reverse("main:create_project")
        response = self.client.get(create_url)
        self.assertRedirects(response, f"{reverse('main:login')}?next={create_url}")

        self.client.force_login(self.member)
        self.assertEqual(self.client.get(create_url).status_code, 403)
        self.assertEqual(
            self.client.post(
                create_url,
                {
                    "title": "Unauthorized project",
                    "description": "Should not be created.",
                    "status": "finished",
                },
            ).status_code,
            403,
        )
        self.assertFalse(Project.objects.filter(title="Unauthorized project").exists())

        self.client.force_login(self.editor)
        self.assertEqual(self.client.get(create_url).status_code, 403)
        self.assertEqual(
            self.client.post(
                create_url,
                {
                    "title": "Editor project",
                    "description": "Editors cannot create projects.",
                    "status": "finished",
                },
            ).status_code,
            403,
        )

    def test_superuser_can_create_project(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("main:create_project"),
            {
                "title": "Authorized project",
                "description": "Created by the portfolio owner.",
                "status": "finished",
                "image_path": "",
                "external_url": "",
            },
        )

        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertTrue(Project.objects.filter(title="Authorized project").exists())

    def test_ajax_project_create_requires_owner_and_post(self):
        create_url = reverse("main:create_project_ajax")
        project_data = {
            "title": "AJAX project",
            "description": "Created through fetch.",
            "status": "finished",
            "image_path": "",
            "external_url": "",
        }

        self.assertEqual(self.client.get(create_url).status_code, 405)
        self.assertEqual(self.client.post(create_url, project_data).status_code, 403)

        for user in (self.member, self.editor):
            self.client.force_login(user)
            response = self.client.post(create_url, project_data)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["message"], "Only the portfolio owner can add projects.")

        self.client.force_login(self.owner)
        response = self.client.post(create_url, project_data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Project.objects.filter(title="AJAX project").exists())

    def test_ajax_project_create_returns_form_errors(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("main:create_project_ajax"),
            {
                "title": "<img src=x>",
                "description": "Invalid project.",
                "status": "finished",
                "image_path": "",
                "external_url": "",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("title", response.json()["errors"])
        self.assertFalse(Project.objects.filter(description="Invalid project.").exists())

    def test_ajax_project_create_requires_csrf(self):
        from django.test import Client

        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.owner)
        create_url = reverse("main:create_project_ajax")
        project_data = {
            "title": "CSRF protected project",
            "description": "Requires a valid CSRF token.",
            "status": "finished",
            "image_path": "",
            "external_url": "",
        }

        self.assertEqual(csrf_client.post(create_url, project_data).status_code, 403)
        page_response = csrf_client.get(reverse("main:show_projects"))
        self.assertEqual(page_response.status_code, 200)
        token = str(page_response.context["csrf_token"])
        response = csrf_client.post(
            create_url,
            project_data,
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, 201)

    def test_delete_project_requires_login_superuser_and_post(self):
        delete_url = reverse("main:delete_project", args=[self.finished_project.pk])
        response = self.client.post(delete_url)
        self.assertRedirects(response, f"{reverse('main:login')}?next={delete_url}")

        self.client.force_login(self.member)
        self.assertEqual(self.client.post(delete_url).status_code, 403)
        self.assertTrue(Project.objects.filter(pk=self.finished_project.pk).exists())

        self.client.force_login(self.editor)
        self.assertEqual(self.client.post(delete_url).status_code, 403)
        self.assertTrue(Project.objects.filter(pk=self.finished_project.pk).exists())

        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(delete_url).status_code, 405)
        response = self.client.post(delete_url)
        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertFalse(Project.objects.filter(pk=self.finished_project.pk).exists())

    def test_authenticated_user_can_toggle_project_star(self):
        toggle_url = reverse("main:toggle_star", args=[self.finished_project.pk])
        self.client.force_login(self.member)

        response = self.client.post(toggle_url)
        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertTrue(self.finished_project.starred_by.filter(pk=self.member.pk).exists())

        self.client.post(toggle_url)
        self.assertFalse(self.finished_project.starred_by.filter(pk=self.member.pk).exists())

    def test_star_requires_login_and_post(self):
        toggle_url = reverse("main:toggle_star", args=[self.finished_project.pk])
        response = self.client.post(toggle_url)

        self.assertRedirects(response, f"{reverse('main:login')}?next={toggle_url}")
        self.client.force_login(self.member)
        self.assertEqual(self.client.get(toggle_url).status_code, 405)
        self.assertFalse(self.finished_project.starred_by.exists())

    def test_projects_json_omits_starred_user_identities(self):
        self.finished_project.starred_by.add(self.member)

        response = self.client.get(reverse("main:get_projects_json"))
        serialized_projects = response.json()
        serialized_project = next(
            item
            for item in serialized_projects
            if item["pk"] == self.finished_project.pk
        )

        self.assertEqual(
            serialized_project["fields"]["title"],
            self.finished_project.title,
        )
        self.assertEqual(serialized_project["fields"]["star_count"], 1)
        self.assertFalse(serialized_project["fields"]["is_starred"])
        self.assertNotIn("starred_by", serialized_project["fields"])
        self.assertNotContains(response, "member")

        self.client.force_login(self.member)
        starred_response = self.client.get(reverse("main:get_projects_json"))
        starred_project = next(
            item
            for item in starred_response.json()
            if item["pk"] == self.finished_project.pk
        )
        self.assertTrue(starred_project["fields"]["is_starred"])

    def test_editor_and_owner_can_toggle_project_stars(self):
        toggle_url = reverse("main:toggle_star", args=[self.finished_project.pk])

        for user in (self.editor, self.owner):
            self.client.force_login(user)
            response = self.client.post(toggle_url)

            self.assertRedirects(response, reverse("main:show_projects"))
            self.assertTrue(
                self.finished_project.starred_by.filter(pk=user.pk).exists()
            )

            self.client.post(toggle_url)
            self.assertFalse(
                self.finished_project.starred_by.filter(pk=user.pk).exists()
            )

    def test_project_page_shows_star_count_and_current_user_state(self):
        self.finished_project.starred_by.add(self.member)

        anonymous_response = self.client.get(reverse("main:get_projects_json"))
        anonymous_project = next(
            item
            for item in anonymous_response.json()
            if item["pk"] == self.finished_project.pk
        )
        self.assertEqual(anonymous_project["fields"]["star_count"], 1)
        self.assertFalse(anonymous_project["fields"]["is_starred"])

        self.client.force_login(self.member)
        starred_response = self.client.get(reverse("main:get_projects_json"))
        starred_project = next(
            item
            for item in starred_response.json()
            if item["pk"] == self.finished_project.pk
        )
        self.assertTrue(starred_project["fields"]["is_starred"])

    def test_finished_project_has_image_and_external_link(self):
        response = self.client.get(reverse("main:get_projects_json"))
        project = next(
            item
            for item in response.json()
            if item["pk"] == self.finished_project.pk
        )

        self.assertEqual(project["fields"]["image_path"], "img/infografis-kastratpacil.png")
        self.assertIn("instagram.com/p/DXG__RDky7O/", project["fields"]["external_url"])

    def test_ongoing_project_has_no_image(self):
        response = self.client.get(reverse("main:get_projects_json"))
        project = next(
            item
            for item in response.json()
            if item["pk"] == self.ongoing_project.pk
        )
        self.assertEqual(project["fields"]["image_path"], "")

    def test_project_form_strips_html_and_rejects_empty_title(self):
        valid_form = ProjectForm(
            {
                "title": "<b>Portfolio</b>",
                "description": "Build <i>great</i> things.",
                "status": "finished",
                "image_path": "",
                "external_url": "",
            }
        )

        self.assertTrue(valid_form.is_valid(), valid_form.errors)
        self.assertEqual(valid_form.cleaned_data["title"], "Portfolio")
        self.assertEqual(valid_form.cleaned_data["description"], "Build great things.")

        invalid_form = ProjectForm(
            {
                "title": "<img src=x>",
                "description": "No title remains.",
                "status": "finished",
                "image_path": "",
                "external_url": "",
            }
        )
        self.assertFalse(invalid_form.is_valid())
        self.assertIn("title", invalid_form.errors)

    def test_empty_projects_page(self):
        Project.objects.all().delete()
        response = self.client.get(reverse("main:show_projects"))

        self.assertContains(response, "No projects have been added or found yet.")

    def test_project_update_permissions_follow_role_matrix(self):
        update_url = reverse("main:update_project", args=[self.finished_project.pk])
        update_data = {
            "title": "Updated Project",
            "description": "Updated by an authorized account.",
            "status": "ongoing",
            "image_path": "",
            "external_url": "",
        }

        response = self.client.post(update_url, update_data)
        self.assertRedirects(response, f"{reverse('main:login')}?next={update_url}")

        self.client.force_login(self.member)
        self.assertEqual(self.client.post(update_url, update_data).status_code, 403)

        self.client.force_login(self.editor)
        self.assertRedirects(
            self.client.post(update_url, update_data),
            reverse("main:show_projects"),
        )

        self.client.force_login(self.owner)
        update_data["title"] = "Owner Updated Project"
        self.assertRedirects(
            self.client.post(update_url, update_data),
            reverse("main:show_projects"),
        )