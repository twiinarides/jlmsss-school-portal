"""
admissions/models.py — JLMSSS Admission Portal v2
Complete rebuild with StudentProfile, DocumentSlot, ApplicationDocument,
EmailVerificationToken, AdminFeedback, AuditLog, NotificationLog.
"""

import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify


# ============================================================================
# CHOICES
# ============================================================================

ENTRY_CLASS_CHOICES = [
    ('s1', 'Senior 1'), ('s2', 'Senior 2'), ('s3', 'Senior 3'),
    ('s4', 'Senior 4'), ('s5', 'Senior 5'), ('s6', 'Senior 6'),
]

INTAKE_TYPE_CHOICES = [
    ('new', 'New Entrant'), ('transfer', 'Transfer Student'), ('both', 'New & Transfer'),
]

TERM_CHOICES = [
    ('term1', 'Term 1'), ('term2', 'Term 2'), ('term3', 'Term 3'), ('full_year', 'Full Year'),
]

FIELD_TYPE_CHOICES = [
    ('text', 'Short Text'), ('textarea', 'Long Text'), ('email', 'Email Address'),
    ('phone', 'Phone Number'), ('number', 'Number'), ('date', 'Date'),
    ('select', 'Dropdown'), ('radio', 'Radio Buttons'), ('checkbox', 'Checkboxes'),
    ('heading', 'Section Heading'), ('paragraph', 'Informational Paragraph'),
]

APPLICATION_STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('submitted', 'Submitted'),
    ('under_doc_review', 'Under Document Review'),
    ('action_required', 'Action Required / Resubmission Needed'),
    ('docs_resubmitted', 'Documents Resubmitted'),
    ('approved', 'Approved'),
    ('provisionally_admitted', 'Provisionally Admitted'),
    ('enrolled', 'Enrolled'),
    ('rejected', 'Rejected'),
    ('withdrawn', 'Withdrawn'),
]

DOCUMENT_STATUS_CHOICES = [
    ('pending', 'Pending Review'),
    ('approved', 'Approved'),
    ('flagged', 'Flagged / Rejected'),
]

GENDER_CHOICES = [
    ('male', 'Male'), ('female', 'Female'), ('other', 'Other / Prefer not to say'),
]

FEEDBACK_TYPE_CHOICES = [
    ('action_required', 'Action Required'),
    ('general_info', 'General Information'),
    ('rejection_notice', 'Rejection Notice'),
    ('congratulations', 'Congratulations / Offer'),
]

CONDITION_OPERATOR_CHOICES = [
    ('eq', 'Equals'), ('neq', 'Not Equals'), ('contains', 'Contains'),
]

LANGUAGE_CHOICES = [
    ('en', 'English'), ('lg', 'Luganda'), ('rk', 'Runyakore-Rukiga'),
]

INTERVIEW_OUTCOME_CHOICES = [
    ('pending', 'Pending'), ('passed', 'Passed'), ('failed', 'Failed'),
]

# Status pipeline order for progress bar display
STATUS_ORDER = [
    'draft', 'submitted', 'under_doc_review', 'action_required',
    'docs_resubmitted', 'approved', 'provisionally_admitted', 'enrolled',
]

STATUS_DISPLAY_PIPELINE = [
    ('draft', 'Draft', 'fas fa-pen'),
    ('submitted', 'Submitted', 'fas fa-paper-plane'),
    ('under_doc_review', 'Under Review', 'fas fa-search'),
    ('approved', 'Approved', 'fas fa-check-circle'),
    ('provisionally_admitted', 'Provisionally Admitted', 'fas fa-graduation-cap'),
    ('enrolled', 'Enrolled', 'fas fa-school'),
]


# ============================================================================
# PAYMENT CONFIG
# ============================================================================

class PaymentConfig(models.Model):
    """School's payment account details for application fees."""
    mtn_number = models.CharField(max_length=20, blank=True, verbose_name='MTN Mobile Money Number')
    mtn_name = models.CharField(max_length=200, blank=True, verbose_name='MTN Account Name')
    airtel_number = models.CharField(max_length=20, blank=True, verbose_name='Airtel Money Number')
    airtel_name = models.CharField(max_length=200, blank=True, verbose_name='Airtel Account Name')
    bank_name = models.CharField(max_length=200, blank=True, verbose_name='Bank Name')
    bank_account = models.CharField(max_length=100, blank=True, verbose_name='Bank Account Number')
    bank_branch = models.CharField(max_length=200, blank=True, verbose_name='Bank Branch')
    bank_swift = models.CharField(max_length=20, blank=True, verbose_name='SWIFT / Sort Code')
    additional_instructions = models.TextField(blank=True, verbose_name='Additional Payment Instructions')
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Payment Configuration'
        verbose_name_plural = 'Payment Configuration'

    def __str__(self):
        return 'Payment Configuration'

    def save(self, *args, **kwargs):
        if self.is_active:
            PaymentConfig.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


