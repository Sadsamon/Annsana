"""
Seed the eight canonical cultural categories defined in TSD §4.

This is a data migration so any fresh database (dev, staging, prod) has
the taxonomy from day one without requiring a separate management-command
invocation. The seed_categories management command remains available as a
convenience for environments that wipe data without re-migrating.
"""
from django.db import migrations

CATEGORIES = [
    ('Food',         'food',         'Traditional dishes, recipes, and food culture.'),
    ('Attire',       'attire',       'Clothing, textiles, and traditional dress.'),
    ('Rituals',      'rituals',      'Ceremonies, rites of passage, and spiritual practices.'),
    ('Music',        'music',        'Traditional instruments, songs, and musical traditions.'),
    ('Language',     'language',     'Proverbs, oral literature, scripts, and dialects.'),
    ('Crafts',       'crafts',       'Handmade objects, artisanry, and material culture.'),
    ('Architecture', 'architecture', 'Buildings, settlements, and built environment.'),
    ('Ceremonies',   'ceremonies',   'Community gatherings, festivals, and celebrations.'),
]


def seed_categories(apps, schema_editor):
    Category = apps.get_model('feed', 'Category')
    for name, slug, description in CATEGORIES:
        Category.objects.get_or_create(
            slug=slug,
            defaults={'name': name, 'description': description},
        )


def unseed_categories(apps, schema_editor):
    Category = apps.get_model('feed', 'Category')
    Category.objects.filter(slug__in=[row[1] for row in CATEGORIES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_categories, reverse_code=unseed_categories),
    ]
