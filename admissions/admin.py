"""
admissions/admin.py — Django admin config for JLMSSS Admission Portal v2
Provides rich views for admin staff to manage applicants, accounts, and applications.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.auth.models import User
from .models import (
    PaymentConfig, AdmissionWindow, WindowEntryClass, DocumentSlot,
    AdmissionForm, FormSection, FormField, FieldOption,
    ApplicantAccount, StudentProfile, Application, ApplicationDocument,
    AdminFeedback, AuditLog, NotificationLog, TransferInfo, Interview,
    EmailVerificationToken, PasswordResetToken,
)


# ============================================================================
# PAYMENT CONFIG
# ============================================================================

@admin.register(PaymentConfig)
class PaymentConfigAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'mtn_number', 'airtel_number', 'bank_name', 'is_active', 'updated_at']
    list_editable = ['is_active']


# ============================================================================
# ADMISSION WINDOW
# ============================================================================

class WindowEntryClassInline(admin.TabularInline):
    model = WindowEntryClass
    extra = 1


class DocumentSlotInline(admin.TabularInline):
    model = DocumentSlot
    extra = 1


@admin.register(AdmissionWindow)
class AdmissionWindowAdmin(admin.ModelAdmin):
    list_display = ['name', 'academic_year', 'term', 'opening_date', 'closing_date', 'application_fee', 'is_active']
    list_editable = ['is_active']
    inlines = [WindowEntryClassInline, DocumentSlotInline]
    prepopulated_fields = {'slug': ('name',)}


# ============================================================================
# FORMS
# ============================================================================

class FormSectionInline(admin.TabularInline):
    model = FormSection
    extra = 1


@admin.register(AdmissionForm)
class AdmissionFormAdmin(admin.ModelAdmin):
    list_display = ['title', 'window', 'entry_class', 'is_active']
    list_filter = ['window', 'entry_class']
    inlines = [FormSectionInline]


class FieldOptionInline(admin.TabularInline):
    model = FieldOption
    extra = 1


@admin.register(FormField)
class FormFieldAdmin(admin.ModelAdmin):
    list_display = ['label', 'section', 'field_type', 'is_required', 'order']
    list_filter = ['section__form__window', 'field_type']
    inlines = [FieldOptionInline]


# ============================================================================
# APPLICANT ACCOUNTS  ← main admin view for all registrations
# ============================================================================

@admin.register(ApplicantAccount)
class ApplicantAccountAdmin(admin.ModelAdmin):
    list_display = [
        'full_name_display', 'email_display', 'phone',
        'email_verified_badge', 'student_count',
        'district', 'created_at',
    ]
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name', 'phone',
        'district',
    ]
    list_filter = ['email_verified', 'district', 'created_at']
    readonly_fields = ['created_at', 'updated_at', 'full_name_display', 'email_display']
    ordering = ['-created_at']

    # ---- custom display columns ----

    @admin.display(description='Full Name', ordering='user__first_name')
    def full_name_display(self, obj):
        name = obj.user.get_full_name().strip()
        return name if name else obj.user.username

    @admin.display(description='Email', ordering='user__email')
    def email_display(self, obj):
        return format_html('<a href="mailto:{0}">{0}</a>', obj.user.email)

    @admin.display(description='Email Verified')
    def email_verified_badge(self, obj):
        if obj.email_verified:
            return format_html('<span style="color:green;font-weight:bold;">✔ Verified</span>')
        return format_html('<span style="color:red;">✘ Pending</span>')

    @admin.display(description='Students')
    def student_count(self, obj):
        count = obj.students.count()
        return format_html('<b>{}</b>', count)


# ============================================================================
# STUDENT PROFILES
# ============================================================================

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'gender', 'date_of_birth',
        'account_holder_name', 'account_phone',
        'guardian_name', 'guardian_phone',
    ]
    search_fields = [
        'first_name', 'last_name', 'guardian_name',
        'guardian_phone', 'account__user__email',
        'account__user__first_name', 'account__user__last_name',
        'account__phone',
    ]
    list_filter = ['gender']

    @admin.display(description='Account Holder')
    def account_holder_name(self, obj):
        return obj.account.full_name

    @admin.display(description='Account Phone')
    def account_phone(self, obj):
        return obj.account.phone


# ============================================================================
# APPLICATIONS
# ============================================================================

class ApplicationDocumentInline(admin.TabularInline):
    model = ApplicationDocument
    extra = 0
    readonly_fields = ['uploaded_at', 'status']


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'application_number', 'student_name_display',
        'applicant_name_display', 'applicant_phone_display',
        'window', 'entry_class', 'status_badge',
        'payment_verified', 'created_at',
    ]
    list_filter = ['status', 'window', 'entry_class', 'payment_verified', 'is_transfer']
    search_fields = [
        'application_number',
        'student__first_name', 'student__last_name',
        'applicant__user__email',
        'applicant__user__first_name', 'applicant__user__last_name',
        'applicant__phone',
    ]
    inlines = [ApplicationDocumentInline]
    readonly_fields = [
        'application_number', 'created_at', 'updated_at',
        'submitted_at', 'offer_generated_at', 'offer_accepted_at',
    ]
    ordering = ['-created_at']

    @admin.display(description='Student Name')
    def student_name_display(self, obj):
        if obj.student:
            return obj.student.full_name
        return '—'

    @admin.display(description='Applicant / Guardian')
    def applicant_name_display(self, obj):
        return obj.applicant.full_name

    @admin.display(description='Phone')
    def applicant_phone_display(self, obj):
        return obj.applicant.phone or '—'

    STATUS_COLORS = {
        'draft': '#888',
        'submitted': '#1a73e8',
        'under_doc_review': '#f09300',
        'action_required': '#e53935',
        'docs_resubmitted': '#7b61ff',
        'approved': '#0288d1',
        'provisionally_admitted': '#2e7d32',
        'enrolled': '#1b5e20',
        'rejected': '#c62828',
        'withdrawn': '#555',
    }

    @admin.display(description='Status', ordering='status')
    def status_badge(self, obj):
        color = self.STATUS_COLORS.get(obj.status, '#888')
        label = obj.get_status_display()
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:4px;font-size:11px;">{}</span>',
            color, label,
        )


# ============================================================================
# ADMIN FEEDBACK
# ============================================================================

@admin.register(AdminFeedback)
class AdminFeedbackAdmin(admin.ModelAdmin):
    list_display = ['application', 'feedback_type', 'subject', 'sent_by', 'is_sent', 'created_at']
    list_filter = ['feedback_type', 'is_sent']


# ============================================================================
# AUDIT / NOTIFICATION LOGS (read-only)
# ============================================================================

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'staff', 'action', 'application']
    list_filter = ['timestamp', 'staff']
    search_fields = ['action', 'details', 'application__application_number']
    readonly_fields = ['timestamp', 'staff', 'action', 'details', 'application', 'ip_address']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ['sent_at', 'recipient_email', 'subject', 'channel', 'status']
    list_filter = ['status', 'channel', 'sent_at']
    search_fields = ['recipient_email', 'subject']
    readonly_fields = ['sent_at', 'recipient_email', 'subject', 'body_preview', 'channel', 'status', 'error_message']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# ============================================================================
# MISC (simple registrations)
# ============================================================================

admin.site.register(TransferInfo)
admin.site.register(Interview)
admin.site.register(EmailVerificationToken)
admin.site.register(PasswordResetToken)