# ============================================================================
# ADMISSION WINDOW
# ============================================================================

class AdmissionWindow(models.Model):
    """A time-bounded period during which the school accepts applications."""
    name = models.CharField(max_length=200, verbose_name='Window Name')
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    academic_year = models.CharField(max_length=20, verbose_name='Academic Year', help_text='e.g. 2025/2026')
    term = models.CharField(max_length=20, choices=TERM_CHOICES, verbose_name='Term')
    description = models.TextField(blank=True, verbose_name='Description')
    opening_date = models.DateTimeField(verbose_name='Opening Date & Time')
    closing_date = models.DateTimeField(verbose_name='Closing Date & Time')
    is_active = models.BooleanField(default=True, verbose_name='Active')
    application_fee = models.DecimalField(
        max_digits=10, decimal_places=0, null=True, blank=True,
        verbose_name='Application Fee (UGX)', help_text='Leave blank if no fee is required.',
    )
    interview_required = models.BooleanField(default=False, verbose_name='Interview Required')
    interview_details = models.TextField(blank=True, verbose_name='Interview Details')
    eligibility_rules = models.TextField(blank=True, verbose_name='Eligibility Rules')
    max_total_students = models.IntegerField(null=True, blank=True, verbose_name='Maximum Total Students')
    offer_letter_intro = models.TextField(
        blank=True, verbose_name='Offer Letter Introduction',
        help_text='Opening paragraph for auto-generated offer letters for this window.',
    )
    resubmission_deadline_days = models.IntegerField(
        default=7, verbose_name='Resubmission Deadline (days)',
        help_text='Days given to applicants to correct flagged documents.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-opening_date']
        verbose_name = 'Admission Window'
        verbose_name_plural = 'Admission Windows'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while AdmissionWindow.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def is_open(self):
        if not self.is_active:
            return False
        now = timezone.now()
        return self.opening_date <= now <= self.closing_date

    @property
    def accepted_count(self):
        return self.applications.filter(status='approved').count()

    @property
    def spots_remaining(self):
        if self.max_total_students is None:
            return None
        return max(0, self.max_total_students - self.accepted_count)


# ============================================================================
# WINDOW ENTRY CLASS
# ============================================================================

class WindowEntryClass(models.Model):
    """Classes available within an AdmissionWindow."""
    window = models.ForeignKey(AdmissionWindow, on_delete=models.CASCADE, related_name='entry_classes')
    entry_class = models.CharField(max_length=5, choices=ENTRY_CLASS_CHOICES, verbose_name='Class')
    intake_type = models.CharField(max_length=10, choices=INTAKE_TYPE_CHOICES, default='both')
    max_students = models.IntegerField(null=True, blank=True, verbose_name='Vacancies')
    is_open = models.BooleanField(default=True, verbose_name='Open for Applications')
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'entry_class']
        unique_together = [('window', 'entry_class')]
        verbose_name = 'Entry Class'
        verbose_name_plural = 'Entry Classes'

    def __str__(self):
        return f'{self.window} — {self.get_entry_class_display()}'

    @property
    def spots_remaining(self):
        if self.max_students is None:
            return None
        accepted = self.window.applications.filter(entry_class=self.entry_class, status='approved').count()
        return max(0, self.max_students - accepted)


# ============================================================================
# DOCUMENT SLOT
# ============================================================================

