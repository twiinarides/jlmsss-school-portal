from django.db import migrations


def ensure_student_life_page(apps, schema_editor):
    Page = apps.get_model("school", "Page")

    Page.objects.update_or_create(
        slug="student-life",
        defaults={
            "title": "Student Life",
            "content": "<p>Student life content will appear here.</p>",
            "is_published": True,
            "order": 0,
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ("school", "0008_fix_gallery_table_schema"),
    ]

    operations = [
        migrations.RunPython(ensure_student_life_page, migrations.RunPython.noop),
    ]
