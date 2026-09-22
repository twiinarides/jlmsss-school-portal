from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django.urls import reverse


class SchoolInfo(models.Model):
    """Main school information and configuration"""
    name = models.CharField(max_length=200)
    motto = models.CharField(max_length=300, blank=True)
    logo = models.ImageField(upload_to='school/', blank=True, null=True)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True)
    about = RichTextField()
    vision = RichTextField(blank=True)
    mission = RichTextField(blank=True)
    dotshule_url = models.URLField(default='https://dotshule.ug/', help_text='Government portal URL')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "School Information"
        verbose_name_plural = "School Information"

    def __str__(self):
        return self.name


class HeadteacherMessage(models.Model):
    """Headteacher's or Admin's video message"""
    ADMIN_TYPE_CHOICES = [
        ('headteacher', 'Headteacher'),
        ('deputy', 'Deputy Headteacher'),
        ('principal', 'Principal'),
        ('director', 'Director'),
        ('other', 'Other Administrator'),
    ]
    
    VIDEO_TYPE_CHOICES = [
        ('youtube', 'YouTube URL'),
        ('local', 'Local Video File'),
    ]
    
    title = models.CharField(max_length=200)
    admin_type = models.CharField(max_length=50, choices=ADMIN_TYPE_CHOICES, default='headteacher', help_text='Type of administrator')
    admin_name = models.CharField(max_length=200, blank=True, help_text='Name of the administrator (optional)')
    video_type = models.CharField(max_length=10, choices=VIDEO_TYPE_CHOICES, default='youtube', help_text='Video source type')
    video_url = models.URLField(blank=True, null=True, help_text='YouTube or video embed URL (if video type is YouTube)')
    video_file = models.FileField(upload_to='headteacher/videos/', blank=True, null=True, help_text='Local video file (if video type is local)')
    thumbnail = models.ImageField(upload_to='headteacher/', blank=True, null=True)
    message = RichTextField(help_text='Accompanying text message')
    order = models.IntegerField(default=0, help_text='Display order (lower numbers appear first)')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Administrator Video Message"
        verbose_name_plural = "Administrator Video Messages"
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


class News(models.Model):
    """School news articles"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    image = models.ImageField(upload_to='news/', blank=True, null=True)
    content = RichTextField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey('NewsCategory', on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.CharField(max_length=200, blank=True, help_text='Comma-separated tags')
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    views = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "News"
        verbose_name_plural = "News"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('news_detail', kwargs={'slug': self.slug})
    
    def get_tags_list(self):
        """Return tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []


class Announcement(models.Model):
    """School announcements"""
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

    title = models.CharField(max_length=200)
    content = RichTextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(blank=True, null=True, help_text='Optional expiration date')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Announcement"
        verbose_name_plural = "Announcements"
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return self.title


