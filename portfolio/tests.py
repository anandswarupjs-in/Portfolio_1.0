import io
import shutil
import tempfile
from datetime import date

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import (Achievement, Certification, ContactMessage, Education, GalleryImage, Profile, Project,
                     ProjectImage, Skill)

MEDIA = tempfile.mkdtemp()


def png(name="t.png"):
    buf = io.BytesIO()
    Image.new("RGB", (20, 20), "white").save(buf, "PNG")
    return SimpleUploadedFile(name, buf.getvalue(), content_type="image/png")


@override_settings(MEDIA_ROOT=MEDIA, SECURE_SSL_REDIRECT=False, ALLOWED_HOSTS=["testserver"])
class PortfolioTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.profile = Profile.objects.create(
            full_name="Anand Swarup J S", professional_title="CSE Student", introduction="Intro text here.",
            about="About text here.", email="anand@example.com", github_url="https://github.com/example",
            linkedin_url="https://linkedin.com/in/example",
            resume=SimpleUploadedFile("cv.pdf", b"%PDF-1.4 test", content_type="application/pdf"),
        )
        self.project = Project.objects.create(
            title="Alpha App", short_description="Does alpha things", full_description="Long alpha text",
            technologies="Python, Django", category="web", is_featured=True, features="One\nTwo",
        )
        self.other = Project.objects.create(
            title="Beta Tool", short_description="Does beta things", technologies="Java", category="software",
        )
        self.hidden = Project.objects.create(
            title="Secret Thing", short_description="hidden", technologies="Rust", is_visible=False,
        )

    # --- pages ---
    def test_homepage_loads_with_profile_from_database(self):
        r = self.client.get(reverse("portfolio:home"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Anand")
        self.assertContains(r, "Intro text here.")
        self.assertContains(r, "CSE Student")

    def test_homepage_loads_without_profile(self):
        Profile.objects.all().delete()
        r = self.client.get(reverse("portfolio:home"))
        self.assertEqual(r.status_code, 200)

    def test_nav_and_sections_present(self):
        r = self.client.get(reverse("portfolio:home"))
        for label in ("Home", "About", "Skills", "Projects", "Achievements", "Contact"):
            self.assertContains(r, ">%s<" % label)
        for anchor in ('id="home"', 'id="about"', 'id="projects"', 'id="contact"'):
            self.assertContains(r, anchor)

    def test_footer_text(self):
        self.assertContains(self.client.get(reverse("portfolio:home")), "netflix inspired")

    def test_resume_download_link(self):
        self.assertContains(self.client.get(reverse("portfolio:home")), "Download resume")
        self.profile.resume = ""
        self.profile.save()
        self.assertNotContains(self.client.get(reverse("portfolio:home")), "Download resume")

    def test_social_links_only_when_present(self):
        self.profile.github_url = ""
        self.profile.save()
        self.assertNotContains(self.client.get(reverse("portfolio:home")), "github.com/example")

    def test_education_and_skills_display(self):
        Education.objects.create(institution="IIIT Kottayam", qualification="B.Tech", field_of_study="CSE", start_year=2023)
        Skill.objects.create(name="Python", category="languages")
        Skill.objects.create(name="HiddenSkill", category="tools", is_visible=False)
        r = self.client.get(reverse("portfolio:home"))
        self.assertContains(r, "IIIT Kottayam")
        self.assertContains(r, "Programming Languages")
        self.assertContains(r, "Python")
        self.assertNotContains(r, "HiddenSkill")

    def test_achievements_and_certifications_display_and_hide(self):
        Achievement.objects.create(title="Won Hackathon", date=date(2025, 1, 5), organization="Org")
        Achievement.objects.create(title="Hidden Award", date=date(2025, 1, 5), is_visible=False)
        Certification.objects.create(title="Cert One", issuing_organization="Issuer", completion_date=date(2025, 2, 1),
                                     credential_url="https://example.com/verify")
        r = self.client.get(reverse("portfolio:home"))
        self.assertContains(r, "Won Hackathon")
        self.assertNotContains(r, "Hidden Award")
        self.assertContains(r, "Cert One")
        self.assertContains(r, "https://example.com/verify")

    def test_gallery_display_and_hidden(self):
        GalleryImage.objects.create(image=png("a.png"), caption="Workshop day", gallery_type="workshop")
        GalleryImage.objects.create(image=png("b.png"), caption="Private pic", is_visible=False)
        r = self.client.get(reverse("portfolio:home"))
        self.assertContains(r, "Workshop day")
        self.assertContains(r, "data-lightbox")
        self.assertNotContains(r, "Private pic")

    # --- projects ---
    def test_featured_projects_on_home_exclude_hidden(self):
        r = self.client.get(reverse("portfolio:home"))
        self.assertContains(r, "Alpha App")
        self.assertNotContains(r, "Secret Thing")

    def test_projects_page_lists_visible_only(self):
        r = self.client.get(reverse("portfolio:projects"))
        self.assertContains(r, "Alpha App")
        self.assertContains(r, "Beta Tool")
        self.assertNotContains(r, "Secret Thing")

    def test_project_search(self):
        r = self.client.get(reverse("portfolio:projects"), {"q": "beta"})
        self.assertEqual(r.context["match_count"], 1)
        self.assertEqual([p.title for p in r.context["projects"] if p.matches], ["Beta Tool"])

    def test_project_category_filter(self):
        r = self.client.get(reverse("portfolio:projects"), {"category": "web"})
        self.assertEqual([p.title for p in r.context["projects"] if p.matches], ["Alpha App"])

    def test_project_technology_filter(self):
        r = self.client.get(reverse("portfolio:projects"), {"tech": "java"})
        self.assertEqual([p.title for p in r.context["projects"] if p.matches], ["Beta Tool"])

    def test_invalid_category_ignored(self):
        r = self.client.get(reverse("portfolio:projects"), {"category": "nonsense"})
        self.assertEqual(r.context["match_count"], 2)

    def test_empty_state(self):
        r = self.client.get(reverse("portfolio:projects"), {"q": "zzzzzz"})
        self.assertEqual(r.context["match_count"], 0)
        self.assertContains(r, "No projects match these filters")

    def test_project_detail(self):
        ProjectImage.objects.create(project=self.project, image=png("s.png"), caption="Shot one", alt_text="Screenshot")
        r = self.client.get(self.project.get_absolute_url())
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Long alpha text")
        self.assertContains(r, "Shot one")
        self.assertContains(r, "Two")

    def test_project_detail_hides_missing_links(self):
        r = self.client.get(self.project.get_absolute_url())
        self.assertNotContains(r, "Live demo")
        self.assertNotContains(r, "Source on GitHub")

    def test_project_detail_shows_links_when_present(self):
        self.project.demo_url = "https://demo.example.com"
        self.project.save()
        self.assertContains(self.client.get(self.project.get_absolute_url()), "Live demo")

    def test_hidden_project_detail_404(self):
        self.assertEqual(self.client.get(self.hidden.get_absolute_url()).status_code, 404)

    def test_unknown_project_404(self):
        self.assertEqual(self.client.get("/projects/nope/").status_code, 404)

    def test_related_projects(self):
        Project.objects.create(title="Gamma Web", short_description="g", technologies="Python", category="web")
        r = self.client.get(self.project.get_absolute_url())
        self.assertIn("Gamma Web", [p.title for p in r.context["related"]])

    def test_slug_auto_generated_and_unique(self):
        a = Project.objects.create(title="Same Title", short_description="x", technologies="a")
        b = Project.objects.create(title="Same Title", short_description="x", technologies="a")
        self.assertEqual(a.slug, "same-title")
        self.assertEqual(b.slug, "same-title-2")

    def test_status_property(self):
        self.assertEqual(self.project.status, "In progress")
        self.project.completion_date = date(2025, 1, 1)
        self.assertEqual(self.project.status, "Completed")

    # --- contact ---
    def post_contact(self, **over):
        data = {"name": "Visitor", "email": "v@example.com", "subject": "Hello", "message": "A valid long message.",
                "source": "contact"}
        data.update(over)
        return self.client.post(reverse("portfolio:contact"), data)

    def test_contact_page_loads(self):
        self.assertEqual(self.client.get(reverse("portfolio:contact")).status_code, 200)

    def test_contact_message_stored(self):
        r = self.post_contact()
        self.assertEqual(r.status_code, 302)
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_contact_success_message_shown(self):
        r = self.post_contact(source="home")
        self.assertTrue(r["Location"].endswith("#contact"))
        r = self.client.get(reverse("portfolio:home"))
        self.assertContains(r, "Message sent")

    def test_contact_validation(self):
        r = self.post_contact(email="not-an-email", message="short")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertContains(r, "The message was not sent")

    def test_contact_requires_all_fields(self):
        r = self.post_contact(name="", subject="")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_contact_honeypot_discards(self):
        self.post_contact(website="http://spam.example")
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_contact_rate_limit(self):
        for _ in range(5):
            self.post_contact()
        self.post_contact()
        self.assertEqual(ContactMessage.objects.count(), 5)

    def test_contact_csrf_enforced(self):
        from django.test import Client
        c = Client(enforce_csrf_checks=True)
        r = c.post(reverse("portfolio:contact"), {"name": "x", "email": "a@b.co", "subject": "s", "message": "long enough message"})
        self.assertEqual(r.status_code, 403)

    def test_contact_get_not_storing(self):
        self.client.get(reverse("portfolio:contact"))
        self.assertEqual(ContactMessage.objects.count(), 0)

    # --- models / uploads ---
    def test_only_one_profile(self):
        with self.assertRaises(ValidationError):
            Profile.objects.create(full_name="B", professional_title="x", introduction="x", email="b@example.com")

    def test_education_year_validation(self):
        e = Education(institution="X", qualification="Y", start_year=2024, end_year=2022)
        with self.assertRaises(ValidationError):
            e.full_clean()

    def test_skill_unique_per_category(self):
        Skill.objects.create(name="Python", category="languages")
        s = Skill(name="Python", category="languages")
        with self.assertRaises(ValidationError):
            s.full_clean()

    def test_upload_rejects_bad_extension(self):
        bad = SimpleUploadedFile("x.exe", b"MZ", content_type="application/octet-stream")
        g = GalleryImage(image=bad)
        with self.assertRaises(ValidationError):
            g.full_clean()

    def test_resume_rejects_non_pdf(self):
        p = Profile(full_name="B", professional_title="t", introduction="i", email="b@example.com",
                    resume=SimpleUploadedFile("r.txt", b"hi"))
        with self.assertRaises(ValidationError) as ctx:
            p.full_clean(exclude=["id"])
        self.assertIn("resume", ctx.exception.message_dict)

    def test_image_upload_saved_and_served_url(self):
        g = GalleryImage.objects.create(image=png("c.png"), caption="C")
        self.assertTrue(g.image.url.startswith("/media/gallery/"))

    # --- admin ---
    def test_admin_requires_login(self):
        r = self.client.get("/admin/")
        self.assertEqual(r.status_code, 302)
        self.assertIn("login", r["Location"])

    def test_admin_login_and_model_pages(self):
        User = get_user_model()
        User.objects.create_superuser("owner", "o@example.com", "a-strong-pass-123")
        self.assertTrue(self.client.login(username="owner", password="a-strong-pass-123"))
        for model in ("profile", "education", "skill", "project", "achievement", "certification", "galleryimage",
                      "contactmessage"):
            r = self.client.get("/admin/portfolio/%s/" % model)
            self.assertEqual(r.status_code, 200, model)
        self.assertEqual(self.client.get("/admin/portfolio/project/add/").status_code, 200)

    def test_admin_profile_add_blocked_when_exists(self):
        User = get_user_model()
        User.objects.create_superuser("owner", "o@example.com", "a-strong-pass-123")
        self.client.login(username="owner", password="a-strong-pass-123")
        self.assertEqual(self.client.get("/admin/portfolio/profile/add/").status_code, 403)

    def test_contact_message_visible_in_admin(self):
        self.post_contact(subject="Admin visible subject")
        User = get_user_model()
        User.objects.create_superuser("owner", "o@example.com", "a-strong-pass-123")
        self.client.login(username="owner", password="a-strong-pass-123")
        self.assertContains(self.client.get("/admin/portfolio/contactmessage/"), "Admin visible subject")

    # --- errors ---
    @override_settings(DEBUG=False)
    def test_custom_404_page(self):
        r = self.client.get("/does-not-exist/")
        self.assertEqual(r.status_code, 404)
        self.assertContains(r, "Page not found", status_code=404)

    # --- email CTA button ---
    def test_email_button_on_home_with_profile(self):
        r = self.client.get(reverse("portfolio:home"))
        self.assertContains(r, "mailto:anandswarupjs@gmail.com")
        self.assertContains(r, "Email me")

    def test_email_button_on_home_without_profile(self):
        Profile.objects.all().delete()
        r = self.client.get(reverse("portfolio:home"))
        self.assertContains(r, "mailto:anandswarupjs@gmail.com")
        self.assertContains(r, "Email me")

    def test_email_button_on_projects_page(self):
        r = self.client.get(reverse("portfolio:projects"))
        self.assertContains(r, "mailto:anandswarupjs@gmail.com")
        self.assertContains(r, "Email me")

    def test_email_button_on_project_detail(self):
        r = self.client.get(self.project.get_absolute_url())
        self.assertContains(r, "mailto:anandswarupjs@gmail.com")
        self.assertContains(r, "Email me")

    def test_email_button_on_contact_page(self):
        r = self.client.get(reverse("portfolio:contact"))
        self.assertContains(r, "mailto:anandswarupjs@gmail.com")
        self.assertContains(r, "Email me")

    def test_email_button_mailto_is_correct(self):
        r = self.client.get(reverse("portfolio:home"))
        self.assertContains(r, 'href="mailto:anandswarupjs@gmail.com"')

    def test_netflix_inspired_is_last_text(self):
        r = self.client.get(reverse("portfolio:home"))
        content = r.content.decode()
        email_pos = content.rfind("Email me")
        netflix_pos = content.rfind("netflix inspired")
        self.assertGreater(netflix_pos, email_pos, "'netflix inspired' must appear after 'Email me'")


@override_settings(MEDIA_ROOT=MEDIA, SECURE_SSL_REDIRECT=False, ALLOWED_HOSTS=["testserver"])
class EnsureAdminCommandTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def _run(self, env_vars):
        from io import StringIO
        from unittest.mock import patch
        from django.core.management import call_command
        out = StringIO()
        with patch.dict("os.environ", env_vars, clear=False):
            call_command("ensure_admin", stdout=out)
        return out.getvalue()

    def test_creates_superuser(self):
        User = get_user_model()
        self.assertEqual(User.objects.filter(username="testadmin").count(), 0)
        output = self._run({
            "DJANGO_SUPERUSER_USERNAME": "testadmin",
            "DJANGO_SUPERUSER_EMAIL": "admin@test.com",
            "DJANGO_SUPERUSER_PASSWORD": "strongpass999",
        })
        self.assertIn("created", output)
        u = User.objects.get(username="testadmin")
        self.assertTrue(u.is_superuser)
        self.assertTrue(u.check_password("strongpass999"))

    def test_updates_existing_superuser_password(self):
        User = get_user_model()
        User.objects.create_superuser("existing_admin", "e@test.com", "oldpassword")
        self._run({
            "DJANGO_SUPERUSER_USERNAME": "existing_admin",
            "DJANGO_SUPERUSER_EMAIL": "e@test.com",
            "DJANGO_SUPERUSER_PASSWORD": "newpassword999",
        })
        u = User.objects.get(username="existing_admin")
        self.assertTrue(u.check_password("newpassword999"))
        self.assertFalse(u.check_password("oldpassword"))

    def test_noop_when_variables_not_set(self):
        import os
        # Ensure vars are absent
        env = {k: "" for k in ("DJANGO_SUPERUSER_USERNAME", "DJANGO_SUPERUSER_EMAIL", "DJANGO_SUPERUSER_PASSWORD")}
        output = self._run(env)
        self.assertIn("skipped", output)
        User = get_user_model()
        self.assertEqual(User.objects.filter(is_superuser=True).count(), 0)
