from .models import SchoolInfo, Announcement, WebsiteConfig
from django.db import OperationalError
from django.db.models import Q
from django.utils import timezone


def school_info(request):
    """Add school information to all templates"""
    school = None
    announcements = []
    priority_announcement = None
    website_config = None
    page_hero_title = None
    page_hero_intro = None
    
    try:
        school = SchoolInfo.objects.filter(is_active=True).first()
        # If no active school, get any school
        if not school:
            school = SchoolInfo.objects.first()
    except (OperationalError, Exception) as e:
        # Database not ready or other error
        pass
    
    try:
        now = timezone.now()
        announcements = list(
            Announcement.objects.filter(is_active=True).filter(
                Q(expires_at__isnull=True) | Q(expires_at__gt=now)
            )[:5]
        )

        priority_announcement = (
            Announcement.objects.filter(is_active=True, priority='high')
            .filter(Q(expires_at__isnull=True) | Q(expires_at__gt=now))
            .order_by('-created_at')
            .first()
        )
    except (OperationalError, Exception) as e:
        announcements = []
        priority_announcement = None
    
    try:
        website_config = WebsiteConfig.objects.filter(is_active=True).first()
    except (OperationalError, Exception) as e:
        website_config = None

    try:
        url_name = getattr(getattr(request, 'resolver_match', None), 'url_name', None)
        hero_map = {
            'about_us': ('About Us', 'Learn about our school, our values, and what we stand for.'),
            'academics': ('Academics', 'Explore our academic performance, departments, and learning programs.'),
            'departments': ('Departments', 'Discover the departments that support teaching and learning.'),
            'admission': ('Admissions', 'Find requirements, guidelines, and the steps to join our school.'),
            'staff': ('Staff', 'Meet our dedicated staff and administration.'),
            'news_list': ('News', 'Read the latest updates, stories, and school notices.'),
            'news_detail': ('News', 'Read the full story and related updates.'),
            'announcements': ('Announcements', 'Important updates and notices from the school.'),
            'events': ('Events', 'See upcoming events, activities, and important dates.'),
            'gallery': ('Gallery', 'Browse photos and highlights from school life.'),
            'contact': ('Contact', 'Get in touch with the school for inquiries and support.'),
            'student_life': ('Student Life', 'Explore student activities, clubs, and school culture.'),
            'page_detail': ('Information', 'Learn more about this page and what it offers.'),
            'student_leaders': ('Student Leaders', 'Meet our student leadership team and prefects.'),
        }
        if url_name in hero_map:
            page_hero_title, page_hero_intro = hero_map[url_name]
    except Exception:
        page_hero_title = None
        page_hero_intro = None
    
    return {
        'school_info': school,
        'announcements': announcements,
        'priority_announcement': priority_announcement,
        'website_config': website_config,
        'page_hero_title': page_hero_title,
        'page_hero_intro': page_hero_intro,
    }