class DocumentSlot(models.Model):
    """
    A required document slot for an AdmissionWindow.
    Defines what documents must be uploaded (e.g. Birth Certificate, PLE Results).
    """
    window = models.ForeignKey(
        AdmissionWindow, on_delete=models.CASCADE, related_name='document_slots',
        verbose_name='Admission Window',
    )
    name = models.CharField(max_length=200, verbose_name='Document Name')
    slot_key = models.SlugField(max_length=100, verbose_name='Slot Key')
    description = models.TextField(blank=True, verbose_name='Description / Instructions')
    is_required = models.BooleanField(default=True, verbose_name='Required')
    accepted_types = models.CharField(
        max_length=100, default='pdf,jpg,jpeg,png',
        verbose_name='Accepted File Types',
        help_text='Comma-separated, e.g. pdf,jpg,png',
    )
    max_size_mb = models.IntegerField(default=5, verbose_name='Max File Size (MB)')
    order = models.IntegerField(default=0, verbose_name='Display Order')
    icon = models.CharField(
        max_length=50, default='fas fa-file-alt',
        verbose_name='Icon (Font Awesome class)',
    )

    class Meta:
        ordering = ['order', 'name']
        unique_together = [('window', 'slot_key')]
        verbose_name = 'Document Slot'
        verbose_name_plural = 'Document Slots'

    def __str__(self):
        return f'{self.window} — {self.name}'

    def save(self, *args, **kwargs):
        if not self.slot_key:
            self.slot_key = slugify(self.name)[:90]
        super().save(*args, **kwargs)

    @property
    def accepted_types_list(self):
        return [t.strip().lstrip('.').lower() for t in self.accepted_types.split(',')]

    @property
    def accepted_types_for_input(self):
        return ','.join(f'.{t.strip().lstrip(".")}' for t in self.accepted_types.split(','))

    @property
    def document_name(self):
        """Alias for name — used in templates."""
        return self.name

    @property
    def accepted_formats(self):
        """Human-readable accepted formats string."""
        return ', '.join(t.strip().upper() for t in self.accepted_types.split(','))


# ============================================================================
# ADMISSION FORM (Dynamic form builder — kept from v1)
# ============================================================================

class AdmissionForm(models.Model):
    window = models.ForeignKey(AdmissionWindow, on_delete=models.CASCADE, related_name='forms')
    entry_class = models.CharField(max_length=5, choices=ENTRY_CLASS_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('window', 'entry_class')]
        verbose_name = 'Admission Form'
        verbose_name_plural = 'Admission Forms'

    def __str__(self):
        return f'{self.window} — {self.get_entry_class_display()} Form'


class FormSection(models.Model):
    form = models.ForeignKey(AdmissionForm, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=200, verbose_name='Title (English)')
    title_luganda = models.CharField(max_length=200, blank=True)
    title_runyakore = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    icon = models.CharField(max_length=60, default='fas fa-list', blank=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Form Section'
        verbose_name_plural = 'Form Sections'

    def __str__(self):
        return f'{self.form} — {self.title}'


class FormField(models.Model):
    section = models.ForeignKey(FormSection, on_delete=models.CASCADE, related_name='fields')
    label = models.CharField(max_length=300, verbose_name='Label (English)')
    label_luganda = models.CharField(max_length=300, blank=True)
    label_runyakore = models.CharField(max_length=300, blank=True)
    field_key = models.SlugField(max_length=100, blank=True)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPE_CHOICES)
    is_required = models.BooleanField(default=True)
    help_text = models.TextField(blank=True)
    placeholder = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)
    condition_field = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='dependent_fields',
    )
    condition_operator = models.CharField(max_length=20, choices=CONDITION_OPERATOR_CHOICES, blank=True)
    condition_value = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Form Field'
        verbose_name_plural = 'Form Fields'

    def __str__(self):
        return f'{self.label} ({self.get_field_type_display()})'

    def save(self, *args, **kwargs):
        if not self.field_key:
            base_key = slugify(self.label)[:90]
            key = base_key
            counter = 1
            qs = FormField.objects.filter(section__form=self.section.form, field_key=key).exclude(pk=self.pk)
            while qs.exists():
                key = f'{base_key}-{counter}'
                counter += 1
                qs = FormField.objects.filter(section__form=self.section.form, field_key=key).exclude(pk=self.pk)
            self.field_key = key
        super().save(*args, **kwargs)


class FieldOption(models.Model):
    field = models.ForeignKey(FormField, on_delete=models.CASCADE, related_name='options')
    label = models.CharField(max_length=200)
    label_luganda = models.CharField(max_length=200, blank=True)
    label_runyakore = models.CharField(max_length=200, blank=True)
    value = models.CharField(max_length=100)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.label


