from django.shortcuts import render

from main.models import Experience, Project

from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect, render

from main.forms import ExperienceForm, ProjectForm

def show_main(request):
    context = {
        "name": "Azkal Azkiya Arifi Putra",
        "npm": "2506636991",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "A Computer Science student at Universitas Indonesia interested "
            "in software development and education."
        ),
    }
    return render(request, "index.html", context)


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
    }
    return render(request, "experience.html", context)


def create_experience(request):
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


def update_experience(request, experience_id):
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


@require_POST
def delete_experience(request, experience_id):
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
    }

    return render(request, "projects.html", context)

def create_project(request):
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

def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Project berhasil dihapus!")

    return redirect("main:show_projects")

def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    projects_json = serializers.serialize("json", projects)
    return HttpResponse(projects_json, content_type="application/json")


def get_experience_json(request):
    experiences = Experience.objects.all()
    experiences_json = serializers.serialize("json", experiences)
    return HttpResponse(experiences_json, content_type="application/json")