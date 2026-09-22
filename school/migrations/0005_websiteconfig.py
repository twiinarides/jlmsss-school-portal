# Generated manually
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0004_set_default_video_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebsiteConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hero_background_image', models.ImageField(blank=True, help_text='Background image for hero section', null=True, upload_to='config/')),
                ('hero_overlay_opacity', models.FloatField(default=0.5, help_text='Overlay opacity (0.0 to 1.0) for background image')),
                ('hero_title', models.CharField(blank=True, help_text='Custom hero title (overrides school name if set)', max_length=200)),
                ('hero_subtitle', models.CharField(blank=True, help_text='Hero subtitle text', max_length=300)),
                ('show_admission_link', models.BooleanField(default=True)),
                ('show_academics_link', models.BooleanField(default=True)),
                ('show_about_link', models.BooleanField(default=True)),
                ('show_login_link', models.BooleanField(default=False, help_text='Show login link in navigation')),
                ('headteacher_section_background', models.ImageField(blank=True, help_text='Background image for headteacher message section', null=True, upload_to='config/')),
                ('headteacher_section_overlay_opacity', models.FloatField(default=0.3, help_text='Overlay opacity for headteacher section')),
                ('footer_text', models.TextField(blank=True, help_text='Custom footer text')),
                ('show_designer_credit', models.BooleanField(default=True)),
                ('designer_name', models.CharField(blank=True, default='Twiina Technologies', max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Website Configuration',
                'verbose_name_plural': 'Website Configuration',
            },
        ),
    ]

