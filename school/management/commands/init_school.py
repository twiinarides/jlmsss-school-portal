from django.core.management.base import BaseCommand
from school.models import SchoolInfo, Page


class Command(BaseCommand):
    help = 'Initialize school with basic information'

    def handle(self, *args, **options):
        # Create or update school info
        school, created = SchoolInfo.objects.get_or_create(
            name="Kamuganguzi Janan Luwum Memorial Senior Secondary School",
            defaults={
                'motto': 'Excellence in Education',
                'address': 'Kampala, Uganda',
                'phone': '+256 XXX XXX XXX',
                'email': 'info@school.ug',
                'about': '<p>Welcome to our school. We are committed to providing quality education...</p>',
                'vision': '<p>To be a leading educational institution...</p>',
                'mission': '<p>To provide quality education that empowers students...</p>',
                'dotshule_url': 'https://dotshule.ug/',
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Successfully created school: {school.name}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'School already exists: {school.name}'))
        
        # Create default pages
        pages_data = [
            {
                'title': 'About Us',
                'slug': 'about',
                'content': '<p>Learn more about our school...</p>',
                'order': 1,
            },
            {
                'title': 'Academics',
                'slug': 'academics',
                'content': '<p>Our academic programs...</p>',
                'order': 2,
            },
            {
                'title': 'Admissions',
                'slug': 'admission',
                'content': '<p>Admission information...</p>',
                'order': 3,
            },
            {
                'title': 'Student Life',
                'slug': 'student-life',
                'content': '<p>Student life and co-curricular activities...</p>',
                'order': 4,
            },
        ]
        
        for page_data in pages_data:
            page, created = Page.objects.get_or_create(
                slug=page_data['slug'],
                defaults=page_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created page: {page.title}'))
        
        self.stdout.write(self.style.SUCCESS('School initialization complete!'))