# ============================================================================
# APPLICANT ACCOUNT (extended from v1)
# ============================================================================

class ApplicantAccount(models.Model):
    """
    Profile for the logged-in user (student applying directly, or parent/guardian).
    One account can manage multiple StudentProfile children.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='applicant_profile')
    phone = models.CharField(max_length=20, verbose_name='Phone Number')
    date_of_birth = models.DateField(null=True, blank=True)
    district = models.CharField(max_length=100, blank=True)
    nationality = models.CharField(max_length=100, blank=True, default='Ugandan')
    preferred_language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')
    # NEW v2 fields
    email_verified = models.BooleanField(default=False, verbose_name='Email Verified')
    profile_photo = models.ImageField(upload_to='admissions/profile_photos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Applicant Profile'
        verbose_name_plural = 'Applicant Profiles'

    def __str__(self):
        return str(self.user)

    @property
    def full_name(self):
        name = self.user.get_full_name()
        return name.strip() if name.strip() else self.user.username

    @property
    def initials(self):
        parts = self.full_name.split()
        if len(parts) >= 2:
            return f'{parts[0][0]}{parts[-1][0]}'.upper()
        return self.full_name[:2].upper()


# ============================================================================
# STUDENT PROFILE (NEW v2)
# ============================================================================

class StudentProfile(models.Model):
    """
    Represents the student/child whose application it is.
    One ApplicantAccount (parent or student) can own multiple StudentProfiles.
    """
    account = models.ForeignKey(
        ApplicantAccount, on_delete=models.CASCADE, related_name='students',
        verbose_name='Account Holder',
    )
    # Bio-data
    first_name = models.CharField(max_length=100, verbose_name='First Name')
    last_name = models.CharField(max_length=100, verbose_name='Last Name')
    other_names = models.CharField(max_length=100, blank=True, verbose_name='Other Names')
    date_of_birth = models.DateField(verbose_name='Date of Birth')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name='Gender')
    nationality = models.CharField(max_length=100, default='Ugandan', verbose_name='Nationality')
    district_of_origin = models.CharField(max_length=100, blank=True, verbose_name='District of Origin')
    religion = models.CharField(max_length=100, blank=True, verbose_name='Religion')
    passport_photo = models.ImageField(
        upload_to='admissions/passport_photos/', null=True, blank=True,
        verbose_name='Passport Photo',
    )
    # Medical / Special Needs
    has_special_needs = models.BooleanField(default=False, verbose_name='Has Special Needs / Disabilities')
    special_needs_details = models.TextField(blank=True, verbose_name='Special Needs Details')
    medical_conditions = models.TextField(blank=True, verbose_name='Medical Conditions')
    blood_group = models.CharField(max_length=10, blank=True, verbose_name='Blood Group')
    # Guardian / Contact
    guardian_name = models.CharField(max_length=200, verbose_name='Guardian Full Name')
    guardian_relationship = models.CharField(
        max_length=50, verbose_name='Relationship to Student',
        help_text='e.g. Father, Mother, Uncle, Legal Guardian',
    )
    guardian_phone = models.CharField(max_length=20, verbose_name='Guardian Phone Number')
    guardian_email = models.EmailField(blank=True, verbose_name='Guardian Email')
    guardian_occupation = models.CharField(max_length=200, blank=True, verbose_name='Guardian Occupation')
    guardian_address = models.TextField(blank=True, verbose_name='Guardian Address')
    # Emergency contact (second guardian)
    emergency_contact_name = models.CharField(max_length=200, blank=True, verbose_name='Emergency Contact Name')
    emergency_contact_phone = models.CharField(max_length=20, blank=True, verbose_name='Emergency Contact Phone')
    # Co-curricular
    cocurricular_interests = models.TextField(blank=True, verbose_name='Co-curricular Interests')
    # Previous school
    previous_school_name = models.CharField(max_length=300, blank=True, verbose_name='Previous School Name')
    previous_school_district = models.CharField(max_length=100, blank=True, verbose_name='Previous School District')
    last_class_attended = models.CharField(max_length=100, blank=True, verbose_name='Last Class Attended')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Student Profile'
        verbose_name_plural = 'Student Profiles'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        parts = [self.first_name]
        if self.other_names:
            parts.append(self.other_names)
        parts.append(self.last_name)
        return ' '.join(parts)

    @property
    def age(self):
        today = timezone.now().date()
        dob = self.date_of_birth
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    @property
    def initials(self):
        return f'{self.first_name[0]}{self.last_name[0]}'.upper() if self.first_name and self.last_name else '??'


# ============================================================================
# EMAIL VERIFICATION TOKEN (NEW v2)
# ============================================================================

class EmailVerificationToken(models.Model):
    """One-time token sent to user email for account activation."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_tokens')
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Email Verification Token'
        verbose_name_plural = 'Email Verification Tokens'

    def __str__(self):
        return f'Token for {self.user.email}'

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = uuid.uuid4().hex + uuid.uuid4().hex[:32]
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(hours=48)
        super().save(*args, **kwargs)

    @property
    def is_valid(self):
        return not self.used and timezone.now() < self.expires_at