class GalleryCategory(models.Model):
    """Gallery categories for better organization"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, max_length=100)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Gallery Category"
        verbose_name_plural = "Gallery Categories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gallery', kwargs={'category': self.slug})


class Gallery(models.Model):
    """School photo gallery"""
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='gallery/')
    description = models.TextField(blank=True)
    category = models.ForeignKey(GalleryCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='images')
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Gallery Image"
        verbose_name_plural = "Gallery"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class StudentLeader(models.Model):
    """Student leaders and prefects"""
    POSITION_CHOICES = [
        ('head_prefect', 'Head Prefect'),
        ('deputy_prefect', 'Deputy Prefect'),
        ('academic_prefect', 'Academic Prefect'),
        ('sports_prefect', 'Sports Prefect'),
        ('entertainment_prefect', 'Entertainment Prefect'),
        ('health_prefect', 'Health Prefect'),
        ('library_prefect', 'Library Prefect'),
        ('dormitory_prefect', 'Dormitory Prefect'),
        ('class_representative', 'Class Representative'),
        ('other', 'Other'),
    ]
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    position = models.CharField(max_length=50, choices=POSITION_CHOICES)
    class_level = models.CharField(max_length=50, blank=True, help_text='e.g., S.4, S.5, S.6')
    photo = models.ImageField(upload_to='student_leaders/', blank=True, null=True)
    bio = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    order = models.IntegerField(default=0, help_text='Display order (lower = first)')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Student Leader"
        verbose_name_plural = "Student Leaders"
        ordering = ['order', 'position', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_position_display()}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Department(models.Model):
    """School departments/faculties"""
    name = models.CharField(max_length=200)
    description = RichTextField()
    head = models.CharField(max_length=200, blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Font Awesome icon class')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Staff(models.Model):
    """School staff members"""
    POSITION_CHOICES = [
        ('headteacher', 'Headteacher'),
        ('deputy', 'Deputy Headteacher'),
        ('teacher', 'Teacher'),
        ('administrator', 'Administrator'),
        ('support', 'Support Staff'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    position = models.CharField(max_length=50, choices=POSITION_CHOICES)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, help_text='Primary department')
    departments = models.ManyToManyField(Department, related_name='staff_members', blank=True, help_text='All departments this staff member teaches (can select multiple)')
    photo = models.ImageField(upload_to='staff/', blank=True, null=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Staff Member"
        verbose_name_plural = "Staff"
        ordering = ['position', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Event(models.Model):
    """School events"""
    title = models.CharField(max_length=200)
    description = RichTextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        ordering = ['start_date']

    def __str__(self):
        return self.title
    
    @property
    def event_date(self):
        """Return just the date part for calendar display"""
        return self.start_date.date()


class AdmissionDocument(models.Model):
    """Admission documents and forms"""
    DOCUMENT_TYPE_CHOICES = [
        ('form', 'Admission Form'),
        ('requirements', 'Requirements'),
        ('guidelines', 'Guidelines'),
        ('fee_structure', 'Fee Structure'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES, default='form')
    file = models.FileField(upload_to='admission/documents/')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Admission Document"
        verbose_name_plural = "Admission Documents"
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


class NewsCategory(models.Model):
    """News categories"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#3b82f6', help_text='Hex color code for category badge')

    class Meta:
        verbose_name = "News Category"
        verbose_name_plural = "News Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class AcademicPerformance(models.Model):
    """Academic performance records"""
    YEAR_CHOICES = [
        ('2024', '2024'),
        ('2023', '2023'),
        ('2022', '2022'),
        ('2021', '2021'),
        ('2020', '2020'),
    ]
    
    TERM_CHOICES = [
        ('term1', 'First Term'),
        ('term2', 'Second Term'),
        ('term3', 'Third Term'),
        ('annual', 'Annual'),
    ]
    
    LEVEL_CHOICES = [
        ('s4', 'Senior 4 (UCE)'),
        ('s6', 'Senior 6 (UACE)'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200, help_text='e.g., "S.4 Results 2024" or "First Term 2024"')
    year = models.CharField(max_length=4, choices=YEAR_CHOICES)
    term = models.CharField(max_length=10, choices=TERM_CHOICES, blank=True, help_text='Leave blank for annual results')
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='other')
    description = RichTextField(blank=True)
    document = models.FileField(upload_to='academics/performance/', blank=True, null=True, help_text='PDF or document with detailed results')
    summary = models.TextField(blank=True, help_text='Brief summary of performance')
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Academic Performance"
        verbose_name_plural = "Academic Performance Records"
        ordering = ['-year', '-created_at']

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    """Contact form messages"""
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} - {self.name}"


class Page(models.Model):
    """Custom pages (About, Academics, etc.)"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    content = RichTextField()
    is_published = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Page"
        verbose_name_plural = "Pages"
        ordering = ['order', 'title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('page_detail', kwargs={'slug': self.slug})


class WebsiteConfig(models.Model):
    """Website-wide configuration settings"""
    # Hero Section
    hero_background_image = models.ImageField(upload_to='config/', blank=True, null=True, help_text='Background image for hero section')
    hero_overlay_opacity = models.FloatField(default=0.5, help_text='Overlay opacity (0.0 to 1.0) for background image')
    hero_title = models.CharField(max_length=200, blank=True, help_text='Custom hero title (overrides school name if set)')
    hero_subtitle = models.CharField(max_length=300, blank=True, help_text='Hero subtitle text')
    
    # Navigation
    show_admission_link = models.BooleanField(default=True)
    show_academics_link = models.BooleanField(default=True)
    show_about_link = models.BooleanField(default=True)
    show_login_link = models.BooleanField(default=False, help_text='Show login link in navigation')
    
    # Headteacher Video Section
    headteacher_section_background = models.ImageField(upload_to='config/', blank=True, null=True, help_text='Background image for headteacher message section')
    headteacher_section_overlay_opacity = models.FloatField(default=0.3, help_text='Overlay opacity for headteacher section')
    
    # Home Page
    learn_more_text = models.CharField(max_length=200, blank=True, default='Learn More About Us', help_text='Text for the "Learn More" button on home page')
    learn_more_url = models.CharField(max_length=200, blank=True, help_text='URL for the "Learn More" button (leave blank to use default About Us page)')
    
    # Footer
    footer_text = models.TextField(blank=True, help_text='Custom footer text')
    show_designer_credit = models.BooleanField(default=True)
    designer_name = models.CharField(max_length=100, default='Twiina Technologies', blank=True)
    
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Website Configuration"
        verbose_name_plural = "Website Configuration"
    
    def __str__(self):
        return "Website Configuration"
    
    def save(self, *args, **kwargs):
        # Ensure only one active configuration
        if self.is_active:
            WebsiteConfig.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class ActivityVideo(models.Model):
    title = models.CharField(max_length=200)
    video_file = models.FileField(upload_to='activities/', help_text='Upload the MP4 video file')
    order = models.IntegerField(default=0, help_text='Display order')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Activity Video'
        verbose_name_plural = 'Activity Videos'

    def __str__(self):
        return self.title
