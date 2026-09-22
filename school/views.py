from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from .models import (
    SchoolInfo, HeadteacherMessage, News, NewsCategory, Announcement,
    Gallery, GalleryCategory, Department, Staff, Event, ContactMessage, Page, WebsiteConfig,
    AdmissionDocument, AcademicPerformance, StudentLeader, ActivityVideo
)
from .forms import ContactForm

from pathlib import Path


def home(request):
    """Home page"""
    try:
        admin_messages = HeadteacherMessage.objects.filter(is_active=True).order_by('order', '-created_at')[:1]  # Get first admin message for hero
        hero_video = admin_messages.first() if admin_messages.exists() else None
    except Exception:
        admin_messages = []
        hero_video = None
    # Removed news and events from home page as they have their own pages
    featured_gallery = Gallery.objects.filter(is_featured=True)[:6]

    hero_slides = Gallery.objects.all().order_by('-is_featured', '-created_at')[:6]

    hero_static_slides = [
        'img/hero_uniform.jpg',
    ]

    hero_carousel_slides = [
        {'src_static': s, 'alt': 'Janan Luwum Memorial SSS Students'}
        for s in hero_static_slides
    ]
    # Get total staff count for stats
    total_staff_count = Staff.objects.filter(is_active=True).count()

    latest_news = News.objects.filter(is_published=True).select_related('category')[:3]
    departments_preview = Department.objects.filter(is_active=True).order_by('order', 'name')[:6]
    upcoming_events = Event.objects.all().order_by('start_date')[:3]

    try:
        activity_videos = ActivityVideo.objects.filter(is_active=True).order_by('order', '-created_at')[:6]
    except Exception:
        activity_videos = []
    
    context = {
        'admin_messages': admin_messages,
        'hero_video': hero_video,
        'hero_slides': hero_slides,
        'hero_static_slides': hero_static_slides,
        'hero_carousel_slides': hero_carousel_slides,
        'featured_gallery': featured_gallery,
        'total_staff_count': total_staff_count,
        'latest_news': latest_news,
        'departments_preview': departments_preview,
        'upcoming_events': upcoming_events,
        'activity_videos': activity_videos,
    }
    return render(request, 'school/home.html', context)


def news_list(request):
    """List all news articles"""
    try:
        news_list = News.objects.filter(is_published=True)
        try:
            categories = NewsCategory.objects.all()
        except Exception:
            categories = []
        
        # Filter by category
        category_slug = request.GET.get('category', '')
        if category_slug:
            try:
                category = NewsCategory.objects.get(slug=category_slug)
                news_list = news_list.filter(category=category)
            except (NewsCategory.DoesNotExist, Exception):
                pass
        
        # Search functionality
        search_query = request.GET.get('search', '')
        if search_query:
            try:
                news_list = news_list.filter(
                    Q(title__icontains=search_query) |
                    Q(content__icontains=search_query) |
                    Q(tags__icontains=search_query)
                )
            except Exception:
                news_list = news_list.filter(
                    Q(title__icontains=search_query) |
                    Q(content__icontains=search_query)
                )
    except Exception:
        news_list = News.objects.none()
        categories = []
        search_query = ''
        category_slug = ''
    
    paginator = Paginator(news_list, 9)
    page_number = request.GET.get('page')
    news = paginator.get_page(page_number)
    
    context = {
        'news': news,
        'categories': categories,
        'search_query': search_query,
        'category_slug': category_slug,
    }
    return render(request, 'school/news_list.html', context)


def news_detail(request, slug):
    """News article detail page"""
    news = get_object_or_404(News, slug=slug, is_published=True)
    news.views += 1
    news.save(update_fields=['views'])
    
    related_news = News.objects.filter(is_published=True).exclude(id=news.id)[:3]
    
    context = {
        'news': news,
        'related_news': related_news,
    }
    return render(request, 'school/news_detail.html', context)


def announcements(request):
    """All announcements"""
    now = timezone.now()
    announcements_list = Announcement.objects.filter(is_active=True).filter(
        Q(expires_at__isnull=True) | Q(expires_at__gt=now)
    )
    
    context = {
        'announcements': announcements_list,
    }
    return render(request, 'school/announcements.html', context)