# ============================================================================
# PASSWORD RESET TOKEN (NEW v2)
# ============================================================================

class PasswordResetToken(models.Model):
    """One-time password reset token."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Password Reset Token'
        verbose_name_plural = 'Password Reset Tokens'

    def __str__(self):
        return f'Reset token for {self.user.email}'

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = uuid.uuid4().hex + uuid.uuid4().hex[:32]
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(hours=2)
        super().save(*args, **kwargs)

    @property
    def is_valid(self):
        return not self.used and timezone.now() < self.expires_at


# ============================================================================
# APPLICATION (extended from v1)
# ============================================================================

class Application(models.Model):
    """A student's application for a specific class in a specific window."""
    window = models.ForeignKey(AdmissionWindow, on_delete=models.PROTECT, related_name='applications')
    applicant = models.ForeignKey(
        ApplicantAccount, on_delete=models.PROTECT, related_name='applications',
        verbose_name='Account Holder',
    )
    # NEW v2: link to specific student profile
    student = models.ForeignKey(
        StudentProfile, on_delete=models.PROTECT, related_name='applications',
        null=True, blank=True, verbose_name='Student',
    )
    entry_class = models.CharField(max_length=5, choices=ENTRY_CLASS_CHOICES, verbose_name='Applying for Class')
    application_number = models.CharField(max_length=20, unique=True, db_index=True, blank=True)
    status = models.CharField(max_length=30, choices=APPLICATION_STATUS_CHOICES, default='draft')
    is_transfer = models.BooleanField(default=False, verbose_name='Transfer Student')
    payment_reference = models.CharField(max_length=100, blank=True, verbose_name='Payment Reference')
    payment_verified = models.BooleanField(default=False, verbose_name='Payment Verified')
    payment_verified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_payments',
    )
    payment_verified_at = models.DateTimeField(null=True, blank=True)
    # Admin fields
    admin_notes = models.TextField(blank=True, verbose_name='Internal Admin Notes')
    rejection_reason = models.TextField(blank=True, verbose_name='Rejection Reason')
    resubmission_notes = models.TextField(blank=True, verbose_name='Resubmission Instructions')
    resubmission_deadline = models.DateTimeField(null=True, blank=True, verbose_name='Resubmission Deadline')
    # Offer letter
    offer_letter = models.FileField(
        upload_to='admissions/offer_letters/', null=True, blank=True,
        verbose_name='Offer Letter PDF',
    )
    offer_generated_at = models.DateTimeField(null=True, blank=True)
    offer_accepted_at = models.DateTimeField(null=True, blank=True, verbose_name='Offer Accepted At')
    offer_accepted_by_ip = models.GenericIPAddressField(null=True, blank=True)
    # Timestamps
    submitted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Application'
        verbose_name_plural = 'Applications'

    def __str__(self):
        return f'{self.application_number} — {self.student or self.applicant}'

    def save(self, *args, **kwargs):
        if not self.application_number:
            from .utils import generate_application_number
            self.application_number = generate_application_number(window=self.window)
        super().save(*args, **kwargs)

    @property
    def student_name(self):
        if self.student:
            return self.student.full_name
        return self.applicant.full_name

    @property
    def entry_class_label(self):
        return dict(ENTRY_CLASS_CHOICES).get(self.entry_class, self.entry_class)

    @property
    def can_edit(self):
        return self.status == 'draft'

    @property
    def can_resubmit(self):
        return self.status == 'action_required'

    @property
    def can_accept_offer(self):
        return self.status in ('approved', 'provisionally_admitted') and self.offer_letter

    @property
    def status_color(self):
        from .utils import get_status_badge
        return get_status_badge(self.status)

    @property
    def status_step(self):
        """Returns 0-based index in the STATUS_DISPLAY_PIPELINE."""
        pipeline_keys = [s[0] for s in STATUS_DISPLAY_PIPELINE]
        if self.status in ('action_required', 'docs_resubmitted'):
            return pipeline_keys.index('under_doc_review')
        try:
            return pipeline_keys.index(self.status)
        except ValueError:
            return 0

    @property
    def documents_all_approved(self):
        docs = self.documents.all()
        if not docs.exists():
            return False
        return not docs.filter(status__in=['pending', 'flagged']).exists()

    @property
    def has_flagged_documents(self):
        return self.documents.filter(status='flagged').exists()


