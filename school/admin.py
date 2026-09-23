from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import (
    SchoolInfo, HeadteacherMessage, News, NewsCategory, Announcement,
    Gallery, GalleryCategory, Department, Staff, Event, ContactMessage, Page, WebsiteConfig,
    AdmissionDocument, AcademicPerformance, StudentLeader, ActivityVideo
)


def _thumb(obj, field_name, size=46):
    f = getattr(obj, field_name, None)
    if not f:
        return ""
    try:
        url = f.url
    except Exception:
        return ""
    return format_html(
        '<img src="{}" style="width:{}px;height:{}px;object-fit:cover;border-radius:10px;" />',
        url,
        size,
        size,
    )


@admin.register(SchoolInfo)
class SchoolInfoAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'is_active', 'updated_at']
    list_editable = ['is_active']
    search_fields = ['name', 'email', 'phone']
    list_filter = ['is_active', 'created_at', 'updated_at']
    ordering = ['-updated_at']
    list_per_page = 25
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'motto', 'logo', 'address', 'phone', 'email', 'website')
        }),
        ('About', {
            'fields': ('about', 'vision', 'mission')
        }),
        ('Settings', {
            'fields': ('dotshule_url', 'is_active')
        }),
    )


@admin.register(HeadteacherMessage)
class HeadteacherMessageAdmin(admin.ModelAdmin):
    list_display = ['title', 'admin_type', 'admin_name', 'order', 'is_active', 'created_at']
    list_editable = ['is_active', 'order']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'admin_name', 'message']
    ordering = ['order', '-created_at']
    list_per_page = 25
    fieldsets = (
        ('Message Details', {
            'fields': ('title', 'admin_type', 'admin_name', 'message')
        }),
        ('Video Settings', {
            'fields': ('video_type', 'video_url', 'video_file', 'thumbnail'),
            'description': 'Choose YouTube URL or upload a local video file'
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active')
        }),
    )


