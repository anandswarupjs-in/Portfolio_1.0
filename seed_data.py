"""
Seed script: populate the database with Anand Originals initial data.
Run with:  python manage.py shell < seed_data.py
"""

import django, os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from portfolio.models import Profile, Education, Skill, Project

# ─── 1. PROFILE ───────────────────────────────────────────────────────────────
if not Profile.objects.exists():
    Profile.objects.create(
        full_name="Anand Swarup J S",
        professional_title="Computer Science Student | Developer | Technology Enthusiast",
        introduction=(
            "Welcome to Anand Originals — a collection of ideas, experiments, and applications "
            "built through curiosity, creativity, and continuous learning.\n\n"
            "Explore the projects, discover the technologies behind them, and take a look at the "
            "stories behind the work."
        ),
        about=(
            "I am a second-year B.Tech Computer Science and Engineering student with an interest "
            "in software development, problem-solving, databases, algorithms, and emerging technologies.\n\n"
            "I enjoy transforming ideas into practical applications and exploring how technology can "
            "solve real-world problems.\n\n"
            "Through individual and collaborative projects, I aim to strengthen my programming skills, "
            "experiment with different technologies, and build applications that are both useful and meaningful.\n\n"
            "I believe every project is an opportunity to learn something new, overcome challenges, "
            "and create something valuable."
        ),
        email="workwithanand23@gmail.com",
        linkedin_url="https://www.linkedin.com/in/anand-swarupjs2007",
        github_url="",
    )
    print("[✓] Profile created.")
else:
    print("[~] Profile already exists — skipped.")

# ─── 2. EDUCATION ─────────────────────────────────────────────────────────────
if not Education.objects.exists():
    Education.objects.create(
        institution="TO BE ADDED",
        qualification="Bachelor of Technology (B.Tech)",
        field_of_study="Computer Science and Engineering",
        start_year=2024,
        end_year=None,          # ongoing
        description="Second Year | Expected graduation: TO BE ADDED",
        display_order=1,
    )
    print("[✓] Education entry created.")
else:
    print("[~] Education already exists — skipped.")

# ─── 3. SKILLS ────────────────────────────────────────────────────────────────
skills_data = [
    # (name, category, display_order)
    # Programming Languages
    ("Python",                           "languages",     1),
    ("C",                                "languages",     2),
    # Web Technologies
    ("HTML",                             "web",           1),
    ("CSS",                              "web",           2),
    # Databases
    ("MySQL",                            "databases",     1),
    # Libraries & Frameworks  → mapped to "web" (closest available category)
    ("NumPy",                            "web",           10),
    ("Matplotlib",                       "web",           11),
    # CS Fundamentals
    ("Data Structures and Algorithms",   "fundamentals",  1),
    ("Database Management Systems",      "fundamentals",  2),
    ("Design and Analysis of Algorithms","fundamentals",  3),
    ("Theory of Computation",            "fundamentals",  4),
    ("Bioinformatics Algorithms",        "fundamentals",  5),
    # Tools
    ("Visual Studio Code",               "tools",         1),
]

created_skills = 0
for name, cat, order in skills_data:
    obj, created = Skill.objects.get_or_create(
        name=name, category=cat,
        defaults={"display_order": order, "is_visible": True}
    )
    if created:
        created_skills += 1

print("[✓] Skills created: %d (existing skipped)" % created_skills)