# ============================================================================
# APPLICATION RESPONSE (from v1 — kept)
# ============================================================================

class ApplicationResponse(models.Model):
    """Stores the applicant's answer for a single FormField."""
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='responses')
    field = models.ForeignKey(FormField, on_delete=models.SET_NULL, null=True)
    field_key = models.CharField(max_length=100, verbose_name='Field Key (Snapshot)')
    text_value = models.TextField(blank=True)

    class Meta:
        unique_together = [('application', 'field')]
        verbose_name = 'Application Response'
        verbose_name_plural = 'Application Responses'

    def __str__(self):
        return f'{self.application.application_number} — {self.field_key}'


# ============================================================================
# APPLICATION DOCUMENT (replaces ApplicationFile — NEW v2)
# ============================================================================

class ApplicationDocument(models.Model):
    """
    A file uploaded for a specific DocumentSlot.
    Has per-document admin review status (pending/approved/flagged).
    """
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='documents')
    slot = models.ForeignKey(
        DocumentSlot, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Document Slot',
    )
    slot_key = models.CharField(max_length=100, verbose_name='Slot Key (Snapshot)')
    slot_name = models.CharField(max_length=200, verbose_name='Slot Name (Snapshot)')
    file = models.FileField(upload_to='admissions/documents/%Y/%m/', verbose_name='Uploaded File')
    original_name = models.CharField(max_length=255, verbose_name='Original File Name')
    file_size_kb = models.IntegerField(default=0, verbose_name='File Size (KB)')
    mime_type = models.CharField(max_length=100, blank=True, verbose_name='MIME Type')
    # Review
    status = models.CharField(max_length=20, choices=DOCUMENT_STATUS_CHOICES, default='pending')
    admin_note = models.TextField(blank=True, verbose_name='Admin Note / Feedback on this document')
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_documents',
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Application Document'
        verbose_name_plural = 'Application Documents'
        ordering = ['slot__order', 'uploaded_at']

    def __str__(self):
        return f'{self.slot_name} — {self.application.application_number}'

    @property
    def extension(self):
        name = self.original_name.lower()
        return name.split('.')[-1] if '.' in name else ''

    @property
    def is_image(self):
        return self.extension in ('jpg', 'jpeg', 'png', 'gif', 'webp')

    @property
    def is_pdf(self):
        return self.extension == 'pdf'

    @property
    def status_badge_class(self):
        mapping = {'pending': 'warning', 'approved': 'success', 'flagged': 'danger'}
        return mapping.get(self.status, 'secondary')


# ============================================================================
# APPLICATION STATUS LOG (kept from v1, extended)
# ============================================================================

class ApplicationStatusLog(models.Model):
    """Immutable audit trail of every status change."""
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='status_logs')
    from_status = models.CharField(max_length=30, blank=True)
    to_status = models.CharField(max_length=30)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    note = models.TextField(blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['changed_at']
        verbose_name = 'Status Log Entry'
        verbose_name_plural = 'Status Log'

    def __str__(self):
        return f'{self.application.application_number}: {self.from_status} → {self.to_status}'

    @property
    def to_status_display(self):
        return dict(APPLICATION_STATUS_CHOICES).get(self.to_status, self.to_status.replace('_', ' ').title())

    @property
    def to_status_color(self):
        from .utils import get_status_badge
        return get_status_badge(self.to_status)


# ============================================================================
# ADMIN FEEDBACK (NEW v2)
# ============================================================================

class AdminFeedback(models.Model):
    """
    A message from a staff member to the applicant about their application.
    Triggers automated email notification.
    """
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='feedbacks')
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_feedbacks')
    feedback_type = models.CharField(max_length=30, choices=FEEDBACK_TYPE_CHOICES, default='action_required')
    subject = models.CharField(max_length=200, verbose_name='Subject')
    message = models.TextField(verbose_name='Message to Applicant')
    is_sent = models.BooleanField(default=False, verbose_name='Email Sent')
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Admin Feedback'
        verbose_name_plural = 'Admin Feedbacks'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_feedback_type_display()} — {self.application.application_number}'


