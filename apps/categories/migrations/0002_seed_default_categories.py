from django.db import migrations

DEFAULT_CATEGORIES = [
    ("Salary", "INCOME"),
    ("Food", "EXPENSE"),
    ("Transport", "EXPENSE"),
    ("Rent", "EXPENSE"),
    ("Shopping", "EXPENSE"),
    ("Education", "EXPENSE"),
    ("Entertainment", "EXPENSE"),
    ("Healthcare", "EXPENSE"),
    ("Other", "EXPENSE"),
]


def seed_default_categories(apps, schema_editor):
    Category = apps.get_model("categories", "Category")
    for name, category_type in DEFAULT_CATEGORIES:
        Category.objects.get_or_create(
            user=None, name=name, category_type=category_type
        )


def remove_default_categories(apps, schema_editor):
    Category = apps.get_model("categories", "Category")
    Category.objects.filter(user__isnull=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("categories", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_default_categories, remove_default_categories),
    ]
