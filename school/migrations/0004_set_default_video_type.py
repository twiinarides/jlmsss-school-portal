# Generated manually
from django.db import migrations


def set_default_video_type(apps, schema_editor):
    """Set default video_type for existing records"""
    HeadteacherMessage = apps.get_model('school', 'HeadteacherMessage')
    for msg in HeadteacherMessage.objects.all():
        if not hasattr(msg, 'video_type') or not msg.video_type:
            if hasattr(msg, 'video_file') and msg.video_file:
                msg.video_type = 'local'
            else:
                msg.video_type = 'youtube'
            msg.save()


def reverse_set_default_video_type(apps, schema_editor):
    """Reverse migration - no action needed"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0003_add_video_file_support'),
    ]

    operations = [
        migrations.RunPython(set_default_video_type, reverse_set_default_video_type),
    ]