# ─── 4. PROJECTS ──────────────────────────────────────────────────────────────
projects_data = [
    {
        "title": "Dental Clinic Management System",
        "tagline": "One platform. Every appointment. Complete clinic management.",
        "short_description": (
            "A centralized management application designed to simplify dental clinic operations, "
            "patient management, and appointment scheduling."
        ),
        "full_description": (
            "The Dental Clinic Management System aims to organize essential clinic operations through "
            "a centralized application. It focuses on managing patient information, appointments, and "
            "clinic-related records in a structured manner.\n\n"
            "The application is intended to reduce manual administrative work and make everyday clinic "
            "operations easier to manage."
        ),
        "features": (
            "Patient management\n"
            "Appointment scheduling\n"
            "Appointment tracking\n"
            "Clinic record management\n"
            "Organized information storage"
        ),
        "category": "software",
        "technologies": "TO BE ADDED",
        "display_order": 1,
    },
    {
        "title": "IntelliPlan",
        "tagline": "Plan smarter. Stay organized. Move forward.",
        "short_description": (
            "IntelliPlan is a productivity application — full details to be added based on the actual implementation."
        ),
        "full_description": "TO BE ADDED based on actual application functionality.",
        "features": "TO BE ADDED",
        "category": "software",
        "technologies": "TO BE ADDED",
        "display_order": 2,
    },
    {
        "title": "Electricity Consumption Analyzer",
        "tagline": "Understand your energy. Analyze your consumption. Make informed decisions.",
        "short_description": (
            "An application focused on analyzing electricity consumption and presenting useful "
            "information about energy usage."
        ),
        "full_description": (
            "The Electricity Consumption Analyzer is designed to help users examine electricity "
            "consumption data and understand usage patterns through data analysis and visualization.\n\n"
            "The project focuses on transforming consumption records into information that is easier "
            "to interpret."
        ),
        "features": (
            "Electricity consumption data analysis\n"
            "Consumption visualization\n"
            "Usage pattern identification"
        ),
        "category": "other",
        "technologies": "TO BE ADDED",
        "display_order": 3,
    },
    {
        "title": "Retail Store Management System",
        "tagline": "Organize inventory. Simplify operations. Manage smarter.",
        "short_description": (
            "A software application intended to support retail store management and organize "
            "important store-related information."
        ),
        "full_description": "TO BE ADDED based on actual implementation.",
        "features": (
            "Product management (TO BE VERIFIED)\n"
            "Inventory management (TO BE VERIFIED)\n"
            "Sales records (TO BE VERIFIED)\n"
            "Customer information (TO BE VERIFIED)\n"
            "Stock tracking (TO BE VERIFIED)"
        ),
        "category": "software",
        "technologies": "TO BE ADDED",
        "display_order": 4,
    },
    {
        "title": "Daily Expense Manager",
        "tagline": "Every expense tells a story. Take control of yours.",
        "short_description": (
            "An application intended to help users record and organize their daily expenses."
        ),
        "full_description": "TO BE ADDED",
        "features": (
            "Expense recording (TO BE VERIFIED)\n"
            "Expense categorization (TO BE VERIFIED)\n"
            "Daily expense summaries (TO BE VERIFIED)\n"
            "Spending history (TO BE VERIFIED)\n"
            "Expense analysis (TO BE VERIFIED)"
        ),
        "category": "software",
        "technologies": "TO BE ADDED",
        "display_order": 5,
    },
    {
        "title": "Laundry Management System",
        "tagline": "From laundry orders to organized operations.",
        "short_description": (
            "A management application intended to organize laundry-related operations and records."
        ),
        "full_description": "TO BE ADDED",
        "features": (
            "Customer management (TO BE VERIFIED)\n"
            "Laundry order management (TO BE VERIFIED)\n"
            "Order tracking (TO BE VERIFIED)\n"
            "Payment records (TO BE VERIFIED)\n"
            "Delivery status (TO BE VERIFIED)"
        ),
        "category": "software",
        "technologies": "TO BE ADDED",
        "display_order": 6,
    },
]

created_projects = 0
for pdata in projects_data:
    title = pdata.pop("title")
    obj, created = Project.objects.get_or_create(
        title=title,
        defaults=pdata,
    )
    if created:
        created_projects += 1
    else:
        print("  [~] Project already exists: %s" % title)

print("[✓] Projects created: %d (existing skipped)" % created_projects)
print("\n✅ Seed complete! All data has been added to the database.")
print("   → Open /admin/ to review and complete the remaining details.")
