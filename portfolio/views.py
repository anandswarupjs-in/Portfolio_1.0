from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import ContactForm
from .models import (PROJECT_CATEGORIES, SKILL_CATEGORIES, Achievement, Certification, Education, GalleryImage,
                     Profile, Project, Skill)

DEFAULT_NAME = "Anand Swarup J S"
DEFAULT_TITLE = "Computer Science and Engineering Student, IIIT Kottayam"


def _name_lines(name):
    """Split a name into display lines, keeping trailing initials with the previous word."""
    lines = []
    for word in name.split():
        if len(word) <= 2 and lines:
            lines[-1] += " " + word
        else:
            lines.append(word)
    return lines


def site_context(request):
    profile = Profile.objects.first()
    name = profile.full_name if profile else DEFAULT_NAME
    return {
        "profile": profile,
        "owner_name": name,
        "owner_title": profile.professional_title if profile else DEFAULT_TITLE,
        "name_lines": _name_lines(name),
    }


def home(request):
    skills = Skill.objects.filter(is_visible=True)
    skill_groups = []
    for key, label in SKILL_CATEGORIES:
        items = [s for s in skills if s.category == key]
        if items:
            skill_groups.append((label, items))

    visible = Project.objects.filter(is_visible=True)

    context = {
        "education": Education.objects.all(),
        "skill_groups": skill_groups,
        "all_projects": list(visible),
        "achievements": Achievement.objects.filter(is_visible=True),
        "certifications": Certification.objects.filter(is_visible=True),
        "gallery": GalleryImage.objects.filter(is_visible=True),
        "form": ContactForm(initial={"source": "home"}),
    }
    return render(request, "home.html", context)


def projects(request):
    q = request.GET.get("q", "").strip()[:100]
    category = request.GET.get("category", "").strip()
    tech = request.GET.get("tech", "").strip()[:60]
    if category not in dict(PROJECT_CATEGORIES):
        category = ""

    all_projects = list(Project.objects.filter(is_visible=True))
    tech_options = {}
    for p in all_projects:
        for t in p.tech_list:
            tech_options.setdefault(t.lower(), t)

    for p in all_projects:
        p.matches = (
            (not q or q.lower() in p.search_blob)
            and (not category or p.category == category)
            and (not tech or tech.lower() in p.tech_lower.split("|"))
        )

    filters_active = bool(q or category or tech)
    context = {
        "projects": all_projects,
        "featured": [p for p in all_projects if p.is_featured],
        "match_count": sum(1 for p in all_projects if p.matches),
        "q": q,
        "category": category,
        "tech": tech,
        "filters_active": filters_active,
        "categories": PROJECT_CATEGORIES,
        "tech_options": sorted(tech_options.values(), key=str.lower),
    }
    return render(request, "projects.html", context)


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug, is_visible=True)
    related = list(Project.objects.filter(is_visible=True, category=project.category).exclude(pk=project.pk)[:3])
    if len(related) < 3:
        mine = {t.lower() for t in project.tech_list}
        for other in Project.objects.filter(is_visible=True).exclude(pk=project.pk):
            if other not in related and mine & set(other.tech_lower.split("|")):
                related.append(other)
            if len(related) == 3:
                break
    return render(request, "project_detail.html", {
        "project": project,
        "screenshots": project.images.all(),
        "related": related,
    })


def _rate_limited(request):
    key = "contact-rate:%s" % request.META.get("REMOTE_ADDR", "unknown")
    window = settings.CONTACT_RATE_WINDOW
    if cache.add(key, 1, window):
        return False
    try:
        return cache.incr(key) > settings.CONTACT_RATE_LIMIT
    except ValueError:  # key expired between add and incr
        cache.set(key, 1, window)
        return False


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            back = reverse("portfolio:home") + "#contact" if form.cleaned_data.get("source") == "home" \
                else reverse("portfolio:contact")
            if form.cleaned_data.get("website"):  # honeypot tripped: pretend success, store nothing
                messages.success(request, "Message sent. Thank you for reaching out.")
                return redirect(back)
            if _rate_limited(request):
                messages.error(request, "Too many messages sent from this connection. Please try again later.")
                return redirect(back)
            form.save()
            messages.success(request, "Message sent. Thank you for reaching out.")
            return redirect(back)
        messages.error(request, "The message was not sent. Check the highlighted fields and try again.")
    else:
        form = ContactForm(initial={"source": "contact"})
    return render(request, "contact.html", {"form": form})