@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'slug']
    ordering = ['name']
    list_per_page = 50


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'title', 'category', 'author', 'is_published', 'is_featured', 'views', 'created_at', 'view_on_website']
    list_editable = ['is_published', 'is_featured']
    list_filter = ['category', 'is_published', 'is_featured', 'created_at']
    search_fields = ['title', 'content', 'tags']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views', 'created_at', 'updated_at']
    autocomplete_fields = ['author', 'category']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    list_per_page = 25
    actions = ['make_published', 'make_unpublished', 'make_featured', 'make_unfeatured']
    save_on_top = True
    view_on_site = True

    @admin.display(description='Image')
    def image_preview(self, obj):
        return _thumb(obj, 'image')

    @admin.display(description='View', ordering='slug')
    def view_on_website(self, obj):
        try:
            url = obj.get_absolute_url()
        except Exception:
            return ''
        return format_html('<a class="btn btn-outline-primary" href="{}" target="_blank">View</a>', url)

    @admin.action(description='Publish selected news')
    def make_published(self, request, queryset):
        queryset.update(is_published=True)

    @admin.action(description='Unpublish selected news')
    def make_unpublished(self, request, queryset):
        queryset.update(is_published=False)

    @admin.action(description='Feature selected news')
    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)

    @admin.action(description='Unfeature selected news')
    def make_unfeatured(self, request, queryset):
        queryset.update(is_featured=False)
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'image', 'content')
        }),
        ('Classification', {
            'fields': ('category', 'tags')
        }),
        ('Publishing', {
            'fields': ('author', 'is_published', 'is_featured')
        }),
        ('Statistics', {
            'fields': ('views', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'priority', 'is_active', 'expires_at', 'created_at']
    list_editable = ['is_active', 'priority']
    list_filter = ['priority', 'is_active', 'created_at']
    search_fields = ['title', 'content']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    list_per_page = 25
    actions = ['activate', 'deactivate']
    save_on_top = True
    fieldsets = (
        ('Announcement', {
            'fields': ('title', 'content')
        }),
        ('Priority & Visibility', {
            'fields': ('priority', 'is_active', 'expires_at')
        }),
        ('System', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at']
    view_on_site = True

    def view_on_site(self, obj):
        return reverse('announcements')

    @admin.action(description='Activate selected announcements')
    def activate(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='Deactivate selected announcements')
    def deactivate(self, request, queryset):
        queryset.update(is_active=False)

    def save_model(self, request, obj, form, change):
        """Broadcast email to all applicant accounts when a new announcement is published."""
        is_new = obj.pk is None
        super().save_model(request, obj, form, change)
        if is_new and obj.is_active:
            try:
                from admissions.models import ApplicantAccount
                from admissions.email_utils import send_announcement_email_to_all
                emails = list(
                    ApplicantAccount.objects.filter(
                        email_verified=True, user__is_active=True
                    ).values_list('user__email', flat=True)
                )
                if emails:
                    ok, fail = send_announcement_email_to_all(obj, emails)
                    self.message_user(request, f'Announcement published. Emails sent: {ok}, failed: {fail}.')
            except Exception as e:
                self.message_user(request, f'Announcement saved, but email broadcast error: {e}', level='warning')



@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['is_active']
    search_fields = ['name', 'slug']
    ordering = ['order', 'name']
    list_per_page = 50


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'title', 'category', 'is_featured', 'created_at', 'view_on_website']
    list_editable = ['is_featured']
    list_filter = ['category', 'is_featured', 'created_at']
    search_fields = ['title', 'description']
    autocomplete_fields = ['category']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    list_per_page = 25
    actions = ['make_featured', 'make_unfeatured']
    save_on_top = True
    readonly_fields = ['image_preview', 'created_at']
    view_on_site = True
    fieldsets = (
        ('Media Item', {
            'fields': ('title', 'category', 'description')
        }),
        ('Image', {
            'fields': ('image', 'image_preview')
        }),
        ('Visibility', {
            'fields': ('is_featured',)
        }),
        ('System', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Image')
    def image_preview(self, obj):
        return _thumb(obj, 'image')

    @admin.display(description='View')
    def view_on_website(self, obj):
        url = reverse('gallery')
        if getattr(obj, 'category_id', None) and getattr(obj.category, 'slug', None):
            return format_html(
                '<a class="btn btn-outline-primary" href="{}?category={}" target="_blank">View</a>',
                url,
                obj.category.slug,
            )
        return format_html('<a class="btn btn-outline-primary" href="{}" target="_blank">View</a>', url)

    def view_on_site(self, obj):
        return reverse('gallery')

    @admin.action(description='Feature selected gallery items')
    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)

    @admin.action(description='Unfeature selected gallery items')
    def make_unfeatured(self, request, queryset):
        queryset.update(is_featured=False)


@admin.register(StudentLeader)
class StudentLeaderAdmin(admin.ModelAdmin):
    list_display = ['photo_preview', 'full_name', 'position', 'class_level', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['position', 'is_active', 'class_level']
    search_fields = ['first_name', 'last_name', 'class_level']
    ordering = ['order', 'position', 'last_name']
    list_per_page = 25

    @admin.display(description='Photo')
    def photo_preview(self, obj):
        return _thumb(obj, 'photo')
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'photo', 'bio')
        }),
        ('Position & Class', {
            'fields': ('position', 'class_level')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active')
        }),
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'head', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'head']
    ordering = ['order', 'name']
    list_per_page = 50


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['photo_preview', 'full_name', 'position', 'department', 'phone', 'email', 'is_active']
    list_editable = ['is_active']
    list_filter = ['position', 'department', 'is_active']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    autocomplete_fields = ['user', 'department', 'departments']
    ordering = ['position', 'last_name']
    list_per_page = 25

    @admin.display(description='Photo')
    def photo_preview(self, obj):
        return _thumb(obj, 'photo')
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'photo', 'bio')
        }),
        ('Position & Department', {
            'fields': ('position', 'department')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone')
        }),
        ('Settings', {
            'fields': ('user', 'is_active')
        }),
    )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'title', 'start_date', 'location', 'is_featured', 'view_on_website']
    list_editable = ['is_featured']
    list_filter = ['is_featured', 'start_date']
    search_fields = ['title', 'description', 'location']
    date_hierarchy = 'start_date'
    ordering = ['-start_date']
    list_per_page = 25
    save_on_top = True
    readonly_fields = ['image_preview', 'created_at']
    view_on_site = True
    fieldsets = (
        ('Event Details', {
            'fields': ('title', 'description')
        }),
        ('Schedule & Location', {
            'fields': ('start_date', 'end_date', 'location')
        }),
        ('Media', {
            'fields': ('image', 'image_preview'),
            'classes': ('collapse',),
        }),
        ('Visibility', {
            'fields': ('is_featured',),
        }),
        ('System', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Image')
    def image_preview(self, obj):
        return _thumb(obj, 'image')

    @admin.display(description='View')
    def view_on_website(self, obj):
        url = reverse('events')
        return format_html('<a class="btn btn-outline-primary" href="{}" target="_blank">View</a>', url)

    def view_on_site(self, obj):
        return reverse('events')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_editable = ['is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['name', 'email', 'phone', 'subject', 'message', 'created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    list_per_page = 25
    actions = ['mark_read', 'mark_unread']
    save_on_top = True

    @admin.action(description='Mark selected messages as read')
    def mark_read(self, request, queryset):
        queryset.update(is_read=True)

    @admin.action(description='Mark selected messages as unread')
    def mark_unread(self, request, queryset):
        queryset.update(is_read=False)


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'is_published', 'order', 'updated_at', 'view_on_website']
    list_editable = ['is_published', 'order']
    list_filter = ['is_published', 'created_at']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'updated_at'
    ordering = ['order', 'title']
    list_per_page = 25
    save_on_top = True
    fieldsets = (
        ('Page Content', {
            'fields': ('title', 'slug', 'content')
        }),
        ('Publishing', {
            'fields': ('is_published', 'order')
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']
    view_on_site = True

    @admin.display(description='View', ordering='slug')
    def view_on_website(self, obj):
        try:
            url = obj.get_absolute_url()
        except Exception:
            return ''
        return format_html('<a class="btn btn-outline-primary" href="{}" target="_blank">View</a>', url)


@admin.register(AdmissionDocument)
class AdmissionDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'document_type', 'is_active', 'order', 'created_at']
    list_editable = ['is_active', 'order']
    list_filter = ['document_type', 'is_active', 'created_at']
    search_fields = ['title', 'description']
    date_hierarchy = 'created_at'
    ordering = ['order', '-created_at']
    list_per_page = 25


@admin.register(AcademicPerformance)
class AcademicPerformanceAdmin(admin.ModelAdmin):
    list_display = ['title', 'year', 'term', 'level', 'is_published', 'created_at']
    list_editable = ['is_published']
    list_filter = ['year', 'term', 'level', 'is_published', 'created_at']
    search_fields = ['title', 'description', 'summary']
    date_hierarchy = 'created_at'
    ordering = ['-year', '-created_at']
    list_per_page = 25
    fieldsets = (
        ('Performance Details', {
            'fields': ('title', 'year', 'term', 'level', 'description', 'summary')
        }),
        ('Document', {
            'fields': ('document',)
        }),
        ('Status', {
            'fields': ('is_published',)
        }),
    )


@admin.register(WebsiteConfig)
class WebsiteConfigAdmin(admin.ModelAdmin):
    list_display = ['is_active', 'updated_at']
    ordering = ['-updated_at']
    list_per_page = 25
    save_on_top = True
    view_on_site = True
    readonly_fields = ['updated_at']
    fieldsets = (
        ('Hero Section', {
            'fields': ('hero_background_image', 'hero_overlay_opacity', 'hero_title', 'hero_subtitle'),
            'description': 'Configure the hero section background image and overlay. The background image will appear behind the entire hero section including the video.'
        }),
        ('Navigation Settings', {
            'fields': ('show_admission_link', 'show_academics_link', 'show_about_link', 'show_login_link')
        }),
        ('Home Page Settings', {
            'fields': ('learn_more_text', 'learn_more_url'),
            'description': 'Configure the "Learn More About Us" button on the home page'
        }),
        ('Headteacher Section', {
            'fields': ('headteacher_section_background', 'headteacher_section_overlay_opacity'),
            'description': 'Background image for the headteacher message section (if used separately)'
        }),
        ('Footer Settings', {
            'fields': ('footer_text', 'show_designer_credit', 'designer_name')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def changelist_view(self, request, extra_context=None):
        # Auto-create WebsiteConfig if it doesn't exist
        try:
            if not WebsiteConfig.objects.exists():
                WebsiteConfig.objects.create(is_active=True)
        except Exception:
            pass
        return super().changelist_view(request, extra_context)
    
    def has_add_permission(self, request):
        # Always allow adding if none exists
        try:
            return not WebsiteConfig.objects.exists()
        except Exception:
            return True
    
    def has_delete_permission(self, request, obj=None):
        return False

    def view_on_site(self, obj):
        return reverse('home')


@admin.register(ActivityVideo)
class ActivityVideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'is_active', 'created_at']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title']
    ordering = ['order', '-created_at']
