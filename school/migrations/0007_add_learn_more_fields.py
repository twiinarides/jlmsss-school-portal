# Generated manually
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0006_academicperformance_admissiondocument_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='websiteconfig',
            name='learn_more_text',
            field=models.CharField(blank=True, default='Learn More About Us', help_text='Text for the "Learn More" button on home page', max_length=200),
        ),
        migrations.AddField(
            model_name='websiteconfig',
            name='learn_more_url',
            field=models.CharField(blank=True, help_text='URL for the "Learn More" button (leave blank to use default About Us page)', max_length=200),
        ),
    ]

