from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from main.forms import ExperienceForm, ProjectForm
from main.models import Experience, Project


def _is_editor(user):
    return user.groups.filter(name="Editor").exists()


def _require_owner(user):
    if not user.is_superuser:
        raise PermissionDenied


def _require_editor_or_owner(user):
    if not user.is_superuser and not _is_editor(user):
        raise PermissionDenied


def show_main(request):
    last_login = request.COOKIES.get("last_login") or (
        "No active login session / Cookie not found"
    )
    context = {
        "name": "Azkal Azkiya Arifi Putra",
        "npm": "2506636991",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "A Computer Science student at Universitas Indonesia interested "
            "in software development and education."
        ),
        "last_login": last_login,
    }
    return render(request, "index.html", context)


def register(request):
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Account created successfully. Please log in.")
        return redirect("main:login")

    context = {
        "name": "Azkal Azkiya Arifi Putra",
        "form": form,
    }
    return render(request, "register.html", context)


def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        response = redirect("main:show_main")
        response.set_cookie(
            "last_login",
            timezone.localtime().strftime("%Y-%m-%d %H:%M:%S"),
        )
        return response

    context = {
        "name": "Azkal Azkiya Arifi Putra",
        "form": form,
    }
    return render(request, "login.html", context)


def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie("last_login")
    return response


def show_experience(request):
    json_response = get_experience_json(request)
    experiences = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    experiences = [experience.object for experience in experiences]

    context = {
        "name": "Azkal Azkiya Arifi Putra",
        "experience_list": experiences,
        "is_editor": _is_editor(request.user),
    }
    return render(request, "experience.html", context)


@login_required(login_url="main:login")
def create_experience(request):
    _require_owner(request.user)
    form = ExperienceForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Experience baru berhasil ditambahkan!")
        return redirect("main:show_experience")

    context = {
        "name": "Azkal Azkiya Arifi Putra",
        "form": form,
        "is_edit": False,
    }
    return render(request, "experience_form.html", context)


@login_required(login_url="main:login")
def update_experience(request, experience_id):
    _require_editor_or_owner(request.user)
    experience = get_object_or_404(Experience, pk=experience_id)
    form = ExperienceForm(request.POST or None, instance=experience)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Experience berhasil diperbarui!")
        return redirect("main:show_experience")

    context = {
        "name": "Azkal Azkiya Arifi Putra",
        "form": form,
        "is_edit": True,
        "experience": experience,
    }
    return render(request, "experience_form.html", context)


@login_required(login_url="main:login")
@require_POST
def delete_experience(request, experience_id):
    _require_owner(request.user)
    experience = get_object_or_404(Experience, pk=experience_id)
    experience.delete()
    messages.success(request, "Experience berhasil dihapus!")
    return redirect("main:show_experience")

def show_projects(request):
    json_response = get_projects_json(request)

    projects = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    projects = [project.object for project in projects]

    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Azkal Azkiya Arifi Putra",
        "project_list": projects,
        "title_query": title_query,
        "is_editor": _is_editor(request.user),
    }

    return render(request, "projects.html", context)


@login_required(login_url="main:login")
def create_project(request):
    _require_owner(request.user)

    form = ProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("main:show_projects")

    context = {
        "name": "Azkal Azkiya Arifi Putra",
        "form": form,
    }
    return render(request, "projects_form.html", context)


@login_required(login_url="main:login")
def update_project(request, project_id):
    _require_editor_or_owner(request.user)
    project = get_object_or_404(Project, pk=project_id)
    form = ProjectForm(request.POST or None, instance=project)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Project berhasil diperbarui!")
        return redirect("main:show_projects")

    context = {
        "name": "Azkal Azkiya Arifi Putra",
        "form": form,
        "is_edit": True,
        "project": project,
    }
    return render(request, "projects_form.html", context)


@login_required(login_url="main:login")
@require_POST
def delete_project(request, project_id):
    _require_owner(request.user)

    project = get_object_or_404(Project, pk=project_id)
    project.delete()
    messages.success(request, "Project berhasil dihapus!")
    return redirect("main:show_projects")


@login_required(login_url="main:login")
@require_POST
def toggle_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.user in project.starred_by.all():
        project.starred_by.remove(request.user)
    else:
        project.starred_by.add(request.user)
    return redirect("main:show_projects")


def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    projects_json = serializers.serialize(
        "json",
        projects,
        use_natural_foreign_keys=True,
    )
    return HttpResponse(projects_json, content_type="application/json")


def get_experience_json(request):
    experiences = Experience.objects.all()
    experiences_json = serializers.serialize("json", experiences)
    return HttpResponse(experiences_json, content_type="application/json")