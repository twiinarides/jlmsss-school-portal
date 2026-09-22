# Generated manually
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0002_alter_headteachermessage_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='headteachermessage',
            name='video_url',
            field=models.URLField(blank=True, help_text='YouTube or video embed URL (if video type is YouTube)', null=True),
        ),
        migrations.AddField(
            model_name='headteachermessage',
            name='video_type',
            field=models.CharField(choices=[('youtube', 'YouTube URL'), ('local', 'Local Video File')], default='youtube', help_text='Video source type', max_length=10),
        ),
        migrations.AddField(
            model_name='headteachermessage',
            name='video_file',
            field=models.FileField(blank=True, help_text='Local video file (if video type is local)', null=True, upload_to='headteacher/videos/'),
        ),
    ]