# ============================================================================
# AUDIT LOG (NEW v2)
# ============================================================================

class AuditLog(models.Model):
    """Records all staff actions for accountability and compliance."""
    staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    application = models.ForeignKey(
        Application, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='audit_logs',
    )
    action = models.CharField(max_length=200, verbose_name='Action Performed')
    details = models.TextField(blank=True, verbose_name='Additional Details')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.action} by {self.staff} at {self.timestamp:%Y-%m-%d %H:%M}'


# ============================================================================
# NOTIFICATION LOG (NEW v2)
# ============================================================================

class NotificationLog(models.Model):
    """Records every email (and SMS if enabled) sent through the portal."""
    CHANNEL_CHOICES = [('email', 'Email'), ('sms', 'SMS')]
    STATUS_CHOICES = [('sent', 'Sent'), ('failed', 'Failed'), ('queued', 'Queued')]

    application = models.ForeignKey(
        Application, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='notifications',
    )
    recipient_email = models.EmailField()
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES, default='email')
    subject = models.CharField(max_length=300)
    body_preview = models.TextField(blank=True, help_text='First 500 chars of message body')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='queued')
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Notification Log'
        verbose_name_plural = 'Notification Logs'
        ordering = ['-sent_at']

    def __str__(self):
        return f'{self.subject} → {self.recipient_email} [{self.status}]'


# ============================================================================
# TRANSFER INFO (kept from v1)
# ============================================================================

class TransferInfo(models.Model):
    """Additional information for transfer students."""
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='transfer_info')
    previous_school_name = models.CharField(max_length=200)
    previous_school_district = models.CharField(max_length=100)
    previous_school_contact = models.CharField(max_length=50, blank=True)
    headteacher_name = models.CharField(max_length=200, blank=True)
    date_last_attended = models.DateField(null=True, blank=True)
    reason_for_leaving = models.TextField()
    any_disciplinary_issues = models.BooleanField(default=False)
    disciplinary_details = models.TextField(blank=True)
    outstanding_fees = models.BooleanField(null=True, blank=True)
    verification_token = models.CharField(max_length=64, unique=True, blank=True)
    verified_by_school = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Transfer Information'
        verbose_name_plural = 'Transfer Information'

    def __str__(self):
        return f'Transfer Info — {self.application.application_number}'

    def save(self, *args, **kwargs):
        if not self.verification_token:
            self.verification_token = uuid.uuid4().hex + uuid.uuid4().hex[:32]
        super().save(*args, **kwargs)


# ============================================================================
# INTERVIEW (kept from v1)
# ============================================================================

class Interview(models.Model):
    """Interview scheduling and outcome."""
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='interviews')
    scheduled_at = models.DateTimeField()
    duration_minutes = models.IntegerField(default=30)
    location = models.CharField(max_length=200, blank=True)
    interviewer = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    outcome = models.CharField(max_length=10, choices=INTERVIEW_OUTCOME_CHOICES, default='pending')
    outcome_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-scheduled_at']
        verbose_name = 'Interview'
        verbose_name_plural = 'Interviews'

    def __str__(self):
        return f'Interview for {self.application.application_number} on {self.scheduled_at:%Y-%m-%d %H:%M}'


# ============================================================================
# LEGACY: ApplicationFile (kept for backward compat, deprecated in favor of ApplicationDocument)
# ============================================================================

class ApplicationFile(models.Model):
    """DEPRECATED: Use ApplicationDocument instead. Kept for backward compatibility."""
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='files')
    field = models.ForeignKey(FormField, on_delete=models.SET_NULL, null=True)
    field_key = models.CharField(max_length=100)
    file = models.FileField(upload_to='admissions/files/%Y/%m/')
    original_name = models.CharField(max_length=255)
    file_size_kb = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Application File (Legacy)'
        verbose_name_plural = 'Application Files (Legacy)'

    def __str__(self):
        return self.original_name
