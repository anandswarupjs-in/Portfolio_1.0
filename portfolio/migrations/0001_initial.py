import django.core.validators
import django.db.models.deletion
from django.db import migrations, models

import portfolio.models

PROJECT_CATEGORIES = [("web", "Web Development"), ("software", "Software"), ("ai", "AI & Machine Learning"), ("systems", "Systems"), ("other", "Other")]
SKILL_CATEGORIES = [("languages", "Programming Languages"), ("web", "Web Development"), ("databases", "Databases"), ("fundamentals", "Computer Science Fundamentals"), ("tools", "Development Tools & Platforms")]
GALLERY_TYPES = [("workshop", "Workshop"), ("event", "Event"), ("collaboration", "Collaboration"), ("other", "Other")]


def pk():
    return ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"))


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Profile",
            fields=[
                pk(),
                ("full_name", models.CharField(max_length=120)),
                ("professional_title", models.CharField(max_length=160)),
                ("introduction", models.TextField(help_text="Short introduction shown in the hero section.")),
                ("about", models.TextField(blank=True, help_text="Longer description for the About section.")),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(blank=True, max_length=30)),
                ("location", models.CharField(blank=True, max_length=120)),
                ("photo", models.ImageField(blank=True, upload_to="profile/", validators=[portfolio.models.validate_image])),
                ("resume", models.FileField(blank=True, help_text="PDF only.", upload_to="resume/", validators=[portfolio.models.validate_pdf])),
                ("github_url", models.URLField(blank=True)),
                ("linkedin_url", models.URLField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name="Education",
            fields=[
                pk(),
                ("institution", models.CharField(max_length=200)),
                ("qualification", models.CharField(max_length=160)),
                ("field_of_study", models.CharField(blank=True, max_length=160)),
                ("start_year", models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1990), django.core.validators.MaxValueValidator(2100)])),
                ("end_year", models.PositiveSmallIntegerField(blank=True, help_text="Leave empty if ongoing.", null=True, validators=[django.core.validators.MinValueValidator(1990), django.core.validators.MaxValueValidator(2100)])),
                ("description", models.TextField(blank=True)),
                ("display_order", models.PositiveIntegerField(default=0)),
            ],
            options={"verbose_name_plural": "Education entries", "ordering": ["display_order", "-start_year"]},
        ),
        migrations.CreateModel(
            name="Skill",
            fields=[
                pk(),
                ("name", models.CharField(max_length=80)),
                ("category", models.CharField(choices=SKILL_CATEGORIES, max_length=20)),
                ("icon", models.CharField(blank=True, help_text="Optional short symbol or text shown before the name.", max_length=50)),
                ("display_order", models.PositiveIntegerField(default=0)),
                ("is_visible", models.BooleanField(default=True)),
            ],
            options={"ordering": ["category", "display_order", "name"]},
        ),
        migrations.AddConstraint(
            model_name="skill",
            constraint=models.UniqueConstraint(fields=("name", "category"), name="uniq_skill_name_category"),
        ),
        migrations.CreateModel(
            name="Project",
            fields=[
                pk(),
                ("title", models.CharField(max_length=140)),
                ("slug", models.SlugField(blank=True, help_text="Auto-generated from the title if empty.", max_length=140, unique=True)),
                ("tagline", models.CharField(blank=True, max_length=200)),
                ("short_description", models.CharField(max_length=300)),
                ("full_description", models.TextField(blank=True)),
                ("features", models.TextField(blank=True, help_text="One feature per line.")),
                ("category", models.CharField(choices=PROJECT_CATEGORIES, default="software", max_length=20)),
                ("technologies", models.CharField(help_text="Comma-separated, e.g. Python, Django, SQLite.", max_length=300)),
                ("github_url", models.URLField(blank=True)),
                ("demo_url", models.URLField(blank=True, verbose_name="Live demo URL")),
                ("thumbnail", models.ImageField(blank=True, upload_to="projects/thumbnails/", validators=[portfolio.models.validate_image])),
                ("hero_image", models.ImageField(blank=True, upload_to="projects/hero/", validators=[portfolio.models.validate_image])),
                ("start_date", models.DateField(blank=True, null=True)),
                ("completion_date", models.DateField(blank=True, help_text="Leave empty if still in progress.", null=True)),
                ("role", models.CharField(blank=True, max_length=200, verbose_name="Role / contribution")),
                ("is_featured", models.BooleanField(default=False, verbose_name="Featured")),
                ("is_visible", models.BooleanField(default=True)),
                ("display_order", models.PositiveIntegerField(default=0)),
            ],
            options={
                "ordering": ["display_order", "-start_date", "title"],
                "indexes": [
                    models.Index(fields=["is_visible", "display_order"], name="proj_vis_order_idx"),
                    models.Index(fields=["is_featured"], name="proj_featured_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="ProjectImage",
            fields=[
                pk(),
                ("image", models.ImageField(upload_to="projects/screenshots/", validators=[portfolio.models.validate_image])),
                ("caption", models.CharField(blank=True, max_length=200)),
                ("alt_text", models.CharField(blank=True, max_length=200)),
                ("display_order", models.PositiveIntegerField(default=0)),
                ("project", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="images", to="portfolio.project")),
            ],
            options={"ordering": ["display_order", "id"]},
        ),
        migrations.CreateModel(
            name="Achievement",
            fields=[
                pk(),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("organization", models.CharField(blank=True, max_length=200)),
                ("date", models.DateField()),
                ("image", models.ImageField(blank=True, upload_to="achievements/", validators=[portfolio.models.validate_image])),
                ("verification_url", models.URLField(blank=True)),
                ("is_visible", models.BooleanField(default=True)),
            ],
            options={"ordering": ["-date"]},
        ),
        migrations.CreateModel(
            name="Certification",
            fields=[
                pk(),
                ("title", models.CharField(max_length=200)),
                ("issuing_organization", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("completion_date", models.DateField()),
                ("certificate_file", models.FileField(blank=True, upload_to="certificates/", validators=[portfolio.models.validate_certificate])),
                ("credential_url", models.URLField(blank=True)),
                ("is_visible", models.BooleanField(default=True)),
            ],
            options={"ordering": ["-completion_date"]},
        ),
        migrations.CreateModel(
            name="GalleryImage",
            fields=[
                pk(),
                ("image", models.ImageField(upload_to="gallery/", validators=[portfolio.models.validate_image])),
                ("caption", models.CharField(blank=True, max_length=200)),
                ("gallery_type", models.CharField(choices=GALLERY_TYPES, default="event", max_length=20)),
                ("alt_text", models.CharField(blank=True, max_length=200)),
                ("display_order", models.PositiveIntegerField(default=0)),
                ("is_visible", models.BooleanField(default=True)),
                ("project", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="gallery_images", to="portfolio.project")),
            ],
            options={"ordering": ["display_order", "-id"]},
        ),
        migrations.CreateModel(
            name="ContactMessage",
            fields=[
                pk(),
                ("name", models.CharField(max_length=120)),
                ("email", models.EmailField(max_length=254)),
                ("subject", models.CharField(max_length=200)),
                ("message", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [models.Index(fields=["-created_at"], name="contact_created_idx")],
            },
        ),
    ]
