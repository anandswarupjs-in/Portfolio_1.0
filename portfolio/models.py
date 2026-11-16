import os

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

MAX_IMAGE_MB = 5
MAX_FILE_MB = 10


def _check(upload, extensions, max_mb):
    ext = os.path.splitext(upload.name)[1].lower().lstrip(".")
    if ext not in extensions:
        raise ValidationError("Unsupported file type. Allowed: %s." % ", ".join(extensions))
    if upload.size > max_mb * 1024 * 1024:
        raise ValidationError("File is too large. Maximum size is %d MB." % max_mb)


def validate_image(upload):
    _check(upload, ("jpg", "jpeg", "png", "webp", "gif"), MAX_IMAGE_MB)


def validate_pdf(upload):
    _check(upload, ("pdf",), MAX_FILE_MB)


def validate_certificate(upload):
    _check(upload, ("pdf", "jpg", "jpeg", "png"), MAX_FILE_MB)


PROJECT_CATEGORIES = [
    ("web", "Web Development"),
    ("software", "Software"),
    ("ai", "AI & Machine Learning"),
    ("systems", "Systems"),
    ("other", "Other"),
]
SKILL_CATEGORIES = [
    ("languages", "Programming Languages"),
    ("web", "Web Development"),
    ("databases", "Databases"),
    ("fundamentals", "Computer Science Fundamentals"),
    ("tools", "Development Tools & Platforms"),
]
GALLERY_TYPES = [
    ("workshop", "Workshop"),
    ("event", "Event"),
    ("collaboration", "Collaboration"),
    ("other", "Other"),
]


class Profile(models.Model):
    full_name = models.CharField(max_length=120)
    professional_title = models.CharField(max_length=160)
    introduction = models.TextField(help_text="Short introduction shown in the hero section.")
    about = models.TextField(blank=True, help_text="Longer description for the About section.")
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    location = models.CharField(max_length=120, blank=True)
    photo = models.ImageField(
        upload_to="profile/", blank=True, validators=[validate_image],
        help_text="Portrait photo. Replaces the 'AO' monogram placeholder in the hero section.",
    )
    resume = models.FileField(upload_to="resume/", blank=True, validators=[validate_pdf], help_text="PDF only.")
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)

    def __str__(self):
        return self.full_name

    @property
    def github_username(self):
        if not self.github_url:
            return ""
        return self.github_url.rstrip("/").split("/")[-1]

    def clean(self):
        if not self.pk and Profile.objects.exists():
            raise ValidationError("Only one profile is allowed. Edit the existing profile instead.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Education(models.Model):
    institution = models.CharField(max_length=200)
    qualification = models.CharField(max_length=160)
    field_of_study = models.CharField(max_length=160, blank=True)
    start_year = models.PositiveSmallIntegerField(validators=[MinValueValidator(1990), MaxValueValidator(2100)])
    end_year = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1990), MaxValueValidator(2100)],
        help_text="Leave empty if ongoing.",
    )
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "-start_year"]
        verbose_name_plural = "Education entries"

    def __str__(self):
        return "%s - %s" % (self.qualification, self.institution)

    def clean(self):
        if self.end_year and self.start_year and self.end_year < self.start_year:
            raise ValidationError({"end_year": "End year cannot be before the start year."})


class Skill(models.Model):
    name = models.CharField(max_length=80)
    category = models.CharField(max_length=20, choices=SKILL_CATEGORIES)
    icon = models.CharField(max_length=50, blank=True, help_text="Optional short symbol or text shown before the name.")
    display_order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ["category", "display_order", "name"]
        constraints = [models.UniqueConstraint(fields=["name", "category"], name="uniq_skill_name_category")]

    def __str__(self):
        return self.name


class Project(models.Model):
    title = models.CharField(max_length=140)
    slug = models.SlugField(max_length=140, unique=True, blank=True, help_text="Auto-generated from the title if empty.")
    tagline = models.CharField(max_length=200, blank=True)
    short_description = models.CharField(max_length=300)
    full_description = models.TextField(blank=True)
    features = models.TextField(blank=True, help_text="One feature per line.")
    category = models.CharField(max_length=20, choices=PROJECT_CATEGORIES, default="software")
    technologies = models.CharField(max_length=300, help_text="Comma-separated, e.g. Python, Django, SQLite.")
    github_url = models.URLField(blank=True)
    demo_url = models.URLField("Live demo URL", blank=True)
    thumbnail = models.ImageField(upload_to="projects/thumbnails/", blank=True, validators=[validate_image])
    hero_image = models.ImageField(upload_to="projects/hero/", blank=True, validators=[validate_image])
    start_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True, help_text="Leave empty if still in progress.")
    role = models.CharField("Role / contribution", max_length=200, blank=True)
    is_featured = models.BooleanField("Featured", default=False)
    is_visible = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "-start_date", "title"]
        indexes = [
            models.Index(fields=["is_visible", "display_order"], name="proj_vis_order_idx"),
            models.Index(fields=["is_featured"], name="proj_featured_idx"),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("portfolio:project_detail", args=[self.slug])

    def clean(self):
        if self.start_date and self.completion_date and self.completion_date < self.start_date:
            raise ValidationError({"completion_date": "Completion date cannot be before the start date."})

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:130] or "project"
            slug, n = base, 2
            while Project.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = "%s-%d" % (base, n)
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def tech_list(self):
        return [t.strip() for t in self.technologies.split(",") if t.strip()]

    @property
    def tech_lower(self):
        return "|".join(t.lower() for t in self.tech_list)

    @property
    def feature_list(self):
        return [f.strip() for f in self.features.splitlines() if f.strip()]

    @property
    def status(self):
        return "Completed" if self.completion_date else "In progress"

    @property
    def search_blob(self):
        return " ".join([self.title, self.tagline, self.short_description, self.full_description]).lower()


class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="projects/screenshots/", validators=[validate_image])
    caption = models.CharField(max_length=200, blank=True)
    alt_text = models.CharField(max_length=200, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "id"]
        verbose_name = "Project screenshot"
        verbose_name_plural = "Project screenshots"

    def __str__(self):
        return "%s - image %s" % (self.project, self.pk or "new")


class Achievement(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    organization = models.CharField(max_length=200, blank=True)
    date = models.DateField()
    image = models.ImageField(upload_to="achievements/", blank=True, validators=[validate_image])
    verification_url = models.URLField(blank=True)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return self.title


class Certification(models.Model):
    title = models.CharField(max_length=200)
    issuing_organization = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    completion_date = models.DateField()
    certificate_file = models.FileField(upload_to="certificates/", blank=True, validators=[validate_certificate])
    credential_url = models.URLField(blank=True)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ["-completion_date"]

    def __str__(self):
        return self.title


class GalleryImage(models.Model):
    image = models.ImageField(upload_to="gallery/", validators=[validate_image])
    caption = models.CharField(max_length=200, blank=True)
    gallery_type = models.CharField(max_length=20, choices=GALLERY_TYPES, default="event")
    project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.SET_NULL, related_name="gallery_images")
    alt_text = models.CharField(max_length=200, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "-id"]

    def __str__(self):
        return self.caption or "Gallery image %s" % self.pk


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["-created_at"], name="contact_created_idx")]

    def __str__(self):
        return "%s: %s" % (self.name, self.subject)
