from django.contrib import admin
from django.utils.html import format_html

from .models import (Achievement, Certification, ContactMessage, Education, GalleryImage, Profile, Project,
                     ProjectImage, Skill)

admin.site.site_header = "ANAND ORIGINALS Admin"
admin.site.site_title = "ANAND ORIGINALS"
admin.site.index_title = "Manage portfolio content"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "professional_title", "email", "photo_preview")
    readonly_fields = ("photo_preview",)
    fieldsets = (
        ("Personal Information", {
            "fields": ("full_name", "professional_title", "email", "phone", "location")
        }),
        ("Hero Photo (Replaces 'AO' Placeholder)", {
            "fields": ("photo", "photo_preview"),
            "description": "Upload your portrait photo here. When empty, the website displays the 'AO' monogram placeholder in the hero section."
        }),
        ("Introductions", {
            "fields": ("introduction", "about")
        }),
        ("Resume & Social Links", {
            "fields": ("resume", "github_url", "linkedin_url")
        }),
    )

    def photo_preview(self, obj):
        if obj and obj.photo:
            return format_html(
                '<img src="{}" style="max-height: 120px; max-width: 120px; object-fit: cover; border-radius: 4px; border: 1px solid #ccc;" alt="Profile Photo" />',
                obj.photo.url
            )
        return format_html('<span style="color: #999; font-style: italic;">No photo uploaded (currently showing "AO" placeholder)</span>')
    photo_preview.short_description = "Photo Preview (AO Replacement)"

    def has_add_permission(self, request):
        return not Profile.objects.exists()  # only one primary profile

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ("qualification", "institution", "start_year", "end_year", "display_order")
    list_editable = ("display_order",)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "display_order", "is_visible")
    list_editable = ("display_order", "is_visible")
    list_filter = ("category", "is_visible")
    search_fields = ("name",)


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 3  # provides multiple screenshot upload rows by default
    fields = ("image", "image_preview", "caption", "alt_text", "display_order")
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="max-height: 60px; max-width: 100px; object-fit: cover; border-radius: 3px;" alt="Screenshot Preview" />',
                obj.image.url
            )
        return "-"
    image_preview.short_description = "Preview"


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "thumbnail_preview", "category", "is_featured", "is_visible", "display_order")
    list_editable = ("is_featured", "is_visible", "display_order")
    list_filter = ("category", "is_featured", "is_visible")
    search_fields = ("title", "short_description", "technologies")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("thumbnail_preview", "hero_preview")
    inlines = [ProjectImageInline]

    fieldsets = (
        ("Basic Information", {
            "fields": ("title", "slug", "tagline", "category", "display_order", "is_featured", "is_visible")
        }),
        ("Descriptions & Features", {
            "fields": ("short_description", "full_description", "features", "technologies", "role")
        }),
        ("Dates & Links", {
            "fields": ("start_date", "completion_date", "github_url", "demo_url")
        }),
        ("Cover & Hero Images", {
            "fields": ("thumbnail", "thumbnail_preview", "hero_image", "hero_preview"),
            "description": "Thumbnail appears on project cards. Hero image appears at the top of the project detail page. Add app screenshots below."
        }),
    )

    def thumbnail_preview(self, obj):
        if obj and obj.thumbnail:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 80px; object-fit: cover; border-radius: 3px;" alt="Thumbnail" />',
                obj.thumbnail.url
            )
        return format_html('<span style="color: #999;">No thumbnail</span>')
    thumbnail_preview.short_description = "Thumbnail"

    def hero_preview(self, obj):
        if obj and obj.hero_image:
            return format_html(
                '<img src="{}" style="max-height: 80px; max-width: 140px; object-fit: cover; border-radius: 3px;" alt="Hero" />',
                obj.hero_image.url
            )
        return format_html('<span style="color: #999;">No hero image</span>')
    hero_preview.short_description = "Hero Preview"


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = ("project", "image_preview", "caption", "display_order")
    list_filter = ("project",)
    search_fields = ("caption", "alt_text", "project__title")
    list_editable = ("display_order",)
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="max-height: 60px; max-width: 100px; object-fit: cover; border-radius: 3px;" alt="Screenshot" />',
                obj.image.url
            )
        return "-"
    image_preview.short_description = "Preview"


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ("title", "organization", "date", "is_visible")
    list_editable = ("is_visible",)
    list_filter = ("is_visible",)
    search_fields = ("title", "organization")


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ("title", "issuing_organization", "completion_date", "is_visible")
    list_editable = ("is_visible",)
    list_filter = ("is_visible",)
    search_fields = ("title", "issuing_organization")


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ("__str__", "gallery_type", "project", "display_order", "is_visible")
    list_editable = ("display_order", "is_visible")
    list_filter = ("gallery_type", "is_visible")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "name", "email", "created_at")
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("name", "email", "subject", "message", "created_at")

    def has_add_permission(self, request):
        return False