def gallery(request):
    """Photo gallery"""
    galleries = Gallery.objects.all()
    category_slug = request.GET.get('category', '')
    
    if category_slug:
        try:
            category = GalleryCategory.objects.get(slug=category_slug, is_active=True)
            galleries = galleries.filter(category=category)
        except GalleryCategory.DoesNotExist:
            category = None
    else:
        category = None
    
    # Get all active categories
    categories = GalleryCategory.objects.filter(is_active=True).order_by('order', 'name')
    
    paginator = Paginator(galleries, 12)
    page_number = request.GET.get('page')
    galleries = paginator.get_page(page_number)
    
    context = {
        'galleries': galleries,
        'categories': categories,
        'category_filter': category_slug,
        'selected_category': category,
    }
    return render(request, 'school/gallery.html', context)


def student_leaders(request):
    """Student leaders page"""
    leaders = StudentLeader.objects.filter(is_active=True).order_by('order', 'position', 'last_name')
    
    # Group by position
    leaders_by_position = {}
    for leader in leaders:
        position = leader.get_position_display()
        if position not in leaders_by_position:
            leaders_by_position[position] = []
        leaders_by_position[position].append(leader)
    
    context = {
        'leaders': leaders,
        'leaders_by_position': leaders_by_position,
    }
    return render(request, 'school/student_leaders.html', context)


def staff_list(request):
    """Staff directory"""
    staff_list = Staff.objects.filter(is_active=True)
    
    position_filter = request.GET.get('position', '')
    if position_filter:
        staff_list = staff_list.filter(position=position_filter)
    
    departments = Department.objects.filter(is_active=True)
    
    context = {
        'staff': staff_list,
        'departments': departments,
        'position_filter': position_filter,
    }
    return render(request, 'school/staff.html', context)


def departments(request):
    """Departments page"""
    departments = Department.objects.filter(is_active=True)
    department_slug = request.GET.get('dept', '')
    selected_department = None
    department_staff = []
    
    if department_slug:
        try:
            selected_department = Department.objects.get(slug=department_slug, is_active=True)
            # Get staff from primary department
            department_staff = Staff.objects.filter(
                department=selected_department,
                is_active=True
            )
            # Try to get from many-to-many if it exists
            try:
                m2m_staff = Staff.objects.filter(
                    departments=selected_department,
                    is_active=True
                )
                department_staff = (department_staff | m2m_staff).distinct()
            except Exception:
                pass
        except Department.DoesNotExist:
            pass
    
    context = {
        'departments': departments,
        'selected_department': selected_department,
        'department_staff': department_staff,
    }
    return render(request, 'school/departments.html', context)


def events(request):
    """Events calendar"""
    events_list = Event.objects.all().order_by('start_date')
    
    # Group events by month for calendar view
    from collections import defaultdict
    events_by_month = defaultdict(list)
    
    for event in events_list:
        try:
            month_key = event.start_date.strftime('%Y-%m')
            events_by_month[month_key].append(event)
        except Exception:
            pass
    
    context = {
        'events': events_list,
        'events_by_month': dict(events_by_month),
    }
    return render(request, 'school/events.html', context)


def contact(request):
    """Contact page"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return redirect('contact')
    else:
        form = ContactForm()
    
    context = {
        'form': form,
    }
    return render(request, 'school/contact.html', context)


def page_detail(request, slug):
    """Custom page detail"""
    page = get_object_or_404(Page, slug=slug, is_published=True)
    
    context = {
        'page': page,
    }
    return render(request, 'school/page_detail.html', context)


def student_life(request):
    page = get_object_or_404(Page, slug='student-life', is_published=True)
    return render(request, 'school/page_detail.html', {'page': page})



def academics(request):
    """Academics page"""
    try:
        performance_records = AcademicPerformance.objects.filter(is_published=True).order_by('-year', '-created_at')
    except Exception:
        performance_records = []
    try:
        page = Page.objects.get(slug='academics', is_published=True)
        return render(request, 'school/page_detail.html', {'page': page, 'performance_records': performance_records})
    except Page.DoesNotExist:
        return render(request, 'school/academics.html', {'performance_records': performance_records})


def about_us(request):
    """About Us page"""
    school_info = SchoolInfo.objects.filter(is_active=True).first()
    return render(request, 'school/about.html', {'school_info': school_info})


def dotshule_login(request):
    """Redirect to dotShule portal for login"""
    school_info = SchoolInfo.objects.filter(is_active=True).first()
    dotshule_url = school_info.dotshule_url if school_info else 'https://dotshule.ug/'
    return redirect(dotshule_url)
